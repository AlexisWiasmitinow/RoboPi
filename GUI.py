# coding: utf-8
from Tkinter import *
from ActorsControl import *
from threading import Thread
from PIL import Image, ImageTk
import Queue
import string
from multiprocessing import Process, Value, Queue
from espeak import espeak
espeak.set_voice("de")
espeak.synth("Hallo Welt, ich bin bereit!")
guiCommands={}
guiCommands['move']='none'
guiCommands['light']=False
guiCommands['angle']=0
guiCommands['autoServo']=False
guiCommands['autoRoll']=False
guiCommands['autoTurn']=False
guiCommands['previewRaw']=True
guiCommands['previewComputed']=False
guiCommands['runVideo']=True
guiCommands['emptyCommandQueue']=False
guiCommands['targetsize']=100
guiCommands['threshold']=100
guiCommands['rotation']=100
guiCommands['drive']=100
global GUI_Message

class Window(Frame):
	def __init__(self, master=None):
		Frame.__init__(self, master)
		self.master = master
		self.init_window()
		
	#Creation of init_window
	def init_window(self):   
			self.master.title("Roboter Bedienung")
			# allowing the widget to take the full space of the root window
			self.pack(fill=BOTH, expand=1)
			slider_Length=200
			SetRow=0
			#test=Label(self, text="First")
			#test.grid(row=0)
			self.forwardDist=StringVar()
			Entry(self,textvariable=self.forwardDist,width=4).grid(row=SetRow, column=2)
			self.forwardDist.set("1000")
			Button(self, text="Vor", command=lambda: self.moveTo("forward")).grid(row=SetRow, column=3)
			Button(self, text="Hoch", command=lambda: self.lookTo(2)).grid(row=SetRow, column=6)
			
			self.slider_target = Scale(self, orient='horizontal', from_=0, to=500, length=slider_Length, command=self.update)
			self.slider_target.grid(row=SetRow, column=7, columnspan=2)
			self.slider_target.set(50)
			self.targetLabel=Label(self, text="Ziel")
			self.targetLabel.grid(row=SetRow, column=9)
			SetRow+=1
			Button(self, text="V 300", command=lambda: self.moveTo("mf300")).grid(row=SetRow, column=3)
			SetRow+=1
			Button(self, text="V 50", command=lambda: self.moveTo("mf50")).grid(row=SetRow, column=3)
			self.slider_threshold = Scale(self, orient='horizontal', from_=0, to=500, length=slider_Length, command=self.update)
			self.slider_threshold.grid(row=SetRow, column=7, columnspan=2)
			self.slider_threshold.set(50)
			self.leftAngle=StringVar()
			Entry(self,textvariable=self.leftAngle,width=4).grid(row=SetRow, column=0)
			self.leftAngle.set("180")
			self.rightAngle=StringVar()
			Entry(self,textvariable=self.rightAngle,width=4).grid(row=SetRow, column=6)
			self.rightAngle.set("180")
			self.threshLabel=Label(self, text="Licht")
			self.threshLabel.grid(row=SetRow, column=9)
			SetRow+=1
			SetCol=0
			Button(self, text="Links", command=lambda: self.moveTo("left")).grid(row=SetRow, column=SetCol)
			SetCol+=1
			Button(self, text="L 90°", command=lambda: self.moveTo("tl90")).grid(row=SetRow, column=SetCol)
			SetCol+=1
			Button(self, text="L 10°", command=lambda: self.moveTo("tl10")).grid(row=SetRow, column=SetCol)
			SetCol+=1
			Button(self, text="Stop", command=lambda: self.moveTo("stop")).grid(row=SetRow, column=SetCol)
			SetCol+=1
			Button(self, text="R 10°", command=lambda: self.moveTo("tr10")).grid(row=SetRow, column=SetCol)
			SetCol+=1
			Button(self, text="R 90°", command=lambda: self.moveTo("tr90")).grid(row=SetRow, column=SetCol)
			SetCol+=1
			Button(self, text="Rechts", command=lambda: self.moveTo("right")).grid(row=SetRow, column=SetCol)
			
			SetRow+=1
			Button(self, text="Z 50", command=lambda: self.moveTo("mb50")).grid(row=SetRow, column=3)
			self.slider_rotation = Scale(self, orient='horizontal', from_=0, to=100, length=slider_Length, command=self.update)
			self.slider_rotation.grid(row=SetRow, column=7, columnspan=2)
			self.slider_rotation.set(30)
			self.rotationLabel=Label(self, text="Drehung")
			self.rotationLabel.grid(row=SetRow, column=9)
			SetRow+=1
			Button(self, text="Z 300", command=lambda: self.moveTo("mb300")).grid(row=SetRow, column=3)
			
			SetRow+=1
			self.lightText=StringVar()
			Button(self, textvariable=self.lightText, command=self.lightSwitch).grid(row=SetRow, column=0)
			self.lightText.set("Licht An")
			self.backwardDist=StringVar()
			Entry(self,textvariable=self.backwardDist,width=4).grid(row=SetRow, column=2)
			self.backwardDist.set("1000")
			Button(self, text="Rueckwaerz", command=lambda: self.moveTo("backward")).grid(row=SetRow, column=3)
			Button(self, text="Runter", command=lambda: self.lookTo(-2)).grid(row=SetRow, column=6)
			self.slider_drive = Scale(self, orient='horizontal', from_=0, to=100, length=slider_Length, command=self.update)
			self.slider_drive.grid(row=SetRow, column=7, columnspan=2)
			self.slider_drive.set(50)
			self.driveLabel=Label(self, text="Fahrt")
			self.driveLabel.grid(row=SetRow, column=9)
			SetRow+=1
			SetCol=0
			self.autoServoText=StringVar()
			Button(self, textvariable=self.autoServoText, command=self.autoServoSwitch).grid(row=SetRow, column=SetCol,columnspan=2)
			self.autoServoText.set("Schauen")
			SetCol+=2
			self.autoRollText=StringVar()
			Button(self, textvariable=self.autoRollText, command=self.autoRollSwitch).grid(row=SetRow, column=SetCol,columnspan=2)
			self.autoRollText.set("Rollen")
			SetCol+=2
			self.autoTurnText=StringVar()
			Button(self, textvariable=self.autoTurnText, command=self.autoTurnSwitch).grid(row=SetRow, column=SetCol,columnspan=2)
			self.autoTurnText.set("Drehen")
			SetCol+=2
			self.previewText=StringVar()
			Button(self, textvariable=self.previewText, command=self.previewSwitch).grid(row=SetRow, column=SetCol,columnspan=2)
			self.previewText.set("Vorschau")
			SetCol+=2
			#SetRow+=1
			#SetCol=0
			Button(self, text="Beenden", command=self.client_exit).grid(row=SetRow, column=SetCol,columnspan=2)
			
			
	def previewSwitch(self):
		guiCommands['previewRaw']= not guiCommands['previewRaw']
		print("preview Status",guiCommands['previewRaw'])
		if guiCommands['previewRaw']==True:
			self.previewText.set("Vorschau Aus")
			espeak.synth("Vorschau An")
		else:
			self.previewText.set("Vorschau An")
			espeak.synth("Vorschau Aus")
			
	def lightSwitch(self):
		guiCommands['light']= not guiCommands['light']
		print("light Status",guiCommands['light'])
		if guiCommands['light']==True:
			lightOn()
			self.lightText.set("Licht Aus")
			espeak.synth("Licht An")
		else:
			lightOff()
			self.lightText.set("Licht An")
			espeak.synth("Licht Aus")
	def autoServoSwitch(self):
		guiCommands['autoServo']= not guiCommands['autoServo']
		print("autoServo Status",guiCommands['autoServo'])
		if guiCommands['autoServo']==True:
			self.autoServoText.set("Schau Aus")
			espeak.synth("Schauen An")
		else:
			self.autoServoText.set("Schauen")
			espeak.synth("Schauen Aus")
			
	def autoRollSwitch(self):
		guiCommands['autoRoll']= not guiCommands['autoRoll']
		print("autoRoll Status",guiCommands['autoRoll'])
		if guiCommands['autoRoll']==True:
			self.autoRollText.set("Roll Aus")
			espeak.synth("Rollen An")
		else:
			self.autoRollText.set("Rollen")
			espeak.synth("Rollen Aus")
			guiCommands['emptyCommandQueue']=True
	def autoTurnSwitch(self):
		guiCommands['autoTurn']= not guiCommands['autoTurn']
		print("autoTurn Status",guiCommands['autoTurn'])
		if guiCommands['autoTurn']==True:
			self.autoTurnText.set("Dreh Aus")
			espeak.synth("Drehen An")
		else:
			self.autoTurnText.set("Drehen")
			espeak.synth("Drehen Aus")
			guiCommands['emptyCommandQueue']=True
	
	def lookTo(self,command):
		print("before look to: ",guiCommands['angle'])
		guiCommands['angle']+=command
		lookTo(guiCommands['angle'])
		print("look to: ",guiCommands['angle'])
		
	def moveTo(self,command):
		print("moveto function",command)
		commandNew="none"
		if command=="forward":
			#print("update function forward",command)
			inputVal=self.forwardDist.get()
			if int(inputVal)>0:
				commandNew="mf"+str(inputVal)
			else:
				commandNew="none"
		elif command=="backward":
			inputVal=self.backwardDist.get()
			if int(inputVal)>0:
				commandNew="mb"+str(inputVal)
			else:
				commandNew="none"
		elif command=="left":
			inputVal=self.leftAngle.get()
			if int(inputVal)>0:
				commandNew="tl"+str(inputVal)
			else:
				commandNew="none"
		elif command=="right":
			inputVal=self.rightAngle.get()
			if int(inputVal)>0:
				commandNew="tr"+str(inputVal)
			else:
				commandNew="none"
		elif command=="stop":
			disableMotors()
			lookTo(0)
			guiCommands['angle']=0
			guiCommands['emptyCommandQueue']=True
		else:
			commandNew=command
		print("update function command",commandNew)
		guiCommands['move']=commandNew

	def update(self,value):
		guiCommands['targetsize']=self.slider_target.get()
		guiCommands['threshold']=self.slider_threshold.get()
		guiCommands['rotation']=self.slider_rotation.get()
		guiCommands['drive']=self.slider_drive.get()
		

	def client_exit(self):
		guiCommands['runVideo']=False
		print("exit pressed")
		espeak.synth("Beenden")
		time.sleep(1)
		#SetLightTo(0)
		exit()

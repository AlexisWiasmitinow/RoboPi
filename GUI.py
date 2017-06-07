from Tkinter import *
from ActorsControl import *
from threading import Thread
from PIL import Image, ImageTk
import Queue
import string
from multiprocessing import Process, Value, Queue

guiCommands={}
guiCommands['move']='none'
guiCommands['light']=False
guiCommands['angle']=0
guiCommands['autoServo']=False
guiCommands['autoRoll']=False
guiCommands['autoTurn']=False
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
			Button(self, text="Vorwaerz", command=lambda: self.moveTo("forward")).grid(row=SetRow, column=3)
			Button(self, text="Hoch", command=lambda: self.lookTo(2)).grid(row=SetRow, column=6)
			SetRow+=1
			Button(self, text="Vorwaerz 300", command=lambda: self.moveTo("mf300")).grid(row=SetRow, column=3)
			SetRow+=1
			Button(self, text="Vorwaerz 50", command=lambda: self.moveTo("mf50")).grid(row=SetRow, column=3)
			self.leftAngle=StringVar()
			Entry(self,textvariable=self.leftAngle,width=4).grid(row=SetRow, column=0)
			self.leftAngle.set("180")
			self.rightAngle=StringVar()
			Entry(self,textvariable=self.rightAngle,width=4).grid(row=SetRow, column=6)
			self.rightAngle.set("180")
			SetRow+=1
			SetCol=0
			Button(self, text="Links", command=lambda: self.moveTo("left")).grid(row=SetRow, column=SetCol)
			SetCol+=1
			Button(self, text="Links 90", command=lambda: self.moveTo("tl90")).grid(row=SetRow, column=SetCol)
			SetCol+=1
			Button(self, text="Links 10", command=lambda: self.moveTo("tl10")).grid(row=SetRow, column=SetCol)
			SetCol+=1
			Button(self, text="Stop", command=lambda: self.moveTo("stop")).grid(row=SetRow, column=SetCol)
			SetCol+=1
			Button(self, text="Rechts 10", command=lambda: self.moveTo("tr10")).grid(row=SetRow, column=SetCol)
			SetCol+=1
			Button(self, text="Rechts 90", command=lambda: self.moveTo("tr90")).grid(row=SetRow, column=SetCol)
			SetCol+=1
			Button(self, text="Rechts", command=lambda: self.moveTo("right")).grid(row=SetRow, column=SetCol)
			SetRow+=1
			Button(self, text="Rueckwaerz 50", command=lambda: self.moveTo("mb50")).grid(row=SetRow, column=3)
			SetRow+=1
			Button(self, text="Rueckwaerz 300", command=lambda: self.moveTo("mb300")).grid(row=SetRow, column=3)
			SetRow+=1
			self.lightText=StringVar()
			Button(self, textvariable=self.lightText, command=self.lightSwitch).grid(row=SetRow, column=0)
			self.lightText.set("Licht An")
			self.backwardDist=StringVar()
			Entry(self,textvariable=self.backwardDist,width=4).grid(row=SetRow, column=2)
			self.backwardDist.set("1000")
			Button(self, text="Rueckwaerz", command=lambda: self.moveTo("backward")).grid(row=SetRow, column=3)
			Button(self, text="Runter", command=lambda: self.lookTo(-2)).grid(row=SetRow, column=6)
			SetRow+=1
			SetCol=0
			self.autoServoText=StringVar()
			Button(self, textvariable=self.autoServoText, command=self.autoServoSwitch).grid(row=SetRow, column=SetCol,columnspan=2)
			self.autoServoText.set("Schauen")
			SetCol+=1
			self.autoRollText=StringVar()
			Button(self, textvariable=self.autoRollText, command=self.autoRollSwitch).grid(row=SetRow, column=SetCol,columnspan=2)
			self.autoRollText.set("Rollen")
			SetCol+=1
			self.autoTurnText=StringVar()
			Button(self, textvariable=self.autoTurnText, command=self.autoTurnSwitch).grid(row=SetRow, column=SetCol,columnspan=2)
			self.autoTurnText.set("Drehen")
			
	def lightSwitch(self):
		guiCommands['light']= not guiCommands['light']
		print("light Status",guiCommands['light'])
		if guiCommands['light']==True:
			lightOn()
			self.lightText.set("Licht Aus")
		else:
			lightOff()
			self.lightText.set("Licht An")
	def autoServoSwitch(self):
		guiCommands['autoServo']= not guiCommands['autoServo']
		print("autoServo Status",guiCommands['autoServo'])
		if guiCommands['autoServo']==True:
			self.autoServoText.set("Schauen Aus")
		else:
			self.autoServoText.set("Schauen")
	def autoRollSwitch(self):
		guiCommands['autoRoll']= not guiCommands['autoRoll']
		print("autoRoll Status",guiCommands['autoRoll'])
		if guiCommands['autoRoll']==True:
			self.autoRollText.set("Rollen Aus")
		else:
			self.autoRollText.set("Rollen")
	def autoTurnSwitch(self):
		guiCommands['autoTurn']= not guiCommands['autoTurn']
		print("autoTurn Status",guiCommands['autoTurn'])
		if guiCommands['autoTurn']==True:
			self.autoTurnText.set("Drehen Aus")
		else:
			self.autoTurnText.set("Drehen")
	
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
		else:
			commandNew=command
		print("update function command",commandNew)
		guiCommands['move']=commandNew


	def client_exit(self):
		print("exit pressed")
		#SetLightTo(0)
		GeneralSettings['RunVideo']=False
		airBlastOn()
		vibratorOff()
		#time.sleep(int(GeneralSettings['FlushTime']))
		motorOff()
		stepperVars['runMotor']=False
		self.t_motor.terminate()
		allOff()
		exit()

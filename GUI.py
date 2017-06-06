from Tkinter import *
from ActorsControl import *
from threading import Thread
from PIL import Image, ImageTk
import Queue
import string
from multiprocessing import Process, Value, Queue

Translations={}
guiCommands={}
guiCommands['move']='none'
guiCommands['light']=False
guiCommands['angle']=0
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
			Button(self, text="Hoch", command=lambda: self.lookTo(5)).grid(row=SetRow, column=6)
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
			Button(self, text="Licht", command=self.lightSwitch).grid(row=SetRow, column=0)
			self.backwardDist=StringVar()
			Entry(self,textvariable=self.backwardDist,width=4).grid(row=SetRow, column=2)
			self.backwardDist.set("1000")
			Button(self, text="Rueckwaerz", command=lambda: self.moveTo("backward")).grid(row=SetRow, column=3)
			Button(self, text="Runter", command=lambda: self.lookTo(-5)).grid(row=SetRow, column=6)
			
			
	def lightSwitch(self):
		guiCommands['light']= not guiCommands['light']
		print("light Status",guiCommands['light'])
		if guiCommands['light']==True:
			lightOn()
		else:
			lightOff()
	
	def lookTo(self,command):
		guiCommands['angle']+=command
		lookTo(guiCommands['angle'])
		
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
		else:
			commandNew=command
		print("update function command",commandNew)
		guiCommands['move']=commandNew
	
	def update(self,value):
		print("update function",value)
		#setMotorSpeed(self.slider_mot.get())
		self.MotorSpeedQueue.put(self.slider_mot.get())
		GeneralSettings['MotorSpeed']=self.slider_mot.get()
		GeneralSettings['FlushTime']=self.slider_flush.get()
		guiParams['ShutterSpeed']=self.slider_par4.get()
		guiParams['ImageThreshold']=self.slider_par6.get()
		guiParams['zoom_x1']=self.slider_par7.get()
		guiParams['zoom_x2']=self.slider_par8.get()
		guiParams['zoom_y1']=self.slider_par9.get()
		guiParams['zoom_y2']=self.slider_par10.get()
		guiParams['BoxMax'][0]=float(self.BoxMaxL.get())
		guiParams['BoxMax'][1]=float(self.BoxMaxW.get())
		guiParams['BoxMin'][0]=float(self.BoxMinL.get())
		guiParams['BoxMin'][1]=float(self.BoxMinW.get())
		GeneralSettings['takePicDelay']=self.slider_takePicDelay.get()/1000.0
		GeneralSettings['airBlastDelay']=self.slider_airBlastDelay.get()/1000.0
		emptyBoxIndex=0
		for i in range(0, len(guiParams['EmptyBoxes'])):
			guiParams['EmptyBoxes'][i][0]=float(self.emptyBoxValues[emptyBoxIndex].get())
			emptyBoxIndex+=1
			guiParams['EmptyBoxes'][i][1]=float(self.emptyBoxValues[emptyBoxIndex].get())
			emptyBoxIndex+=1
			guiParams['EmptyBoxes'][i][2]=float(self.emptyBoxValues[emptyBoxIndex].get())
			emptyBoxIndex+=1
			guiParams['EmptyBoxes'][i][3]=float(self.emptyBoxValues[emptyBoxIndex].get())
			emptyBoxIndex+=1
		
		GeneralSettings['SavePics']=self.savePicsOptions[self.savePicsOptionsTranslated.index(self.pulldown_save_pics.get())]
		#print("SavePicsGenSet: ",GeneralSettings['SavePics'])
		guiParams['contour_to_find']=int(self.pulldown_contour.get())*1
		
	def changePreview(self,value):
		GeneralSettings['ShowPreview']=self.previewOptions[self.previewOptionsTranslated.index(self.pulldown_preview.get())]
		if GeneralSettings['ShowPreview']=="Standing Setup":
			motorOff()
			vibratorOff()
			airBlastOff()
		else:
			#print("now gui")
			motorOn()
			vibratorOn()
	
	

	def save_settings(self, to_save="all"):
		self.update(None)
		f = open(str(GeneralSettings['InstallPath'])+'settings.txt', 'r')
		self.readLines=f.readlines()
		f.close()
		f = open(str(GeneralSettings['InstallPath'])+'settings.txt', 'w')
		writeDict=guiParams.copy()
		#print("to_save: ",to_save)
		GeneralSettingsSave=GeneralSettings.copy()
		#GeneralSettingsSave={}
		#for k,v in GeneralSettings.items():
		#	GeneralSettingsSave[k]=v
		del GeneralSettingsSave['StatusMessage']
		del GeneralSettingsSave['RunVideo']
		del GeneralSettingsSave['TranslationNo']
		GeneralSettingsSave['SelectedType']=self.TypeChangedTo
		#f = open('test.txt', 'w')
		#print("readlines",self.readLines )
		if to_save == "general" :
			#print("general save")
			f.write(str(GeneralSettingsSave)+"\n")
			for i in range(1,len(self.readLines)) :
				f.write(self.readLines[i])
		else :
			#print("all save")
			f.write(str(GeneralSettingsSave)+"\n")
			for i in range(0,GeneralSettings['TotalTypes']):
				if i == GeneralSettings['SelectedType']-1:
					f.write(str(writeDict)+"\n")
					#print("save dict line "+str(i)+" selected: "+str(GeneralSettings['SelectedType'])+" write "+str(writeDict))
				else: 
					f.write(self.readLines[i+1])
		#f.write(str(guiParams)+"\n")
		f.close()
		load_settings(GeneralSettings['SelectedType'])

	def set_fields_values(self):
		
		#guiParams['EmptyBoxes']=readDict['EmptyBoxes']
		#print("EmptyBoxes: ",readDict['EmptyBoxes'][0][0])
		GeneralSettings['TranslationNo']=self.availableTranslations.index(GeneralSettings['SetLanguage'])
		
		#print("Translation :",Translations['Image Recognition Control'][GeneralSettings['TranslationNo']])
		self.master.title(Translations['Image Recognition Control'][GeneralSettings['TranslationNo']])
		self.shutterLabel.config(text=Translations['Shutter Speed (ns)'][GeneralSettings['TranslationNo']])
		#self.flushLabel.config(text=Translations['Light Brightness'][GeneralSettings['TranslationNo']])
		#self.objectThresholdLabel.config(text=Translations['Object Threshold'][GeneralSettings['TranslationNo']])
		self.imageThresholdLabel.config(text=Translations['Image Threshold'][GeneralSettings['TranslationNo']])
		self.partTypeLabel.config(text=Translations['Part Type'][GeneralSettings['TranslationNo']])
		self.savePicsLabel.config(text=Translations['Save Pictures'][GeneralSettings['TranslationNo']])
		self.EmptyBoxExplainLabel.config(text=Translations['Coordinates of Boxes to be empty, relative to Boundary L and W'][GeneralSettings['TranslationNo']])
		#entry=self.pulldownSavepics.children['menu']
		#print entry
		#self.pulldownSavepics['menu'].delete(0, len(self.savePicsOptions))
		#for i in range(0,len(self.savePicsOptions)):
		#	entry.entryconfig(i,label=Translations[self.savePicsOptions[i]][GeneralSettings['TranslationNo']])
			#self.savePicsOptions[i]=Translations[self.savePicsOptions[i]][GeneralSettings['TranslationNo']]
			#self.pulldownSavepics['menu'].add_command(label=Translations[self.savePicsOptions[i]][GeneralSettings['TranslationNo']])
		#	print("savePicsOptions: ",Translations[self.savePicsOptions[i]][GeneralSettings['TranslationNo']])
		
	
	
	def readCommands(self):
		if GeneralSettings['master']=="remote" :
			f = open('commands.txt', 'r')
			changedSettings=False
			readLine=f.readline()
			f.close()
			GeneralSettingsRead=eval(readLine)
			for k,v in GeneralSettingsRead.items():
				if GeneralSettings[k] != v:
					#print("change!")
					changedSettings=True
					GeneralSettings[k]=v
			if changedSettings==True :
				self.writeStatus()
				self.pulldown_parttype.set(GeneralSettings['SelectedType'])
				self.load_settings()
				#print("updated settings: ",GeneralSettings)
				self.update(None)
	

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

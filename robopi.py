#!/usr/bin/env python
from pinConfigurations import *
from ActorsControl import *
import time
from pivideostream import PiVideoStream
import cv2
from Tkinter import *
from threading import Thread
import time, multiprocessing, sys, getopt
import numpy as np
from GUI import *
from espeak import espeak
espeak.set_voice("de")


vs = PiVideoStream((1296,736)).start()
time.sleep(1)
ActorsQueue=multiprocessing.Queue(3)
t_actors=multiprocessing.Process(target=controlActors, args=(ActorsQueue,))
t_actors.start()
#ActorsQueue.put("mf200")
time.sleep(3)
vs.SetParam()
lookTo(0)
#ActorsQueue.put("mb200")

def guiThread():
	root = Tk()
	root.geometry("800x270+0+0")
	app = Window(root)
	root.mainloop()

t_gui=Thread(target=guiThread)
t_gui.start()
runVideo=True
#for i in range(0,10):
lastSpeak="bla"
while (runVideo==True):
	runVideo=guiCommands['runVideo']
	scale_factor=0.5
	#print("frame")
	#frame = vs.readCropped(0,0,0,0)
	frame = vs.read()
	imageHeight,imageWidth=frame.shape[:2]
	frame_small=cv2.resize(frame,(int(imageWidth*scale_factor),int(imageHeight*scale_factor)),interpolation = cv2.INTER_AREA)
	#grayImage = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
	b,g,r=cv2.split(frame_small)
	grayImage=r
	imageHeight,imageWidth=grayImage.shape[:2]
	#red=frame[0,0,100]
	#cv2.imshow('Test',frame)
	#imageHeight,imageWidth=frame_small.shape[:2]
	#b,g,r=cv2.split(frame_small)
	#r=r-b-g
	if imageWidth>0:
		#print("guiCommands['previewRaw'] 2 ",guiCommands['previewRaw'])
		ret, thresh = cv2.threshold(grayImage,guiCommands['threshold'],255,0)
		
		(cnts, _) = cv2.findContours(thresh, cv2.RETR_EXTERNAL, 2)
		cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
		if  guiCommands['previewRaw']==True:
			cv2.namedWindow('Vorschau',cv2.WINDOW_NORMAL)
			cv2.resizeWindow('Vorschau',500,150)
			cv2.moveWindow('Vorschau',0,300)
		"""	
		if guiCommands['emptyCommandQueue']==True:
			guiCommands['emptyCommandQueue']=False
			ActorsQueue.clear()
		"""
		if len(cnts)>0:
			mainContour=cnts[0]
			box = cv2.minAreaRect(mainContour)
			hOffset=box[0][0]-imageWidth/2
			vOffset=imageHeight/2-box[0][1]
			boxWidth=box[1][1]
			boxHeight=box[1][0]
			boxMax=max(boxWidth,boxHeight)
			sizeOffset=guiCommands['targetsize']-boxMax
			#print("guiCommands['previewRaw'] ",guiCommands['previewRaw'])
			if guiCommands['previewRaw']==True:
				#print("preview")
				cv2.imshow('Vorschau',thresh)
				boxPoints = cv2.cv.BoxPoints(box)
				boxPoints = np.array(boxPoints, dtype="int")
				cv2.drawContours(frame_small, mainContour, -1, (255, 0, 0), 2)
				if sizeOffset>0:
					cv2.drawContours(frame_small, [boxPoints], -1, ( 255,255, 0), 2)
				else:
					cv2.drawContours(frame_small, [boxPoints], -1, ( 255, 0,255), 2)
				cv2.putText(frame_small," Box Dimensions W: "+str(box[0][0])+" H: "+str(box[0][1])+" Horiz: "+str(hOffset)+" Vert: "+str(vOffset)+" width: "+str(boxWidth),(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.45, (0, 0, 255), 2)
				#cv2.imshow('Computed',frame)
				cv2.imshow('Vorschau',frame_small)
			else:
				cv2.destroyAllWindows()
			proportionality=0.001*guiCommands['rotation']
		
			if hOffset>0:
				moveCommand="tr"+str(int(abs(hOffset*proportionality)))
				#espeak.synth("Rechts")
				Speak="rechts"
			elif hOffset<0:
				moveCommand="tl"+str(int(abs(hOffset*proportionality)))
				#espeak.synth("Links")
				Speak="links"
			else:
				moveCommand="none"
			if moveCommand!='none' and int(moveCommand[2:])>0 and guiCommands['autoTurn']==True:
				print("moveCommand turn: ",moveCommand)
				if Speak != lastSpeak:
					espeak.synth(Speak)
				lastSpeak=Speak
				ActorsQueue.put(moveCommand)
			if guiCommands['autoServo']==True:
				guiCommands['angle']+=vOffset*proportionality*0.1
				print("auto look to: ",guiCommands['angle'])
				lookTo(guiCommands['angle'])
			
			
			#distance measurement
			proportionality2=0.02*guiCommands['drive']
			if sizeOffset<0:
				moveCommand="mb"+str(int(abs(sizeOffset*proportionality2)))
				Speak="weg"
			else:
				moveCommand="mf"+str(int(abs(sizeOffset*proportionality2)))
				Speak="hin"
			if moveCommand!='none' and int(moveCommand[2:])>0 and guiCommands['autoRoll']==True:
				print("moveCommand roll: ",moveCommand)
				if Speak != lastSpeak:
					espeak.synth(Speak)
				lastSpeak=Speak
				ActorsQueue.put(moveCommand)
		elif  guiCommands['previewRaw']==True:
			cv2.imshow('Vorschau',frame_small)
			#cv2.imshow('Raw',frame_small)
			#cv2.imshow('Thresh',thresh)
		else:
			cv2.destroyAllWindows()
	"""
	if ActorsQueue.qsize()>5:		
		time.sleep(2)
	else:
		time.sleep(0.2)
	"""
	#print("shape: ",frame.shape)
	#print("move: ",guiCommands['move'])
	if guiCommands['move']!='none':
		ActorsQueue.put(guiCommands['move'])
		guiCommands['move']='none'
	if cv2.waitKey(1) & 0xFF == ord('q'):
		runVideo=False
		break
	time.sleep(0.1)

lightOff()
servoOff()
disableMotors()
ActorsQueue.put("quit")
vs.stop()
cv2.destroyAllWindows()
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

vs = PiVideoStream((1296,736)).start()
time.sleep(1)
ActorsQueue=multiprocessing.Queue()
t_actors=multiprocessing.Process(target=controlActors, args=(ActorsQueue,))
t_actors.start()
#ActorsQueue.put("mf200")
time.sleep(3)
vs.SetParam()
lookTo(0)
#ActorsQueue.put("mb200")

def guiThread():
	root = Tk()
	root.geometry("600x300+0+0")
	app = Window(root)
	root.mainloop()

t_gui=Thread(target=guiThread)
t_gui.start()
runVideo=True
#for i in range(0,10):
while (runVideo==True):
	runVideo=guiCommands['runVideo']
	scale_factor=0.5
	#print("frame")
	#frame = vs.readCropped(0,0,0,0)
	frame = vs.read()
	grayImage = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	imageHeight,imageWidth=grayImage.shape[:2]
	frame_small=cv2.resize(grayImage,(int(imageWidth*scale_factor),int(imageHeight*scale_factor)),interpolation = cv2.INTER_AREA)
	#red=frame[0,0,100]
	#cv2.imshow('Test',frame)
	imageHeight,imageWidth=frame_small.shape[:2]
	#b,g,r=cv2.split(frame_small)
	#r=r-b-g
	if imageWidth>0:
		#print("guiCommands['previewRaw'] 2 ",guiCommands['previewRaw'])
		ret, thresh = cv2.threshold(frame_small,100,255,0)
		
		(cnts, _) = cv2.findContours(thresh, cv2.RETR_EXTERNAL, 2)
		cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
		if len(cnts)>0:
			mainContour=cnts[0]
			box = cv2.minAreaRect(mainContour)
			hOffset=box[0][0]-imageWidth/2
			vOffset=imageHeight/2-box[0][1]
			boxWidth=box[1][0]
			#print("guiCommands['previewRaw'] ",guiCommands['previewRaw'])
			if guiCommands['previewRaw']==True:
				print("preview")
				cv2.imshow('Thresh',thresh)
				boxPoints = cv2.cv.BoxPoints(box)
				boxPoints = np.array(boxPoints, dtype="int")
				cv2.drawContours(frame, mainContour, -1, (255, 0, 0), 2)
				cv2.drawContours(frame, [boxPoints], -1, ( 0,255, 0), 2)
				cv2.putText(frame," Box Dimensions W: "+str(box[0][0])+" H: "+str(box[0][1])+" Horiz: "+str(hOffset)+" Vert: "+str(vOffset)+" width: "+str(boxWidth),(10,30),cv2.FONT_HERSHEY_SIMPLEX,0.45, (0, 0, 255), 2)
				cv2.imshow('Computed',frame)
			else:
				cv2.destroyAllWindows()
			proportionality=0.05
			if hOffset>0:
				moveCommand="tr"+str(int(abs(hOffset*proportionality)))
			elif hOffset<0:
				moveCommand="tl"+str(int(abs(hOffset*proportionality)))
			else:
				moveCommand="none"
			if moveCommand!='none' and int(moveCommand[2:])>0 and guiCommands['autoTurn']==True:
				print("moveCommand turn: ",moveCommand)
				ActorsQueue.put(moveCommand)
			if guiCommands['autoServo']==True:
				guiCommands['angle']+=vOffset*proportionality
				print("auto look to: ",guiCommands['angle'])
				lookTo(guiCommands['angle'])
			targetWidth=100
			sizeOffset=targetWidth-boxWidth
			#distance measurement
			proportionality2=0.5
			if sizeOffset<0:
				moveCommand="mb"+str(int(abs(sizeOffset*proportionality2)))
			else:
				moveCommand="mf"+str(int(abs(sizeOffset*proportionality2)))
			if moveCommand!='none' and int(moveCommand[2:])>0 and guiCommands['autoRoll']==True:
				print("moveCommand roll: ",moveCommand)
				ActorsQueue.put(moveCommand)
		elif  guiCommands['previewRaw']==True:
			cv2.imshow('Raw',frame_small)
			#cv2.imshow('Thresh',thresh)
		else:
			cv2.destroyAllWindows()
	#time.sleep(0.02)
	#print("shape: ",frame.shape)
	#print("move: ",guiCommands['move'])
	if guiCommands['move']!='none':
		ActorsQueue.put(guiCommands['move'])
		guiCommands['move']='none'
	if cv2.waitKey(1) & 0xFF == ord('q'):
		runVideo=False
		break

lightOff()
servoOff()
disableMotors()
ActorsQueue.put("quit")
vs.stop()
cv2.destroyAllWindows()
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
#time.sleep(1)
#ActorsQueue.put("mb200")

def guiThread():
	root = Tk()
	root.geometry("600x400+50+50")
	app = Window(root)
	root.mainloop()

t_gui=Thread(target=guiThread)
t_gui.start()
runVideo=True
#for i in range(0,10):
while (runVideo==True):
	#print("frame")
	#frame = vs.readCropped(0,0,0,0)
	frame = vs.read()
	#red=frame[0,0,100]
	#cv2.imshow('Test',frame)
	b,g,r=cv2.split(frame)
	ret, thresh = cv2.threshold(r,30,255,0)
	cv2.imshow('Red',r)
	cv2.imshow('Thresh',thresh)
	time.sleep(0.02)
	#print("shape: ",frame.shape)
	#print("move: ",guiCommands['move'])
	if guiCommands['move']!='none':
		ActorsQueue.put(guiCommands['move'])
		guiCommands['move']='none'
	if cv2.waitKey(1) & 0xFF == ord('q'):
		runVideo=False
		break

lightOff()
ActorsQueue.put("quit")
vs.stop()
cv2.destroyAllWindows()
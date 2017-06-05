#!/usr/bin/env python
from pinConfigurations import *
from ActorsControl import *
import time
from pivideostream import PiVideoStream
import cv2
#import Adafruit_PCA9685
#pwm = Adafruit_PCA9685.PCA9685()
#pwm.set_pwm_freq(60)


#pwm.set_pwm(0, 0, servo_max)

#lightOn()
#lookTo(-30)
#time.sleep(2)
lookTo(-20)
time.sleep(2)
#lookTo(30)
time.sleep(1)
servoOff()

#time.sleep(1)
lightOff()
"""
squareWidth=400
rotateAngle=90
moveTo(200,squareWidth)
rotateTo(1,rotateAngle)
moveTo(200,squareWidth)
rotateTo(1,rotateAngle)
moveTo(200,squareWidth)
rotateTo(1,rotateAngle)
moveTo(200,squareWidth)
rotateTo(1,rotateAngle)
"""
lightOn()
#rotateTo(1,-90)
#moveTo(200,-200)
#rotateTo(1,-45)
#moveTo(200,1300)
lightOff()
vs = PiVideoStream((1296,736)).start()
time.sleep(1)
#for i in range(0,1):
while (1):
	#print("frame")
	#frame = vs.readCropped(0,0,0,0)
	frame = vs.read()
	cv2.imshow('Test',frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
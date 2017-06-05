import os
import time
import RPi.GPIO as GPIO
from pinConfigurations import *
import Adafruit_PCA9685
import math
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 
GPIO.setup(lightPin,GPIO.OUT)
GPIO.output(lightPin, 0)

GPIO.setup(dirRightMotorPin,GPIO.OUT)
GPIO.setup(dirLeftMotorPin,GPIO.OUT)
GPIO.setup(stepRightMotorPin,GPIO.OUT)
GPIO.setup(stepLeftMotorPin,GPIO.OUT)

GPIO.setup(enableRightMotorPin,GPIO.OUT)
GPIO.setup(enableLeftMotorPin,GPIO.OUT)
GPIO.output(enableRightMotorPin, 1)
GPIO.output(enableLeftMotorPin, 1)


GPIO.setup(servoEnablePin,GPIO.OUT)
GPIO.output(servoEnablePin, 1)

debugActors=False
debugActors2=True

def DeleteImages(ControlImagePath):
	#os.system("rm control_images/turn_* 2> /dev/null 1> /dev/null")
	#os.system("rm control_images/image_* 2> /dev/null 1> /dev/null")
	#os.system("rm control_images/*/* 2> /dev/null 1> /dev/null")
	os.system("mkdir -p  "+str(ControlImagePath)+"logs 2> /dev/null 1> /dev/null")
	os.system("mkdir -p  "+str(ControlImagePath)+"good 2> /dev/null 1> /dev/null")
	os.system("mkdir -p  "+str(ControlImagePath)+"bad_orient 2> /dev/null 1> /dev/null")
	os.system("mkdir -p  "+str(ControlImagePath)+"bad_size 2> /dev/null 1> /dev/null")
	deletecommand="rm "+str(ControlImagePath)+"*/* 2> /dev/null 1> /dev/null"
	#print("deletecommand:",deletecommand)
	os.system(deletecommand)
	deletecommand2="rm "+str(ControlImagePath)+"logs/* 2> /dev/null 1> /dev/null"
	#print("deletecommand:",deletecommand)
	os.system(deletecommand2)
	#os.system("rm "+str(ControlImagePath)+"*/* 2> /dev/null 1> /dev/null")
	#os.system("rm control_images/flip/image_* 2> /dev/null 1> /dev/null")
	#os.system("rm control_images/bad_size/image_* 2> /dev/null 1> /dev/null")
	#os.system("rm control_images/bad_orient/image_* 2> /dev/null 1> /dev/null")
	
def lookTo(value):
	pwm.set_pwm(0, 0, value)
	if debugActors==True: print("look to",value)
	
def servoOff():
	pwm.set_pwm(0,0,0)
	
def lightOn():
	GPIO.output(lightPin, 1)

def lightOff():
	GPIO.output(lightPin, 0)

def moveTo(speed,distance):
	speed=speed*10
	if debugActors2==True: print("distance:",distance)
	if debugActors2==True: print("speed:",speed)
	GPIO.output(enableRightMotorPin, 0)
	GPIO.output(enableLeftMotorPin, 0)
	stepsToGo=int(abs(distance)*stepsPerTurn*microsteps/wheelCircumference)
	if 1*distance>0:
		if debugActors2==True: print("forward:")
		GPIO.output(dirLeftMotorPin, 0)
		GPIO.output(dirRightMotorPin, 1)
	else:
		if debugActors2==True: print("backward:")
		GPIO.output(dirLeftMotorPin, 1)
		GPIO.output(dirRightMotorPin, 0)
	stepsPerSecond=speed*stepsPerTurn*microsteps/wheelCircumference*0.1
	delay=1.0/stepsPerSecond
	if debugActors2==True: print("delay:",delay)
	for i in range(0,stepsToGo):
		if debugActors==True: print("step, delay:",delay)
		GPIO.output(stepLeftMotorPin, 1)
		GPIO.output(stepRightMotorPin, 1)
		time.sleep(delay)
		GPIO.output(stepLeftMotorPin, 0)
		GPIO.output(stepRightMotorPin, 0)
		time.sleep(delay)
	time.sleep(delay*10)
	GPIO.output(enableRightMotorPin, 1)
	GPIO.output(enableLeftMotorPin, 1)

def rotateTo(speed,angle):
	if debugActors2==True: print("angle:",angle)
	if debugActors2==True: print("speed:",speed)
	trackCircleCircumference=math.pi*trackWidth*1.0
	stepsToGo=int(abs(trackCircleCircumference*(angle*1.0/360)*stepsPerTurn*microsteps/wheelCircumference))
	if debugActors2==True: print("steps:",stepsToGo)
	stepsPerSecond=stepsToGo/speed
	if debugActors2==True: print("steps:",stepsPerSecond)
	delay=1.0/stepsPerSecond
	
	if debugActors2==True: print("delay:",delay)
	GPIO.output(enableRightMotorPin, 0)
	GPIO.output(enableLeftMotorPin, 0)
	if angle>0:
		GPIO.output(dirLeftMotorPin, 1)
		GPIO.output(dirRightMotorPin, 1)
	else:
		GPIO.output(dirLeftMotorPin, 0)
		GPIO.output(dirRightMotorPin, 0)
	
	for i in range(0,stepsToGo):
			if debugActors==True: print("step, delay:",delay)
			GPIO.output(stepLeftMotorPin, 1)
			GPIO.output(stepRightMotorPin, 1)
			time.sleep(delay)
			GPIO.output(stepLeftMotorPin, 0)
			GPIO.output(stepRightMotorPin, 0)
			time.sleep(delay)
	time.sleep(delay*10)
	GPIO.output(enableRightMotorPin, 1)
	GPIO.output(enableLeftMotorPin, 1)
	
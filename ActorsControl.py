import os
import time
import RPi.GPIO as GPIO
from pinConfigurations import *
import Adafruit_PCA9685
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 
GPIO.setup(airBlastPin,GPIO.OUT)
GPIO.output(airBlastPin, 0)
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
	if debugActors2==True: print("distance:",distance)
	GPIO.output(enableRightMotorPin, 0)
	GPIO.output(enableLeftMotorPin, 0)

	stepsPerTurn=200
	circumference=200
	microsteps=1
	if 1*distance>0:
		if debugActors2==True: print("forward:")
		GPIO.output(dirLeftMotorPin, 0)
		GPIO.output(dirRightMotorPin, 1)
	else:
		if debugActors2==True: print("backward:")
		GPIO.output(dirLeftMotorPin, 1)
		GPIO.output(dirRightMotorPin, 0)
	stepsPerSecond=speed*stepsPerTurn*microsteps/circumference*0.1
	delay=1.0/stepsPerSecond
	for i in range(0,abs(distance)):
		if debugActors2==True: print("step, delay:",delay)
		GPIO.output(stepLeftMotorPin, 1)
		GPIO.output(stepRightMotorPin, 1)
		time.sleep(delay)
		GPIO.output(stepLeftMotorPin, 0)
		GPIO.output(stepRightMotorPin, 0)
		
	GPIO.output(enableRightMotorPin, 1)
	GPIO.output(enableLeftMotorPin, 1)

	
	

def motorDirection(direction):
	if direction=="forward":
		GPIO.output(dirBeltMotorPin, 0)
	else:
		GPIO.output(dirBeltMotorPin, 1)
		
def motorOn():
	GPIO.output(enableBeltMotorPin, 0)
	
def motorOff():
	GPIO.output(enableBeltMotorPin, 1)
	
def flushBeltStart(previewSetting):
	#print("flush start")
	if previewSetting == "Standing Setup":
		vibratorOff()
		motorOff()
		airBlastOff()
	else:
		#vibratorOff()
		motorOn()
		airBlastOn()
		
	
def flushBeltStop(previewSetting):
	#print("flush stop")
	if previewSetting != "Standing Setup":
		vibratorOn()
		motorOn()
	airBlastOff()

def allOff():
	vibratorOff()
	motorOff()
	airBlastOff()

	
	
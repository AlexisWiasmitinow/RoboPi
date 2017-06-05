import os
import RPi.GPIO as GPIO
from pinConfigurations import *
import Adafruit_PCA9685
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(60)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 
GPIO.setup(airBlastPin,GPIO.OUT)
GPIO.output(airBlastPin, 0)
GPIO.setup(vibratorPin,GPIO.OUT)
GPIO.output(vibratorPin, 0)

GPIO.setup(enableBeltMotorPin,GPIO.OUT)
GPIO.output(enableBeltMotorPin, 1)
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
	pwm.set_pwm_freq(0)
	

	
def vibratorOn():
	if debugActors==True: print("vibrator on")
	GPIO.output(vibratorPin, 1)
	
def vibratorOff():
	if debugActors==True: print("vibrator off")
	GPIO.output(vibratorPin, 0)
	
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

	
	
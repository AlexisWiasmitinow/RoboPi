#!/usr/bin/env python
# Import required libraries
import sys
import time
import RPi.GPIO as GPIO
import time
import getopt

# Use BCM GPIO references
# instead of physical pin numbers
def usage():
	print("usage: -s speed <RPM> -t <turns> -d direction <l/r>")

def main():
	try: 
		opts, args =getopt.getopt(sys.argv[1:], "s:t:d:",["speed=","turns=","direction="])
	except getopt.GetoptError as err:
		usage()
		sys.exit(2)
	#print("opts: ",opts)
	#print("args: ",sys.argv[1:])
	if len(opts)<3:
		usage()
		sys.exit(2)
	for o,a, in opts:
		if o=="-s":
			speed=float(a)
		elif o=="-t":
			turns=float(a)
		elif o=="-d":
			direction=a
			

	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	motor=2
	#2 is good
	stepPin=13
	dirPin=16
	enablePin=12
	stepPin2=5
	dirPin2=6
	enablePin2=4
	
	sleepTimeStep=0.0001
	microsteps=1
	#turns=1 #turns
	stepsPerTurn=200
	#pulsesToGo=100
	#resolution=(1920, 1088)
	
	GPIO.setup(stepPin,GPIO.OUT)
	GPIO.output(stepPin, False)
	GPIO.setup(dirPin,GPIO.OUT)
	GPIO.output(dirPin, True)
	GPIO.setup(enablePin,GPIO.OUT)
	GPIO.output(enablePin, False)
	GPIO.setup(stepPin2,GPIO.OUT)
	GPIO.output(stepPin2, False)
	GPIO.setup(dirPin2,GPIO.OUT)
	GPIO.output(dirPin2, True)
	GPIO.setup(enablePin2,GPIO.OUT)
	GPIO.output(enablePin2, False)
	
	
	print("speed RPM: ", speed)
	speedHz=speed/60
	print("speed Hz: ", speedHz) 
	sleepTimeStep=1.0/(microsteps*stepsPerTurn*speedHz)
	print("Delay: ", sleepTimeStep)
	if direction=="r":
		GPIO.output(dirPin, True)
		GPIO.output(dirPin2, True)
	elif direction=="l":
		GPIO.output(dirPin, False)
		GPIO.output(dirPin2, False)
	else:
		print("direction not clear, please enter l or r")
	print("Direction: ", direction)
	
	print("Going for: "+str(turns)+" turns")
	
	stepsToGo=int(turns*stepsPerTurn*microsteps)
	#for i in range(0,runFor*stepsPerTurn*microsteps):
	for i in range(0,stepsToGo):
		#print("step: ", i)
		GPIO.output(stepPin, True)
		GPIO.output(stepPin2, True)
		time.sleep(sleepTimeStep)
		print("step")
		GPIO.output(stepPin, False)
		GPIO.output(stepPin2, False)
		time.sleep(sleepTimeStep)
		
	
	GPIO.output(enablePin, True)
	GPIO.output(enablePin2, True)
	print("finished, motor disabled")
		
		
if __name__ == "__main__":
	main()


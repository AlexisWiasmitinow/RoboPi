#!/usr/bin/env python
from pinConfigurations import *
from ActorsControl import *
import time
#import Adafruit_PCA9685
#pwm = Adafruit_PCA9685.PCA9685()
#pwm.set_pwm_freq(60)

servo_min = 150  # Min pulse length out of 4096
servo_max = 600  # Max pulse length out of 4096

#pwm.set_pwm(0, 0, servo_max)
lookTo(servo_min)
#servoOff()
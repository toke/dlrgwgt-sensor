#!/bin/env python

import RPi.GPIO as GPIO

#GPIO.setmode(GPIO.BCM)
GPIO.setmode(GPIO.BOARD)
#GPIO.setup(3, GPIO.IN)
#GPIO.setup(7, GPIO.IN)
#GPIO.setup(8, GPIO.IN)
#GPIO.setup(17, GPIO.IN)
#GPIO.setup(18, GPIO.IN)
#GPIO.setup(27, GPIO.IN)


#print GPIO.input(3)
#print GPIO.input(8)
#print GPIO.input(17)
#print GPIO.input(18)
#print GPIO.input(27)

GPIO.cleanup()

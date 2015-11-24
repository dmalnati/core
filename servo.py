#!/usr/bin/env python


import RPi.GPIO as GPIO
import time


from libServo import *


PIN_OUT = 7

def Setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIN_OUT, GPIO.OUT)
    s = ServoControlDiscrete(PIN_OUT, 0.5, 2.4)

    return s

def Cleanup():
    GPIO.cleanup()

def MoveAround(s):
    for count in range(0, 3):
        s.MoveTo(0.0)
        s.MoveTo(25.0)
        s.MoveTo(50.0)
        s.MoveTo(75.0)
        s.MoveTo(100.0)

    s.MoveTo(50.0)

s = Setup()
MoveAround(s)
Cleanup()


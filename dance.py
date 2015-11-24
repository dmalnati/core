#!/usr/bin/python

import sys
import random

import RPi.GPIO as GPIO

from libServo import *



def SetUpGPIO(pin):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.OUT)


def CleanUpGPIO():
    GPIO.cleanup()


def Main():
    pin = 7

    SetUpGPIO(pin)
    s = ServoControlDiscrete(pin)

    while True:
        break
        pct = 25
        print(pct)
        s.MoveTo(pct)
        pct = 75
        print(pct)
        s.MoveTo(pct)

    while True:
        pct = random.randint(0, 100)
        print(pct)
        s.MoveTo(pct)

    CleanUpGPIO()


Main()

#!/usr/bin/python

import sys
import os
import time

import RPi.GPIO as GPIO

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *


def PinPulse(bcPin, msInterval):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(bcPin, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)

    while True:
#        print("HIGH")
        GPIO.output(bcPin, GPIO.HIGH)
        time.sleep(msInterval)

#        print("LOW")
        GPIO.output(bcPin, GPIO.LOW)
        time.sleep(msInterval)

def PinPulseExperimental(bcPin, msIntervalDiscard):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(bcPin, GPIO.OUT, pull_up_down=GPIO.PUD_DOWN)

    p = GPIO.PWM(bcPin, 50)

    msStart = 1.0
    msEnd   = 2.0

    pctStart = msStart / (1000.0 / 50.0) * 100
    pctEnd   = msEnd   / (1000.0 / 50.0) * 100
    pctNow   = pctStart
    pctStep  = 0.1

    p.start(pctNow)
    while pctNow < pctEnd:
        print("Changing to " + str(pctNow))
        p.ChangeDutyCycle(pctNow)
        time.sleep(0.5)

        pctNow += pctStep

    print ("DONE")


def Main():
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " <bcPin> <msInterval>")
        sys.exit(-1)

    bcPin      = int(sys.argv[1])
    msInterval = float(sys.argv[2]) / 1000.0

    PinPulse(bcPin, msInterval)

    evm_MainLoop()


Main()



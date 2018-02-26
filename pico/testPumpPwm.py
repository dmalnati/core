#!/usr/bin/python

import os
import sys
import time

import pigpio


sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *


# http://abyz.me.uk/rpi/pigpio/python.html
PIG    = pigpio.pi()
BC_PIN = None



def OnKeyboardReadable(inputStr):
    global BC_PIN

    pwmPct       = int(inputStr)
    pwmDutyCycle = int(float(pwmPct) * 255.0 / 100.0)

    print("Changing PWM to be %s%%" % (pwmPct))
    print("")

    PIG.set_PWM_dutycycle(BC_PIN, pwmDutyCycle)


def ControlPWM():
    global BC_PIN

    WatchStdinEndLoopOnEOF(OnKeyboardReadable, binary=True)

    print("Enter a number in the range 0-100")

    evm_MainLoop()

    # Stop PWM once you hit CTL+C
    print("")
    print("Stopping PWM, exiting")
    PIG.set_PWM_dutycycle(BC_PIN, 0)
    PIG.stop()


def Main():
    global BC_PIN

    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " <bcPin>")
        sys.exit(-1)

    BC_PIN = int(sys.argv[1])

    ControlPWM()


Main()









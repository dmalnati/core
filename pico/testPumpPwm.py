#!/usr/bin/python

import os
import sys
import time

from libPumpPwm import *

import pigpio


sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *


PUMP = None


def OnKeyboardReadable(inputStr):
    global PUMP

    inputStr = inputStr.strip()

    if inputStr != "":
        print("Changing PWM to be %s%%" % (inputStr))
        print("")

        PUMP.SetPwmPct(inputStr)


def ControlPWM():
    global PUMP

    WatchStdinEndLoopOnEOF(OnKeyboardReadable, binary=True)

    print("Enter a number in the range 0-100")

    evm_MainLoop()

    # Stop PWM once you hit CTL+C
    print("")
    print("Stopping PWM, exiting")
    PUMP.End()


def Main():
    global PUMP

    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " <bcPin>")
        sys.exit(-1)

    PUMP = PumpPwm(int(sys.argv[1]))

    ControlPWM()


Main()









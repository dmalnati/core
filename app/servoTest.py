#!/usr/bin/python

import sys
import os

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.ws import *
from myLib.motor import *


def ControlServo(bcPin):
    pigd = pigpio.pi()
    sc = ServoControl(pigd, bcPin)

    def OnStdin(line):
        sc.MoveTo(line)

    WatchStdinEndLoopOnEOF(OnStdin)

def Main():
    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " <bcPin>")
        sys.exit(-1)

    bcPin = sys.argv[1]

    ControlServo(bcPin)

    evm_MainLoop()


Main()



#!/usr/bin/python

import sys
import os
import time

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *


tickLast = 0

def CbEdgeChange(bcPin, level, tick):
    global tickLast

    diffTick = tick - tickLast
    tickLast = tick

    if diffTick > 2000:
        print("")

    print("bcPin: " + str(bcPin) + ", level: " + str(level) + ", tick: " + str(tick) + ", diffTick: " + str(diffTick))


def WatchPin(bcPin):
    pigd = pigpio.pi()

    pigd.set_mode(bcPin, pigpio.INPUT)
    pigd.set_glitch_filter(bcPin, 250)
#    pigd.set_pull_up_down(bcPin, pigpio.PUD_DOWN)

    cbCtl = pigd.callback(bcPin, pigpio.EITHER_EDGE, CbEdgeChange)


def Main():
    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " <bcPin>")
        sys.exit(-1)

    bcPin = int(sys.argv[1])

    WatchPin(bcPin)

    print("Waiting")
    evm_MainLoop()


Main()



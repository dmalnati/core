#!/usr/bin/python

import sys
import os
import math
import signal

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.motor import *


def DegToRad(deg):
    return ((float(deg) / 360.0) * (math.pi * 2.0))

def DegToX(deg, leftRightRange=90.0):
    return (leftRightRange * math.sin(DegToRad(deg)))

def DegToY(deg, upDownRange=90.0):
    return (upDownRange * math.cos(DegToRad(deg)))

cont = True
def Dance(bcPinX, bcPinY):
    global cont

    pigd = pigpio.pi()

    scX = ServoControl(pigd, bcPinX)
    scY = ServoControl(pigd, bcPinY)

    degStep = 1
    deg     = 0

    scX.MoveTo(0)
#    scY.MoveTo(90)
    scY.MoveTo(0)

    time.sleep(.3)

    while cont:
        degX = DegToX(deg)
        degY = DegToY(deg)

        print("deg(" + str(deg) +
              "), X(" + str(degX) +
              "), Y(" + str(degY) + ")")

        scX.MoveTo(degX)
#        scY.MoveTo(degY)

        deg = (deg + degStep) % 360

        time.sleep(.5)

    scX.Stop()
    scY.Stop()



def Main():
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " <bcPinX> <bcPinY>")
        sys.exit(-1)

    bcPinX = sys.argv[1]
    bcPinY = sys.argv[2]

    print("Starting")

    def OnCtlC(signal, frame):
        global cont
        cont = False
    signal.signal(signal.SIGINT, OnCtlC)

    Dance(bcPinX, bcPinY)


Main()






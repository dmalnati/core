#!/usr/bin/python

import sys
import os

import RPi.GPIO as GPIO

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'lib'))
from libUtl import *
from libSimpleWsIface import *
from libServo import *


class Handler(WSNodeMgrEventHandlerIface):
    def __init__(self, scd):
        WSNodeMgrEventHandlerIface.__init__(self)

        self.scd = scd

    def OnWebSocketConnectedInbound(self, ws):
        pass

    def OnWebSocketConnectedOutbound(self, ws, userData):
        pass

    def OnWebSocketReadable(self, ws, userData):
        data = ws.Read()
        self.scd.MoveTo(float(data))

    def OnWebSocketClosed(self, ws, userData):
        evm_MainLoopFinish()

    def OnWebSocketError(self, ws, userData):
        print("Connection Refused")
        evm_MainLoopFinish()


def SetUpGPIO(pin):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin, GPIO.OUT)


def CleanUpGPIO():
    GPIO.cleanup()


def Main():
    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " <port> <path>")
        sys.exit(-1)

    port = sys.argv[1]
    path = sys.argv[2]

    SetUpGPIO(7)
    s = ServoControlDiscrete(7)

    handler   = Handler(s)
    wsNodeMgr = WSNodeMgr(handler)

    wsNodeMgr.listen(port, path)

    evm_MainLoop()

    CleanUpGPIO()


Main()

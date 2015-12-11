#!/usr/bin/python

import sys
import os

import json

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.ws import *
from myLib.motor import *


class ServoNode(WSNodeMgrEventHandlerIface):
    def __init__(self, bcPin, url, password, clientId):
        WSNodeMgrEventHandlerIface.__init__(self)

        self.wsNodeMgr = WSNodeMgr(self)

        self.url      = url
        self.password = password
        self.clientId = clientId

        pigd = pigpio.pi()
        self.sc = ServoControl(pigd, bcPin)

    def OnWebSocketConnectedOutbound(self, ws, userData):
        Log("Connection Successful, logging in")
        ws.Write(json.dumps({
            "MESSAGE_TYPE" : "REQ_LOGIN_SC",
            "ID"           : self.clientId,
            "PASSWORD"     : self.password,
        }))
        self.sc.MoveTo(0)

    def OnWebSocketReadable(self, ws, userData):
        data = ws.Read()
        self.OnServoCommand(data)

    def OnWebSocketClosed(self, ws, userData):
        Log("Connection Lost")
        self.Restart()

    def OnWebSocketError(self, ws, userData):
        Log("Connection Refused")
        self.Restart()

    def Start(self):
        Log("Attempting connection")
        self.Restart(msDelay=0)

    def Restart(self, msDelay=1000):
        def OnTimeout():
            self.wsNodeMgr.connect(self.url)

        if msDelay != 0:
            Log("Next connection attempt in " + str(msDelay) + "ms")

        evm_SetTimeout(OnTimeout, msDelay)

    def OnServoCommand(self, deg):
        Log("Moving to " + deg)
        self.sc.MoveTo(deg)

    def Cleanup(self):
        self.sc.Stop()


def Main():
    if len(sys.argv) != 5:
        print("Usage: " +
              sys.argv[0] +
              " <bcPin> <url> <password> <clientId>")
        sys.exit(-1)

    bcPin      = sys.argv[1]
    url        = sys.argv[2]
    password   = sys.argv[3]
    clientId   = sys.argv[4]

    Log("Starting")
    servoNode = ServoNode(bcPin, url, password, clientId)
    servoNode.Start()

    evm_MainLoop()

    servoNode.Cleanup()


Main()






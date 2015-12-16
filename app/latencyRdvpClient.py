#!/usr/bin/python

import sys
import os

import json


sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.ws import *


class LatencyNode(WSNodeMgrEventHandlerIface):
    def __init__(self, url, password, clientId):
        WSNodeMgrEventHandlerIface.__init__(self)

        self.wsNodeMgr = WSNodeMgr(self)

        self.url      = url
        self.password = password
        self.clientId = clientId

    def OnWebSocketConnectedOutbound(self, ws, userData):
        Log("Connection Successful, logging in")
        ws.Write(json.dumps({
            "MESSAGE_TYPE" : "REQ_LOGIN_SC",
            "ID"           : self.clientId,
            "PASSWORD"     : self.password,
        }))

    def OnWebSocketReadable(self, ws, userData):
        msg = ws.Read()

        try:
            jsonObjReq = json.loads(msg)

            ws.Write(json.dumps({
                "MESSAGE_TYPE" : "REP_PING_PONG",
                "DATA"         : jsonObjReq
            }))
        except:
            pass


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


def Main():
    if len(sys.argv) != 4:
        print("Usage: " + sys.argv[0] + " <url> <password> <clientId>")
        sys.exit(-1)

    url        = sys.argv[1]
    password   = sys.argv[2]
    clientId   = sys.argv[3]

    Log("Starting")
    latencyNode = LatencyNode(url, password, clientId)
    latencyNode.Start()

    evm_MainLoop()


Main()






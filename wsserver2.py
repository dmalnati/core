#!/usr/bin/python

import json
import sys

from libUtl import *
from libSimpleWsIface import *



class Handler(WSNodeMgrEventHandlerIface):
    def OnWebSocketConnectedInbound(self, ws):
        Log("connected inbound: " + ws.GetId())
        self.LogState()
        Log("-----")

    def OnWebSocketConnectedOutbound(self, ws, userData):
        Log("connected outbound: " + ws.GetId() + ", " + str(userData))
        self.LogState()

    def OnWebSocketReadable(self, ws, userData):
        data = ws.Read()
        Log("readable: " + ws.GetId() + ", " + str(userData) + ": " + data)

    def OnWebSocketClosed(self, ws, userData):
        Log("closed: " + ws.GetId() + ", " + str(userData))
        self.LogState()

    def OnWebSocketError(self, ws, userData):
        Log("error: " + ws.GetId() + ", " + str(userData))
        self.LogState()


def CullHandler(handler):
    def Timeout():
        Log("Cull Start")
        for ws in handler.GetWebSocketInboundList():
            id   = ws.GetId()
            secs = ws.GetTimeDurationConnectedSecs()
            print("Checking " + id + ": connected " + str(secs) + " secs")
            if ws.GetTimeDurationConnectedSecs() > 12:
                print("Closing " + id)
                ws.Close()
        Log("Cull Complete")

    evm_PeriodicCallback(Timeout, 5000)



def Main():
    HandleSignals()

    if len(sys.argv) != 3:
        print("Usage: " + sys.argv[0] + " <port> <path>")
        sys.exit(-1)

    port = sys.argv[1]
    path = sys.argv[2]

    handler = Handler()
    wsNodeMgr = WSNodeMgr(handler)

    wsUrl = "ws://localhost:" + str(port) + path

    Log("Starting listening on " + wsUrl)
    wsNodeMgr.listen(port, path)

    CullHandler(handler)

    def ConnectToSelf():
        Log("Attempting to connect to myself on " + wsUrl)
        wsNodeMgr.connect(wsUrl, "heynow")

    evm_SetTimeout(ConnectToSelf, 3500)

    evm_MainLoop()


Main()

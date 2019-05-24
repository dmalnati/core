#!/usr/bin/python

import sys
import os

import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.ws import *



class App(WSApp):
    def __init__(self, serviceOrPort):
        WSApp.__init__(self, serviceOrPort)
        
    def Run(self):
        service, port = self.GetServiceAndPort()
        Log("%s : %s" % (service, port))

        if self.IsOk():
            self.Listen()
            
            Log("Running")
            evm_MainLoop()
            
        else:
            Log("Not OK, quitting")
            
    ######################################################################
    #
    # Implementing WSNodeMgr Events
    #
    ######################################################################

    def OnWebSocketConnectedInbound(self, ws):
        Log("OnWebSocketConnectedInbound")

    def OnWebSocketReadable(self, ws, userData):
        msg = ws.Read()
        Log("Got msg: %s" % msg)

    def OnWebSocketClosed(self, ws, userData):
        Log("WS Closed")

    def OnWebSocketError(self, ws, userData):
        Log("WebSocketError: Why did this happen?")



def Main():
    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <serviceOrPort>" % (sys.argv[0]))
        sys.exit(-1)

    serviceOrPort = sys.argv[1]

    app = App(serviceOrPort)
    app.Run()


Main()















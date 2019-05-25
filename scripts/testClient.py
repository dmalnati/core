#!/usr/bin/python

import sys
import os

import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.ws import *



class App(WSApp):
    def __init__(self, serviceOrAddrOrPort):
        WSApp.__init__(self)

        self.connectTo = serviceOrAddrOrPort
        self.ws        = None
        
    def Run(self):
        service, port = self.GetServiceAndPort()
        Log("%s : %s" % (service, port))

        if self.IsOk():
            self.Connect(self.connectTo)
            
            Log("Running")
            
            WatchStdinLinesEndLoopOnEOF(self.OnKeyboardInput)
            
            evm_MainLoop()
            
        else:
            Log("Not OK, quitting")
            
            
    def OnKeyboardInput(self, line):
        if self.ws:
            self.ws.Write(json.dumps({
                "MESSAGE_TYPE"       : "A_LINE",
                "LINE"               : line,
            }))
    
    ######################################################################
    #
    # Implementing WSNodeMgr Events
    #
    ######################################################################

    def OnWebSocketConnectedOutbound(self, ws):
        self.ws = ws
        Log("OnWebSocketConnectedOutbound")

    def OnWebSocketReadable(self, ws):
        jsonObj = json.loads(ws.Read())
        
        Log("Got data")
        print(json.dumps(jsonObj,
                         sort_keys=True,
                         indent=4,
                         separators=(',', ': ')))
        

    def OnWebSocketClosed(self, ws):
        self.ws = None
        Log("WS Closed")

    def OnWebSocketError(self, ws):
        Log("Couldn't connect")



def Main():
    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <serviceOrAddrOrPort>" % (sys.argv[0]))
        sys.exit(-1)

    serviceOrAddrOrPort = sys.argv[1]

    app = App(serviceOrAddrOrPort)
    app.Run()


Main()















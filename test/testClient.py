#!/usr/bin/python -u

import sys
import os

from libCore import *


class App(WSApp):
    def __init__(self, serviceOrAddrOrPort):
        WSApp.__init__(self)

        self.connectTo = serviceOrAddrOrPort
        self.ws        = None
        
    def Run(self):
        data = self.GetSelfServiceData()
        Log("%s : %s" % (data["service"], data["port"]))

        if self.IsOk():
            self.Connect(self.connectTo)
            
            WatchStdinLinesEndLoopOnEOF(self.OnKeyboardInput)
            
            Log("Running")
            evm_MainLoop()
            
        else:
            Log("Not OK, quitting")
            
            
    def OnKeyboardInput(self, line):
        if self.ws:
            self.ws.Write({
                "MESSAGE_TYPE"       : "A_LINE",
                "LINE"               : line,
            })
    
    ######################################################################
    #
    # Implementing WSNodeMgr Events
    #
    ######################################################################

    def OnWebSocketConnectedOutbound(self, ws):
        self.ws = ws
        Log("OnWebSocketConnectedOutbound")

    def OnWebSocketReadable(self, ws):
        msg = ws.Read()
        Log("Got data")
        ws.DumpMsg(msg)

    def OnWebSocketClosed(self, ws):
        self.ws = None
        Log("WS Closed")

    def OnWebSocketError(self, ws):
        Log("Couldn't connect")



def Main():
    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <serviceOrAddrOrPort>" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    serviceOrAddrOrPort = sys.argv[1]

    app = App(serviceOrAddrOrPort)
    app.Run()


Main()















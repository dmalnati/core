#!/usr/bin/python3.5 -u

import sys
import os

from libCore import *


class Sophisticated(WSApp):
    def __init__(self, wsApp):
        WSApp.__init__(self)
        self.wsApp = wsApp

    def Connect(self, svc):
        self.wsApp.Connect(svc, handler=self)

    ######################################################################
    ##
    ## Implementing WSNodeMgr Events
    ##
    ######################################################################

    def OnWebSocketConnectedOutbound(self, ws):
        Log("Sophisticated Connected")

    def OnWebSocketReadable(self, ws):
        msg = ws.Read()
        Log("Sophisticated Got data")
        ws.DumpMsg(msg)


    def OnWebSocketClosed(self, ws):
        Log("Sophisticated WS Closed")

    def OnWebSocketError(self, ws):
        Log("Sophisticated Couldn't connect")



class App(WSApp):
    def __init__(self, serviceOrAddrOrPort1, serviceOrAddrOrPort2):
        WSApp.__init__(self)

        self.connectTo     = serviceOrAddrOrPort1
        self.connectToAlso = serviceOrAddrOrPort2
        self.ws            = None
        self.soph          = Sophisticated(self)
        
    def Run(self):
        data = self.GetSelfServiceData()
        Log("%s : %s" % (data["service"], data["port"]))

        if self.IsOk():
            self.Connect(self.connectTo)
            self.soph.Connect(self.connectToAlso)
            
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
    if len(sys.argv) < 3 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <serviceOrAddrOrPort1> <serviceOrAddrOrPort2>" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    serviceOrAddrOrPort1 = sys.argv[1]
    serviceOrAddrOrPort2 = sys.argv[2]

    app = App(serviceOrAddrOrPort1, serviceOrAddrOrPort2)
    app.Run()


Main()















#!/usr/bin/python3.5 -u

import sys
import os

from libCore import *


class App(WSApp):
    def __init__(self, serviceOrAddrOrPort, special):
        WSApp.__init__(self)

        self.connectTo = serviceOrAddrOrPort
        self.special   = special
        self.ws        = None
        
    def Run(self):
        self.ws = self.Connect(self, self.connectTo)
        self.ws.SetSpecial(self.special)
        
        WatchStdinLinesEndLoopOnEOF(self.OnKeyboardInput)
        
        Log("Running")
        evm_MainLoop()


    def OnKeyboardInput(self, line):
        if self.ws:
            self.ws.Write({
                "MESSAGE_TYPE"       : "A_LINE",
                "LINE"               : line,
            })
    
    ######################################################################
    #
    # Implementing WSApp Events
    #
    ######################################################################

    def OnConnect(self, ws):
        self.ws = ws
        Log("OnWebSocketConnectedOutbound")

    def OnMessage(self, ws, msg):
        Log("Got WS data")
        ws.DumpMsg(msg)

    def OnClose(self, ws):
        self.ws = None
        Log("WS Closed")

    def OnError(self, ws):
        Log("Couldn't connect")



def Main():
    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <serviceOrAddrOrPort> [<special>]" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    serviceOrAddrOrPort = sys.argv[1]
    special = False
    if len(sys.argv) >= 3:
        if sys.argv[2] == "special":
            special = True

    app = App(serviceOrAddrOrPort, special)
    app.Run()


Main()















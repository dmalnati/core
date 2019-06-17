#!/usr/bin/python3.5 -u

import sys
import os

from libCore import *


class App(WSApp):
    def __init__(self, serviceOrPort):
        WSApp.__init__(self, serviceOrPort)


    def Run(self):
        WatchStdinLinesEndLoopOnEOF(self.OnKeyboardInput)

        Log("Running")
        evm_MainLoop()


    def OnKeyboardInput(self, line):
        Log("Sending keyboard input to all inbound connected")
        for ws in self.GetWSInboundList():
            ws.Write({
                "MESSAGE_TYPE" : "A_MSG_DISTRIBUTED",
                "LINE"         : line,
            })
        
        
    ######################################################################
    #
    # Implementing WSApp Events
    #
    ######################################################################
        
    def OnWSConnectIn(self, ws):
        ws.SetHandler(self)
        self.ws = ws
        numConnected = len(self.GetWSInboundList())
        Log("New inbound connection, total %s" % numConnected)
        Log("")
            
    def OnMessage(self, ws, msg):
        Log("Got WS data")
        ws.DumpMsg(msg)

    def OnClose(self, ws):
        self.ws = None
        numConnected = len(self.GetWSInboundList())
        Log("WS inbound closed, total %s" % numConnected)

    def OnError(self, ws):
        Log("Couldn't connect")



def Main():
    serviceOrPort = None
    
    if len(sys.argv) < 1 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s [<serviceOrPort>]" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    if len(sys.argv) >= 2:
        serviceOrPort = sys.argv[1]

    app = App(serviceOrPort)
    app.Run()


Main()















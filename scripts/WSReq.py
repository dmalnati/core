#!/usr/bin/python -u

import sys
import os

from libCore import *


class App(WSApp):
    def __init__(self, serviceOrAddrOrPort, command):
        WSApp.__init__(self)

        self.connectTo = serviceOrAddrOrPort
        self.command   = command
        self.ws        = None
        self.worked    = False
        
    def Run(self):
        self.ws = self.Connect(self, self.connectTo)
        self.ws.SetSpecial(True)
        
        WatchStdinLinesEndLoopOnEOF(self.OnKeyboardInput)
        
        Log("Running")
        evm_MainLoop()

        return self.worked


    def OnKeyboardInput(self, line):
        pass
    
    def OnTimeout(self):
        Log("Timed out waiting for reply, exiting")
        evm_MainLoopFinish()


    ######################################################################
    #
    # Implementing WSApp Events
    #
    ######################################################################

    def OnConnect(self, ws):
        Log("Connected, sending command %s" % self.command)
        self.ws = ws
        self.ws.Write({
            "COMMAND" : self.command,
        })
        Log("Waiting for reply...")

        evm_SetTimeout(self.OnTimeout, 10000)

    def OnMessage(self, ws, msg):
        if "REPLY" in msg:
            reply = msg["REPLY"] 

            if reply == "ACK":
                self.worked = True

            Log("Got Response: %s" % reply)
        else:
            Log("Got Response, not understood:")
            ws.DumpMsg(msg)

        Log("Exiting")
        evm_MainLoopFinish()

    def OnClose(self, ws):
        Log("Connection closed, exiting")
        evm_MainLoopFinish()

    def OnError(self, ws):
        Log("Couldn't connect")
        evm_MainLoopFinish()



def Main():
    if len(sys.argv) < 3 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <serviceOrAddrOrPort> <command>" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    serviceOrAddrOrPort = sys.argv[1]
    command             = sys.argv[2]

    app = App(serviceOrAddrOrPort, command)

    return app.Run() == False


sys.exit(Main())















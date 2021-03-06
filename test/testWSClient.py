#!/usr/bin/python3.5 -u

import sys
import os

import json

from libCore import *
from libWS import *



class Handler(WebSocketEventHandler):
    def __init__(self, app):
        self.ws = None
        self.app = app

    def OnConnect(self, ws):
        Log("OnConnect")
        self.ws = ws

    def OnMessage(self, ws, msg):
        Log("OnMessage: %s" % msg)

    def OnClose(self, ws):
        Log("OnClose")
        self.ws = None
        self.app.Connect()

    def OnError(self, ws):
        Log("OnError")

    def GotData(self, line):
        Log("Handler data: %s" % line)
        if self.ws:
            self.ws.Write({
                "MESSAGE_TYPE" : "A_LINE",
                "LINE"         : line,
            })
        


class App():
    def __init__(self, addr):
        self.connectTo = addr
        self.wsm       = WSManager(os.getpid())
        self.webSocket = None
        self.handler   = Handler(self)

    def Connect(self):
        self.webSocket = self.wsm.Connect(self.handler, self.connectTo)

    def Run(self):
        Log("Starting")

        self.Connect()
        
        WatchStdinLinesEndLoopOnEOF(self.OnKeyboardInput)
        
        Log("Running")
        evm_MainLoop()

    def OnKeyboardInput(self, line):
        Log("Got data: %s" % line)
        self.handler.GotData(line)



def Main():
    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <addr>" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    addr = sys.argv[1]

    app = App(addr)
    app.Run()


Main()















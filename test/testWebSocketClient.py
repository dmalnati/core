#!/usr/bin/python3.5 -u

import sys
import os

import json

from libCore import *



class Handler(WebSocketEventHandler):
    def __init__(self, raw):
        self.raw = raw
        self.ws  = None

    def OnConnect(self, ws):
        Log("OnConnect")
        self.ws = ws

    def OnMessage(self, ws, msg):
        Log("OnMessage: %s" % msg)

    def OnClose(self, ws):
        Log("OnClose")
        self.ws = None

    def OnError(self, ws):
        Log("OnError")

    def GotData(self, line):
        Log("Handler data: %s" % line)
        if self.ws:
            if self.raw:
                self.ws.Write(line)
            else:
                self.ws.Write(json.dumps({
                    "MESSAGE_TYPE" : "A_LINE",
                    "LINE"         : line,
                }))
        


class App():
    def __init__(self, addr, raw):
        self.connectTo = addr
        self.webSocket = None
        self.handler   = Handler(raw)

    def Run(self):
        Log("Starting")

        self.webSocket = WebSocketOutbound(self.handler, self.connectTo)
        self.webSocket.Connect()
        
        WatchStdinLinesEndLoopOnEOF(self.OnKeyboardInput)
        
        Log("Running")
        evm_MainLoop()

    def OnKeyboardInput(self, line):
        Log("Got data: %s" % line)
        self.handler.GotData(line)



def Main():
    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <addr> [-raw]" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    addr = sys.argv[1]
    raw = False
    if len(sys.argv) >= 3:
        raw = sys.argv[2] == "-raw"
    
    app = App(addr, raw)
    app.Run()


Main()















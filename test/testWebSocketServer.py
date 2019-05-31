#!/usr/bin/python -u

import sys
import os

from libCore import *



class HandlerOnNew(WebSocketConnectionReceivedEventHandler):
    def __init__(self, theWebSocketEventHandler):
        self.theWebSocketEventHandler = theWebSocketEventHandler

    def OnConnect(self, ws):
        Log("OnConnect")
        self.theWebSocketEventHandler.HeyYouGotAWebSocket(ws)


class Handler(WebSocketEventHandler):
    def __init__(self):
        self.ws = None

    def HeyYouGotAWebSocket(self, ws):
        Log("Given a WebSocket")
        self.ws = ws
        ws.SetHandler(self)

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
            self.ws.Write(json.dumps({
                "MESSAGE_TYPE" : "A_LINE",
                "LINE"         : line,
            }))



class App():
    def __init__(self, port, wsPath):
        self.port         = port
        self.wsPath       = wsPath
        self.wsMgr        = WebServiceManager()
        self.handler      = Handler()
        self.handlerOnNew = HandlerOnNew(self.handler)
        
    def Run(self):
        Log("%s : %s" % (self.port, self.wsPath))
        
        self.wsMgr.Listen(self.port)
        self.wsMgr.AddWebSocketListener(self.handlerOnNew, self.wsPath)
        
        WatchStdinLinesEndLoopOnEOF(self.OnKeyboardInput)

        Log("Running")
        evm_MainLoop()


    def OnKeyboardInput(self, line):
        Log("Got data: %s" % line)
        self.handler.GotData(line)
        

def Main():
    if len(sys.argv) < 3 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <port> <wsPath>" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    port   = sys.argv[1]
    wsPath = sys.argv[2]

    app = App(port, wsPath)
    app.Run()


Main()















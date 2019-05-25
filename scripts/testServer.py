#!/usr/bin/python -u

import sys
import os

from libCore import *


class App(WSApp):
    def __init__(self, serviceOrPort):
        WSApp.__init__(self, serviceOrPort)
        
    def Run(self):
        data = self.GetSelfServiceData()
        Log("%s : %s" % (data["service"], data["port"]))

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

    def OnWebSocketReadable(self, ws):
        jsonObj = json.loads(ws.Read())
        
        Log("Got data, distributing")
        print(json.dumps(jsonObj,
                         sort_keys=True,
                         indent=4,
                         separators=(',', ': ')))
        
        line = jsonObj["LINE"]
        
        for wsIn in self.GetWebSocketInboundList():
            wsIn.Write(json.dumps({
                "MESSAGE_TYPE"       : "A_MSG_DISTRIBUTED",
                "LINE"               : line,
            }))

    def OnWebSocketClosed(self, ws):
        Log("WS Closed")

    def OnWebSocketError(self, ws):
        Log("WebSocketError: Why did this happen?")



def Main():
    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <serviceOrPort>" % (sys.argv[0]))
        sys.exit(-1)

    serviceOrPort = sys.argv[1]

    app = App(serviceOrPort)
    app.Run()


Main()















#!/usr/bin/python

import sys

from libUtl import *
from libSimpleWsIface import *


class Handler(WSNodeMgrEventHandlerIface):
    def OnWebSocketConnectedInbound(self, ws):
        Bridge(ws)

    def OnWebSocketConnectedOutbound(self, ws, userData):
        Bridge(ws)

    def OnWebSocketReadable(self, ws, userData):
        data = ws.Read()
        print(data)

    def OnWebSocketClosed(self, ws, userData):
        sys.exit(0)

    def OnWebSocketError(self, ws, userData):
        sys.exit(0)

def Bridge(ws):
    def OnStdin():
        line = sys.stdin.readline()
        if not line:
            ws.Close()
            sys.exit(0)
        else:
            ws.Write(line.rstrip("\n"))

    WatchStdin(OnStdin)


def Main():
    HandleSignals()

    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("Usage:")
        print("       " + sys.argv[0] + " connect <url>")
        print("       " + sys.argv[0] + " listen  <port> <path>")
        sys.exit(-1)

    mode = sys.argv[1]

    handler   = Handler()
    wsNodeMgr = WSNodeMgr(handler)

    if mode == "connect" and len(sys.argv) == 3:
        url = sys.argv[2]

        wsNodeMgr.connect(url)
    elif mode == "listen" and len(sys.argv) == 4:
        port = sys.argv[2]
        path = sys.argv[3]

        wsNodeMgr.listen(port, path)
    else:
        print("Invalid arguments")
        sys.exit(-1)

    evm_MainLoop()


Main()

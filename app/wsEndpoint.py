#!/usr/bin/python

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.ws import *


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
        print("Connection Refused")
        sys.exit(0)


def Bridge(ws):
    def OnStdin():
        line = sys.stdin.readline()
        if not line:
            ws.Close()
            sys.exit(0)
        else:
            ws.Write(line.rstrip("\n"))

    WatchStdinRaw(OnStdin)


def Main():
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("Usage:")
        print("       " + sys.argv[0] + " <url>         (to connect)")
        print("       " + sys.argv[0] + " <port> <path> (to listen)")
        sys.exit(-1)

    handler   = Handler()
    wsNodeMgr = WSNodeMgr(handler)

    if len(sys.argv) == 2:
        url = sys.argv[1]

        wsNodeMgr.connect(url)
    elif len(sys.argv) == 3:
        port = sys.argv[1]
        path = sys.argv[2]

        wsNodeMgr.listen(port, path)
    else:
        print("Invalid arguments")
        sys.exit(-1)

    evm_MainLoop()


Main()

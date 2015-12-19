#!/usr/bin/python

import sys
import os

import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.ws import *


def GetPrettyJSON(jsonObj):
    return json.dumps(jsonObj,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))

def OnHandleMessage(jsonObj):
    msgType = jsonObj["type"]

    if msgType == "offer":
        sdpStr = jsonObj["sdp"]

        Log("SDP: \n" + sdpStr)
    elif msgType == "geticecandidate":
        dataStr = jsonObj["data"]

        dataObj = json.loads(dataStr)
        Log("ICE Candidate: \n" + GetPrettyJSON(dataObj))
    elif msgType == "message":
        dataStr = jsonObj["data"]
        Log("Message: " + dataStr)


class Handler(WSNodeMgrEventHandlerIface):
    def OnWebSocketConnectedInbound(self, ws):
        Bridge(ws)

    def OnWebSocketConnectedOutbound(self, ws, userData):
        Bridge(ws)

    def OnWebSocketReadable(self, ws, userData):
        data = ws.Read()
        jsonObj = json.loads(data);

        Log("Received JSON:")
        print(GetPrettyJSON(jsonObj))

        OnHandleMessage(jsonObj)

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
            line = line.rstrip("\n");

            if line == "offer":
                str = json.dumps({
                    "command_id" : "offer"
                })

                Log("Sending: " + str)
                ws.Write(str)

                str = json.dumps({
                    "command_id" : "geticecandidate"
                })
                Log("Sending: " + str)
                ws.Write(str)

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

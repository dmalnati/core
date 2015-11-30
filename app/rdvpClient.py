#!/usr/bin/python

import sys
import os

import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.ws import *


class Handler(WSNodeMgrEventHandlerIface):
    def __init__(self, password, clientType, clientId, scClientId):
        WSNodeMgrEventHandlerIface.__init__(self)

        self.password   = password
        self.clientType = clientType
        self.clientId   = clientId
        self.scClientId = scClientId

    def OnWebSocketConnectedOutbound(self, ws, userData):
        if self.clientType == "CC":
            ws.Write(json.dumps({
                "MESSAGE_TYPE"  : "REQ_LOGIN_" + self.clientType,
                "ID"            : self.clientId,
                "PASSWORD"      : self.password,
                "CONNECT_TO_ID" : self.scClientId
            }))

            Bridge(ws)
        elif self.clientType == "SC":
            ws.Write(json.dumps({
                "MESSAGE_TYPE"  : "REQ_LOGIN_" + self.clientType,
                "ID"            : self.clientId,
                "PASSWORD"      : self.password
            }))
            ws.Write("queue this")
            ws.Write("and this")

            Bridge(ws)
        elif self.clientType == "AC":
            ws.Write(json.dumps({
                "MESSAGE_TYPE"  : "REQ_LOGIN_" + self.clientType,
                "ID"            : self.clientId,
                "PASSWORD"      : self.password
            }))

            Bridge(ws)
        else:
            ws.Write(json.dumps({
                "MESSAGE_TYPE"  : "REQ_LOGIN_" + self.clientType,
                "ID"            : self.clientId,
                "PASSWORD"      : self.password
            }))

            Bridge(ws)
            


    def OnWebSocketReadable(self, ws, userData):
        data = ws.Read()

        if self.clientType == "AC":
            jsonObj = json.loads(data)
            print(json.dumps(jsonObj,
                             sort_keys=True,
                             indent=4,
                             separators=(',', ': ')))
        else:
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

    WatchStdin(OnStdin)


def Main():
    if len(sys.argv) != 5 and len(sys.argv) != 6:
        print("Usage:")
        print("         " + sys.argv[0] + " <url> <password> SC <clientId>")
        print("         " +
              sys.argv[0] +
              " <url> <password> CC <clientId> <scClientId>")
        print("         " + sys.argv[0] + " <url> <password> AC <clientId>")
        sys.exit(-1)

    url        = sys.argv[1]
    password   = sys.argv[2]
    clientType = sys.argv[3]
    clientId   = sys.argv[4]

    scClientId = None
    if clientType == "CC":
        if (len(sys.argv) == 6):
            scClientId = sys.argv[5]
        else:
            print("Err: Client Type SC must have scClientId argument")
            sys.exit(-1)

    handler   = Handler(password, clientType, clientId, scClientId)
    wsNodeMgr = WSNodeMgr(handler)

    wsNodeMgr.connect(url)

    evm_MainLoop()


Main()






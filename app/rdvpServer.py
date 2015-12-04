#!/usr/bin/python

import sys
import os

from collections import deque

import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.ws import *


'''
Rendez-vous Point Server

In change of pairing up clients who want to relay data back and forth to one
another.

Expects three types of clients to connect in:
- Server-client: Those offering to be connected to
- Client-client: Those initiating connection to a server-client
- Admin-client : Those interacting with the server itself


Any Server-client will, upon connection:
- send type, id, password, and services
- wait for ack or close
- any subsequent data is comms from other party

Any Client-client will, upon connection:
- send type, id, password, and id to connect to
- wait for ack or close
- any subsequent data is comms from other party

Any Admin-client will, upon connection:
- send type, id, and password
- send/receive admin messages


Initial use-case is for internet-relay of comms between RPi and web client.

Expected use there is for setting up WebRTC comms.  The rdvp is not involved
in any WebRTC-specific behavior.  It is simply a central location to find
other devices.

Future-facing, this is likely a control-panel type of hub which can serve up
web pages which make interfacing with connect-in devices easier.

'''


class RDVPClient():
    def __init__(self, ws, clientType, clientId):
        self.ws = ws

        self.clientType = clientType
        self.clientId = clientId

        self.msgQueue = deque()

        self.wantsEventOnBridgeUp = False

        self.bridgedPair = None

    def SetWantsEventOnBridgeUp(self):
        self.wantsEventOnBridgeUp = True

    def GetWantsEventOnBridgeUp(self):
        return self.wantsEventOnBridgeUp

    def GetClientType(self):
        return self.clientType

    def GetClientId(self):
        return self.clientId

    def GetWs(self):
        return self.ws

    def QueueMessage(self, msg):
        self.msgQueue.append(msg)

    def GetMessageQueue(self):
        return self.msgQueue

    def ClearMessageQueue(self):
        self.msgQueue.clear()

    def SetBridgedPair(self, client):
        self.bridgedPair = client

    def GetBridgedPair(self):
        return self.bridgedPair

    def IsBridged(self):
        return self.bridgedPair != None






class RDVPServer(WSNodeMgrEventHandlerIface):
    def __init__(self, password):
        WSNodeMgrEventHandlerIface.__init__(self)

        self.password = password

        self.ws__client = {}
        self.bridgeList = deque()


    def GetClientByTypeId(self, clientType, clientId):
        retVal = None

        for ws, client in self.ws__client.items():
            if client.GetClientType() == clientType and \
               client.GetClientId()   == clientId:
                retVal = client
                break

        return retVal

    def IsIdInUse(self, clientType, clientId):
        return self.GetClientByTypeId(clientType, clientId) != None

    def Bridge(self, clientId, connectToId):
        cc = self.GetClientByTypeId("CC", clientId)
        sc = self.GetClientByTypeId("SC", connectToId)

        cc.SetBridgedPair(sc)
        sc.SetBridgedPair(cc)

        if cc.GetWantsEventOnBridgeUp():
            self.SendEventOnBridgeUp(cc.GetWs(),
                                     cc.GetClientId(),
                                     sc.GetClientId())

        if sc.GetWantsEventOnBridgeUp():
            self.SendEventOnBridgeUp(sc.GetWs(),
                                     cc.GetClientId(),
                                     sc.GetClientId())

        self.BroadcastAdminData({
            "CCSC_BRIDGE_LIST_INSERT" : [[cc.GetClientId(), sc.GetClientId()]]
        })

        Log("Bridge(" + cc.GetClientId() + ", " + sc.GetClientId() + ") Up")
        if len(sc.GetMessageQueue()):
            #Log("    SC(" + sc.GetClientId() + ") had " +
            #    str(len(sc.GetMessageQueue())) +
            #    " queued msgs, flushing")
            for msg in sc.GetMessageQueue():
                self.PassMessage(sc, cc, msg)
            sc.ClearMessageQueue()

    def RegisterClient(self, ws, clientType, clientId):
        client = RDVPClient(ws, clientType, clientId)
        self.ws__client[ws] = client

        Log(clientType + "(" + clientId + ") Registered")

        self.BroadcastAdminData({
            clientType + "_LIST_INSERT" : [clientId]
        })

        return client


    def IsClientKnown(self, ws):
        return ws in self.ws__client

    def PassMessage(self, clientFrom, clientTo, msg):
        #Log(clientFrom.GetClientType() + "(" + clientFrom.GetClientId() +
        #    ") sent message, bridging to pair " +
        #    clientTo.GetClientType() + "(" + clientTo.GetClientId() + ")")
        clientTo.GetWs().Write(msg)






    def HandleAdminMsg(self, client, msg):
        # should be json
        # should be message types we recognize
        Log(client.GetClientType() + "(" +
            client.GetClientId() + ") sent msg")


    def GetAdminClientImage(self):
        jsonObj = {}

        scList = []
        ccList = []
        acList = []

        ccscBridgeList = []

        for ws, client in self.ws__client.items():
            if client.GetClientType() == "SC":
                scList.append(client.GetClientId())
            if client.GetClientType() == "CC":
                ccList.append(client.GetClientId())
                if client.IsBridged():
                    ccscBridgeList.append([
                        client.GetClientId(), 
                        client.GetBridgedPair().GetClientId()
                    ])
            if client.GetClientType() == "AC":
                acList.append(client.GetClientId())

        jsonObj["SC_LIST"] = scList
        jsonObj["CC_LIST"] = ccList
        jsonObj["AC_LIST"] = acList

        jsonObj["CCSC_BRIDGE_LIST"] = ccscBridgeList

        return jsonObj

    def BroadcastAdminData(self, deltaObj=None):
        jsonObj = self.GetAdminClientImage()
        jsonObj["MESSAGE_TYPE"] = "EVENT_IMAGE"

        # incorporate changes
        if deltaObj:
            for listType in ["SC", "CC", "AC", "CCSC_BRIDGE"]:
                for operation in ["INSERT", "DELETE"]:
                    field = listType + "_LIST_" + operation
                    if field in deltaObj:
                        jsonObj[field] = deltaObj[field]
                    else:
                        jsonObj[field] = []

        # broadcast
        for ws, client in self.ws__client.items():
            if client.GetClientType() == "AC":
                ws.Write(json.dumps(jsonObj))


    def HandleClientMsg(self, ws, msg):
        client = self.ws__client[ws]

        if client.GetClientType() == "AC":
            self.HandleAdminMsg(client, msg)
        else:
            if client.IsBridged():
                self.PassMessage(client, client.GetBridgedPair(), msg)
            else:
                # hmm, this would have to be an SC I think...
                # the cc will have been connected (or not) instantly by now,
                # so no chance to queue.
                #Log("SC(" + client.GetClientId() +
                #    ") sent message but not bridged, queuing")
                client.QueueMessage(msg)


    def HandleClientDisconnect(self, ws):
        client = self.ws__client[ws]

        if client.GetClientType() == "AC":
            # ok, don't care, just remove reference
            clientId = client.GetClientId()

            del self.ws__client[ws]
            Log("AC(" + clientId + ") De-registered")

            self.BroadcastAdminData({
                "AC_LIST_DELETE" : [clientId]
            })
        else:
            if client.IsBridged():
                # get bridged pair
                bridgedPair = client.GetBridgedPair()


                # build delta
                deltaObj = {}
                deltaObj[client.GetClientType() + "_LIST_DELETE"] = \
                    [client.GetClientId()]
                deltaObj[bridgedPair.GetClientType() + "_LIST_DELETE"] = \
                    [bridgedPair.GetClientId()]
                ccscBridge = []
                if client.GetClientType() == "CC":
                    ccscBridge = \
                        [client.GetClientId(), bridgedPair.GetClientId()]
                else:
                    ccscBridge = \
                        [bridgedPair.GetClientId(), client.GetClientId()]
                deltaObj["CCSC_BRIDGE_LIST_DELETE"] = [ccscBridge]


                Log(client.GetClientType() +
                    "(" + client.GetClientId() + ") De-registered")
                # remove reference for end which closed itself
                del self.ws__client[ws]

                Log("Bridge(" + ccscBridge[0] + ", " +
                     ccscBridge[1] + ") Down")

                # close and remove reference for other side
                Log(bridgedPair.GetClientType() +
                    "(" + bridgedPair.GetClientId() +
                    ") De-registered as a result of Bridge Down")

                bridgedPair.GetWs().Close()
                del self.ws__client[bridgedPair.GetWs()]

                # Broadcast change
                self.BroadcastAdminData(deltaObj)
            else:
                Log(client.GetClientType() +
                    "(" + client.GetClientId() + ") De-registered")
                # ok, don't care, just remove reference
                del self.ws__client[ws]

                self.BroadcastAdminData({
                    client.GetClientType() + "_LIST_DELETE" : \
                        [client.GetClientId()]
                })







    ##################################################################
    #
    # Login Validation
    #
    ##################################################################


    def SendAck(self, ws, messageType):
        ws.Write(json.dumps({
            "MESSAGE_TYPE" : messageType.replace("REQ_", "REP_", 1),
            "ERROR"        : 0
        }))

    def SendNackAndClose(self, ws, messageType, errorText):
        Log("Nacking and Closing: " + errorText)
        ws.Write(json.dumps({
            "MESSAGE_TYPE" : messageType.replace("REQ_", "REP_", 1),
            "ERROR"        : 1,
            "REASON"       : errorText
        }))

        ws.Close()

    def SendEventOnBridgeUp(self, ws, ccId, scId):
        ws.Write(json.dumps({
            "MESSAGE_TYPE" : "EVENT_BRIDGE_UP",
            "CC_ID"        : ccId,
            "SC_ID"        : scId,
        }))

    def ValidateBasicLogin(self,
                           ws,
                           clientType,
                           jsonObjReq,
                           registerClientOnOk=True,
                           ackIfRequested=True,
                           forceAck=False):
        retVal = True

        messageType = jsonObjReq["MESSAGE_TYPE"]
        clientId    = jsonObjReq["ID"]

        #Log("Validating Basic Login for " + \
        #    clientType + "(" + clientId + ")")
        if self.IsIdInUse(clientType, clientId):
            retVal = False
            errorText = clientType + "(" + clientId + ") already in use"

            self.SendNackAndClose(ws, messageType, errorText)
        else:
            # allow client to request to get an ACK.
            if (ackIfRequested and "ACK_ON_OK" in jsonObjReq) or forceAck:
                self.SendAck(ws, messageType)

            if registerClientOnOk:
                self.RegisterClient(ws, clientType, clientId)

                if "EVENT_ON_BRIDGE_UP" in jsonObjReq:
                    client = self.GetClientByTypeId(clientType, clientId)
                    client.SetWantsEventOnBridgeUp()


        return retVal


    def HandleNewLoginSC(self, ws, jsonObjReq):
        self.ValidateBasicLogin(ws, "SC", jsonObjReq)

    def HandleNewLoginCC(self, ws, jsonObjReq):
        messageType = jsonObjReq["MESSAGE_TYPE"]
        clientId    = jsonObjReq["ID"]
        connectToId = jsonObjReq["CONNECT_TO_ID"]

        errorText = None

        if self.ValidateBasicLogin(ws, "CC", jsonObjReq, False, False):
            # validate that SC client is logged in such that they can bridge
            if self.IsIdInUse("SC", connectToId):
                scClient = self.GetClientByTypeId("SC", connectToId)

                # ensure connection not attempted to already-bridged SC
                if not scClient.IsBridged():
                    # allow client to request to get an ACK.
                    if "ACK_ON_OK" in jsonObjReq:
                        self.SendAck(ws, messageType)

                    self.RegisterClient(ws, "CC", clientId)

                    if "EVENT_ON_BRIDGE_UP" in jsonObjReq:
                        client = self.GetClientByTypeId("CC", clientId)
                        client.SetWantsEventOnBridgeUp()

                    self.Bridge(clientId, connectToId)
                else:
                    errorText = "Attempted to connect to SC(" + \
                                connectToId                    + \
                                ") which is already in use"
                    self.SendNackAndClose(ws, messageType, errorText)
            else:
                errorText = "Attempted to connect to SC(" + \
                            connectToId                    + \
                            ") which is not logged in"
                self.SendNackAndClose(ws, messageType, errorText)


    def HandleNewLoginAC(self, ws, jsonObjReq):
        self.ValidateBasicLogin(ws, "AC", jsonObjReq, True, True, True)


    def HandleNewLogin(self, ws, msg):
        try:
            jsonObjReq = json.loads(msg)
        except:
            self.SendNackAndClose(ws,
                                  "REQ_INVALID_FORMAT",
                                  "Invalid Message Format (" + msg + ")")
        else:
            messageType = jsonObjReq["MESSAGE_TYPE"]
            password    = jsonObjReq["PASSWORD"]

            if password == self.password:
                if messageType == "REQ_LOGIN_SC":
                    self.HandleNewLoginSC(ws, jsonObjReq)
                elif messageType == "REQ_LOGIN_CC":
                    self.HandleNewLoginCC(ws, jsonObjReq)
                elif messageType == "REQ_LOGIN_AC":
                    self.HandleNewLoginAC(ws, jsonObjReq)
                else:
                    self.SendNackAndClose(ws,
                                          messageType,
                                          "Invalid MESSAGE_TYPE")
            else:
                self.SendNackAndClose(ws, messageType, "Invalid PASSWORD")



    ######################################################################
    #
    # Implementing WSNodeMgr Events
    #
    ######################################################################

    def OnWebSocketConnectedInbound(self, ws):
        # I don't care
        pass

    def OnWebSocketReadable(self, ws, userData):
        msg = ws.Read()

        if self.IsClientKnown(ws):
            self.HandleClientMsg(ws, msg)
        else:
            self.HandleNewLogin(ws, msg)

    def OnWebSocketClosed(self, ws, userData):
        if self.IsClientKnown(ws):
            self.HandleClientDisconnect(ws)
        else:
            # I don't care
            pass

    def OnWebSocketError(self, ws, userData):
        Log("WebSocketError: Why did this happen?")



def Main():
    if len(sys.argv) != 5:
        print("Usage: " +
              sys.argv[0] +
              " <port> <wsPath> <localDirAsWebRoot> <password>")
        sys.exit(-1)

    port              = sys.argv[1]
    wsPath            = sys.argv[2]
    localDirAsWebRoot = sys.argv[3]
    password          = sys.argv[4]

    handler   = RDVPServer(password)
    wsNodeMgr = WSNodeMgr(handler)

    Log("RDVP Server Starting")
    wsNodeMgr.listen(port, wsPath, localDirAsWebRoot)

    evm_MainLoop()


Main()

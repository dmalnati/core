import os
import time

import json

from libWebSocket import *
from libEvm import *


###############################################################################
#
# This is the WS interface.
#
# Enhances and simplifies basic WebSocket interface.
#
# Supports
# - JSON message passing, only.
# - Client sends ID on connect
# - auto-retry connect
# - event interface changes
#
#
#
# Classes defined here:
#
#
# WSEventHandler
# - Inherit from this (or duck-type) as a handler for events
#
#
# WS
# - Represents a connection, either inbound or outbound.
# - Cannot create yourself, must use WSManager
# - When connecting outbound, auto-sends first message identifying itself
#
#
# WSManager
# - Central place to acquire new inbound or outbound links
# - Keeps track of all links
# - Must be only one of these
# - Required for any WS usage
#
#
#
# A client will:
# - wsm = WSManager(id)
# - ws = wsm.Connect(handler, addr) 
# - deal with OnX events
#
# A server will:
# - wsm = WSManager(id)
# - wsm.Listen(WSConnectionReceivedEventHandler, ...)
# - OnWSConnectIn(ws)
#     hand off to something, do whatever actions a server does now
#     ws.SetHandler(WSEventHandler)
#
#
#
###############################################################################


class WSEventHandler():
    def __init__(self):
        pass
        
    def OnConnect(self, ws):
        pass

    def OnMessage(self, ws, msg):
        pass

    def OnClose(self, ws):
        pass

    # auto re-connects
    def OnError(self, ws):
        pass

        
        
class WSConnectionReceivedEventHandler():
    def OnWSConnectIn(self, ws):
        # ws.SetHandler(...)
        # followed by getting the relevant WebSocketEventHandler events
        pass
        
        
        
        
        
###############################################################################
#
# WS is the type to be passed around representing a connection.
#
# These can only be created by WSManager.
#
# Messages pass through are JSON only.
#
###############################################################################

class WS(WebSocketEventHandler):
    def __init__(self, wsManager, inOut, handler = None):
        self.wsManager = wsManager
        self.inOut     = inOut
        self.handler   = handler
        self.webSocket = None
    
    #############################
    # Public
    #############################
    
    def SetHandler(self, handler):
        self.handler = handler
    
    def Connect(self):
        self.webSocket.Connect()
    
    def ConnectCancel(self):
        self.webSocket.ConnectCancel()

    def Write(self, msg):
        try:
            self.webSocket.Write(json.dumps(msg))
        except Exception as e:
            pass

    def Close(self):
        self.webSocket.Close()
        
        if self.inOut == "IN":
            self.wsManager.OnWSCloseInbound(self)
        if self.inOut == "OUT":
            self.wsManager.OnWSCloseOutbound(self)
        
    def DumpMsg(self, msg):
        print(json.dumps(msg,
                        sort_keys=True,
                        indent=4,
                        separators=(',', ': ')))
    
    
    def SendAbort(self, reason):
        try:
            self.Write({
                "SESSION_ACTION": "ABORT",
                "ID"            : str(self.wsManager.id),
                "MESSAGE_TYPE"  : "ERROR",
                "REASON"        : reason,
            })
            self.webSocket.Close()
        except Exception as e:
            pass

        
    #############################
    # Implementing WebSocketEventHandler
    #############################

    def OnConnect(self, webSocket):
        self.Write({
            "SESSION_ACTION" : "NEW",
            "ID"             : str(self.wsManager.id),
        })
        
        # this event can only happen to outbound
        self.wsManager.OnWSConnectOutbound(self)

        if self.handler:
            self.handler.OnConnect(self)

    def OnMessage(self, webSocket, buf):
        try:
            msg = json.loads(buf)
            if self.handler:
                self.handler.OnMessage(self, msg)
        except:
            pass

    def OnClose(self, webSocket):
        if self.inOut == "IN":
            self.wsManager.OnWSCloseInbound(self)
        if self.inOut == "OUT":
            self.wsManager.OnWSCloseOutbound(self)
        
        if self.handler:
            self.handler.OnClose(self)

    def OnError(self, webSocket):
        if self.handler:
            self.handler.OnError(self)
        evm_SetTimeout(self.Connect, 5000)

    #############################
    # Private
    #############################
    
    def SetWebSocket(self, webSocket):
        self.webSocket = webSocket

    
    
    
    

class WSManager(WebSocketManager,
                WebSocketConnectionReceivedEventHandler):
    def __init__(self, id):
        WebSocketManager.__init__(self)
        
        self.id = id
        
        self.wsOutbound__data = dict()
        self.wsInbound__data  = dict()
        
        self.listenHandler = None
        
        
    def GetWSInboundList(self):
        return self.wsInbound__data.keys()
        
    def GetWSOutboundList(self):
        return self.wsOutbound__data.keys()
        
        
    #############################
    # Mocking WebSocketManager interface
    #############################

    def Connect(self, handler, url):
        ws = WS(self, "OUT", handler)
        webSocket = WebSocketOutbound(ws, url)
        ws.SetWebSocket(webSocket)
        ws.Connect()
        
        return ws

    def ConnectCancel(self, handle):
        ws = handle
        ws.ConnectCancel()
    
    
    #
    # Really we want to absorb all the updates for the listen sockets into the
    # main class, but we can't, because further-inherited children may want
    # to do the same thing, and then they'd intercept these lower-level
    # events.
    #
    # So we make a class to the side, have an instance, and let it twiddle the
    # internals of this class.
    #
    class ListenSnooper(WebSocketEventHandler):
        def __init__(self, wsManager):
            self.wsManager = wsManager
    
        def OnConnect(self, webSocket):
            
            # here we intercept incoming connections so we can get a look at
            # them beforehand.
            
            # tell this websocket to call us back until we choose to propigate to
            # the upper layers
            
            # the methods below are how we keep track of these websockets
            webSocket.SetHandler(self)
        
        def OnMessage(self, webSocket, buf):
            ok = True
            try:
                msg = json.loads(buf)
                err = False
            except:
                self.wsManager.SendAbortToWebSocket(webSocket, "MESSAGE NOT JSON")
                ok = False
            
            if ok:
                # validate all the right stuff
                if "SESSION_ACTION" in msg and "ID" in msg:
                    sessionAction = msg["SESSION_ACTION"]
                    id            = msg["ID"]
                    
                    if sessionAction == "NEW" and id != "":
                        # good to go, time to pass upward
                        
                        # intercept incoming connections so we can get a look at
                        # them beforehand.
                        # create our own ws object which notifies us
                        ws = WS(self.wsManager, "IN")
                        ws.SetWebSocket(webSocket)
                        
                        # propigate events from webSocket up to WS
                        webSocket.SetHandler(ws)
                        
                        # keep track of this socket
                        self.wsManager.OnWSConnectInbound(ws)
                        
                        # tell the upper layer
                        self.wsManager.listenHandler.OnWSConnectIn(ws)
                    else:
                        err = True
                else:
                    err = True
                    
                if err:
                    self.wsManager.SendAbortToWebSocket(webSocket, "MANDATORY PROTOCOL FIELDS MISSING OR INVALID")
            else:
                pass
            
        def OnClose(self, webSocket):
            pass

        def OnError(self, webSocket):
            pass
        
        
    def Listen(self, handler, port, wsPath):
        self.listenHandler = handler
        
        snooper = WSManager.ListenSnooper(self)
        
        WebSocketManager.Listen(self, snooper, port, wsPath)
        
        
        
        
        
    
    #############################
    # Private
    #############################
    
    #############################
    # WebSocketConnectionReceivedEventHandler
    #############################


    def SendAbortToWebSocket(self, webSocket, msg):
        # WS objects can abort, but webSockets can't.
        # So make a WS just to abort it.
        webSocket.SetHandler(None)
        ws = WS(self, "-")
        ws.SetWebSocket(webSocket)
        ws.SendAbort(msg)
        
    
    
    
    
    
    
    #############################
    # Noticing outbound events
    #############################

    def OnWSConnectOutbound(self, ws):
        self.wsOutbound__data[ws] = True
    
    def OnWSCloseOutbound(self, ws):
        self.wsOutbound__data.pop(ws)
    
    
    
    #############################
    # Noticing inbound events
    #############################
    
    def OnWSConnectInbound(self, ws):
        self.wsInbound__data[ws] = True
    
    def OnWSCloseInbound(self, ws):
        self.wsInbound__data.pop(ws)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
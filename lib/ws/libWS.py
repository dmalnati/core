import os
import time
import inspect

import json

from libWebService import *
from libEvm import *


###############################################################################
#
# This is the WS interface.
#
# Enhances and simplifies basic WebService/WebSocket interface.
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
#     or deal with the events itself
#
#
#
###############################################################################


class WSConnectionReceivedEventHandler():
    def OnWSConnectIn(self, ws):
        # ws.SetHandler(...)
        # followed by getting the relevant WebSocketEventHandler events
        # or deal with the events itself
        pass
        


class WSEventHandler(WSConnectionReceivedEventHandler):
    # for outbound only
    def OnConnect(self, ws):
        pass

    def OnMessage(self, ws, msg):
        pass

    def OnClose(self, ws):
        pass

    # auto re-connects outbound only
    def OnError(self, ws):
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
        self.special   = False
    
    #############################
    # Public
    #############################
    
    def SetSpecial(self, special):
        self.special = special
    
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
        if self.inOut == "IN_NON_PRIMARY":
            self.wsManager.OnWSNonPrimaryCloseInbound(self)
        
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
        if self.special:
            self.Write({
                "SESSION_TYPE"   : "SPECIAL",
                "SESSION_ACTION" : "NEW",
                "ID"             : str(self.wsManager.id),
            })
        else:
            self.Write({
                "SESSION_TYPE"   : "NORMAL",
                "SESSION_ACTION" : "NEW",
                "ID"             : str(self.wsManager.id),
            })
        
        # this event can only happen to outbound
        self.wsManager.OnWSConnectOutbound(self)

        if self.handler:
            self.handler.OnConnect(self)

    def OnMessage(self, webSocket, buf):
        msg = None
        try:
            msg = json.loads(buf)
        except:
            self.SendAbort("MESSAGE NOT JSON")
        
        if msg and self.handler:
            self.handler.OnMessage(self, msg)

    def OnClose(self, webSocket):
        if self.inOut == "IN":
            self.wsManager.OnWSCloseInbound(self)
        if self.inOut == "OUT":
            self.wsManager.OnWSCloseOutbound(self)
        if self.inOut == "IN_NON_PRIMARY":
            self.wsManager.OnWSNonPrimaryCloseInbound(self)
        
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

    
    
    
    

class WSManager(WebServiceManager,
                WebSocketConnectionReceivedEventHandler):
    def __init__(self, id):
        WebServiceManager.__init__(self)
        
        self.id = id
        
        self.wsOutbound__data = dict()
        self.wsInbound__data  = dict()
        self.wsInboundNonPrimary__data = dict()
        
        self.specialSessionHandler = WSManager.SpecialSessionHandler(self)
        self.shutdownHandler       = self
        
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
                if "SESSION_TYPE" in msg and "SESSION_ACTION" in msg and "ID" in msg:
                    sessionType   = msg["SESSION_TYPE"]
                    sessionAction = msg["SESSION_ACTION"]
                    id            = msg["ID"]
                    
                    if sessionType == "SPECIAL":
                        self.wsManager.OnSpecialSession(webSocket, msg)
                    elif sessionAction == "NEW" and id != "":
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
                        
                        # Set the handler to handle the ws events also if it
                        # seems to be capable, otherwise leave unset, meaning
                        # the events will be handled at a lower level but not
                        # propigate upward.
                        if self.wsManager.CapableOfWSEventHandler(self.wsManager.listenHandler):
                            ws.SetHandler(self.wsManager.listenHandler)
                        
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
        
    
    # this is for primary service communication purposes.
    # any supplemental websocket or web service handlers will not be
    # managed specifically by this library
    def Listen(self, handler, port, wsPath):
        self.listenHandler = handler
        
        snooper = WSManager.ListenSnooper(self)
        
        portListening = WebServiceManager.Listen(self, port)
        
        WebServiceManager.AddWebSocketListener(self, snooper, wsPath)
        
        return portListening
    
    
    
    # this is for arbitrary additional ws listeners
    def AddWSListener(self, handler, wsPath):
        # keep track of them, separate from normal service
        # enforce json
        # don't require initial message passing, message structure, etc
        
        class NonPrimaryWSListener():
            def __init__(self, wsManager, listenHandler):
                self.wsManager     = wsManager
                self.listenHandler = listenHandler
                
            def OnConnect(self, webSocket):
                ws = WS(self.wsManager, "IN_NON_PRIMARY")
                ws.SetWebSocket(webSocket)
                webSocket.SetHandler(ws)
                
                # keep track of this socket
                self.wsManager.OnWSNonPrimaryConnectInbound(ws)
                
                # tell the upper layer
                if self.wsManager.CapableOfWSEventHandler(self.listenHandler):
                    ws.SetHandler(self.listenHandler)
                    
                self.listenHandler.OnWSConnectIn(ws)
        
        handlerNonPrimary = NonPrimaryWSListener(self, handler)
        
        return WebServiceManager.AddWebSocketListener(self, handlerNonPrimary, wsPath)
        
        
    
    
    class SpecialSessionHandler():
        def __init__(self, wsManager):
            self.wsManager = wsManager
            
            self.ws__data = dict()
    
        def AddSpecialSession(self, webSocket, msg):
            # create our own ws object which notifies us
            ws = WS(self, "-")
            ws.SetWebSocket(webSocket)
            
            # propigate events from webSocket up to WS
            webSocket.SetHandler(ws)
            
            # have the WS conact me for messaging
            ws.SetHandler(self)
            
            # keep track of special sessions
            self.ws__data[ws] = msg
            
            
        def OnMessage(self, ws, msg):
            if "COMMAND" in msg:
                command = msg["COMMAND"]
                
                if command == "KILL":
                    ws.Write({
                        "REPLY" : "ACK",
                    })
                    evm_MainLoopFinish()
                elif command == "SHUTDOWN":
                    ws.Write({
                        "REPLY" : "ACK",
                    })
                    self.wsManager.shutdownHandler.OnShutdown()
                else:
                    ws.Write({
                        "REPLY" : "NACK",
                    })

        def OnClose(self, ws):
            self.ws__data.pop(ws)

    
    
    def OnSpecialSession(self, webSocket, msg):
        self.specialSessionHandler.AddSpecialSession(webSocket, msg)
        
    def OnShutdown(self):
        Log("SHUTDOWN received, doing nothing")
    
    #############################
    # Private
    #############################
    
    def CapableOfWSEventHandler(self, handler):
        retVal = True
        
        # list of tuples (fnName, code)
        eventHandlerMemberList = inspect.getmembers(WSEventHandler(), predicate=inspect.ismethod)
        handlerMemberList = inspect.getmembers(handler, predicate=inspect.ismethod)
    
        # build list of fnNames in event handler
        eventHandlerFnList = []
        for member in eventHandlerMemberList:
            fnName = member[0]
            eventHandlerFnList.append(fnName)
        
        # build list of fnNames in handler
        handlerFnList = []
        for member in handlerMemberList:
            fnName = member[0]
            handlerFnList.append(fnName)    
        
        # check all necessary exist
        for fn in eventHandlerFnList:
            if fn not in handlerFnList:
                retVal = False
        
        return retVal
    
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
        if ws in self.wsOutbound__data:
            self.wsOutbound__data.pop(ws)
        else:
            Log("ERR: OnWSCloseOutbound ws closed but not in list")
    
    
    
    #############################
    # Noticing inbound events
    #############################
    
    def OnWSConnectInbound(self, ws):
        self.wsInbound__data[ws] = True
    
    def OnWSCloseInbound(self, ws):
        if ws in self.wsInbound__data:
            self.wsInbound__data.pop(ws)
        else:
            Log("ERR: OnWSCloseInbound ws closed but not in list")
        
        
    #############################
    # Noticing non-primary inbound events
    #############################
    
    def OnWSNonPrimaryConnectInbound(self, ws):
        self.wsInboundNonPrimary__data[ws] = True
    
    def OnWSNonPrimaryCloseInbound(self, ws):
        if ws in self.wsInboundNonPrimary__data:
            self.wsInboundNonPrimary__data.pop(ws)
        else:
            Log("ERR: OnWSNonPrimaryCloseInbound ws closed but not in list")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

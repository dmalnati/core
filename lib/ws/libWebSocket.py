import os
import time

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from tornado import gen


from libUtl import *


###############################################################################
#
# Represents primitive socket-like behavior of WebSockets
#
# Classes defined here:
#
#
# WebSocketEventHandler
# - Inherit from this (or duck-type) as a handler for events
#
#
# WebSocketReceivedEventHandler
# - If you call Listen on WebSocketManager, provide one of these to receive
#   the websockets as they come in
#
# WebSocketConnectionReceivedEventHandler
# - This is what you have to do when you call Listen
#
#
# WebSocketOutbound
# - an instance of an outbound websocket
# - feel free to use independely of anything else
#
# WebSocketInbound
# - an instance of an inbound websocket
#
#
# WebSocketManager
# - Gets you access to a central place to acquire outbound and inbound
#   WebSockets
# - Must be only be one of these
# - Not required if only using outbound WebSockets
#
#
# 
# A client will:
# - ws = WebSocketOutbound(WebSocketEventHandler, ...)
# - ws.Connect() 
# - deal with OnX events
#
# A server will:
# - WebSocketManager.Listen(WebSocketConnectionReceivedEventHandler, ...)
# - OnConnect(ws)
#     hand off to something, do whatever actions a server does now
#     ws.SetHandler(WebSocketEventHandler)
#
#
#
###############################################################################


###############################################################################
#
# Event Interface
#
###############################################################################

class WebSocketEventHandler():
    def OnConnect(self, ws):
        pass

    def OnMessage(self, ws, msg):
        pass

    def OnClose(self, ws):
        pass

    def OnError(self, ws):
        pass


class WebSocketConnectionReceivedEventHandler():
    def OnConnect(self, ws):
        # ws.SetHandler(...)
        # followed by getting the relevant WebSocketEventHandler events
        pass
        
        
        

###############################################################################
#
# WebSocket Object Interfaces
# Inbound is a subset of outbound
#   All that's different is Inbound doesn't have a Connect() function
#
###############################################################################

class WebSocketOutbound():
    def __init__(self, handler, url):
        self.handler   = handler
        self.url       = url
        self.conn      = None
        self.cancelled = False

        
    #############################
    # Public
    #############################
    
    def SetHandler(self, handler):
        self.handler = handler

    def Connect(self):
        WebSocketOutbound.ConnectPrivate(self, self.url)

    def ConnectCancel(self):
        self.cancelled = True

    def Write(self, msg):
        self.conn.write_message(msg)

    def Close(self):
        self.conn.close()
    
    
    #############################
    # Private
    #############################

    def OnConnect(self):
        self.handler.OnConnect(self)

    def OnMessage(self, msg):
        self.handler.OnMessage(self, msg)

    def OnClose(self):
        self.handler.OnClose(self)

    def OnError(self):
        self.handler.OnError(self)


    @staticmethod
    @gen.coroutine
    def ConnectPrivate(ws, url):
        try:
            fut = tornado.websocket.websocket_connect(url)
            conn = yield fut
        except Exception as e:
            if not ws.cancelled:
                ws.OnError()
            return

        if ws.cancelled:
            conn.close()
            return

        ws.set_conn(conn)
        ws.OnConnect()

        while True:
            msg = yield conn.read_message()
            if msg is None:
                ws.OnClose()
                break
            ws.OnMessage(msg)

    # basically a private function to be called by Connect
    def set_conn(self, conn):
        self.conn = conn

        

class WebSocketInbound():
    def __init__(self, wsInboundRecieverInstance):
        self.wsInboundRecieverInstance = wsInboundRecieverInstance
        
        self.handler = None

    #############################
    # Public
    #############################

    def SetHandler(self, handler):
        self.handler = handler
    
    def Write(self, msg):
        self.wsInboundRecieverInstance.write_message(msg)

    def Close(self):
        self.wsInboundRecieverInstance.close()
    
    
    #############################
    # Private
    #############################

    def OnMessage(self, msg):
        if self.handler:
            self.handler.OnMessage(self, msg)

    def OnClose(self):
        if self.handler:
            self.handler.OnClose(self)


            

###############################################################################
#
# Private class, ignore
#
###############################################################################
        
        
# Handler class will hold the single callback to distribute events,
# the individual instances will come alive to handle each new 
# inbound WebSocket
class WebSocketInboundReceiver(tornado.websocket.WebSocketHandler):
    def initialize(self, **key__value):
        self.handlerOnOpen = key__value["handlerOnOpen"]
        self.handlerWebSocketEvent = None
    
    #############################
    # Private
    #############################

    def check_origin(self, origin):
        return True

    def open(self):
        self.set_nodelay(True)
        
        ws = WebSocketInbound(self)
        
        self.handlerWebSocketEvent = ws;
        
        self.handlerOnOpen.OnConnect(ws)

    def on_message(self, msg):
        self.handlerWebSocketEvent.OnMessage(msg)

    def on_close(self):
        self.handlerWebSocketEvent.OnClose()

        
        
        
        
        
        
        
        
###############################################################################
#
# Public class
#
###############################################################################

class WebSocketManager():
    def __init__(self):
        self.webApp = None

    # can only do this once
    def Listen(self, handler, port, wsPath):
        retVal = 0

        if not self.webApp:
            handlerList = [
                (wsPath, WebSocketInboundReceiver, dict(handlerOnOpen=handler))
            ]

            # Create the web App
            self.webApp = tornado.web.Application(handlerList)

            # Continue with init
            socketList = tornado.netutil.bind_sockets(port)
            httpServer = tornado.httpserver.HTTPServer(self.webApp)
            httpServer.add_sockets(socketList)

            listeningPort = socketList[0].getsockname()[1]
            retVal = listeningPort


        else:
            retVal = 0

        return retVal








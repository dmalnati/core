#!/usr/bin/python


import time

from collections import deque

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from tornado import gen


'''
This is the WebSocket interface the users of a WSNodeMgr will have.
They will additionally be given events associated with a particular ws.
No instances of this class should be instantiated by an end user.
'''
class WSIface():
    # private
    def SetMessage(self, msg):
        self.msg = msg

    def GetMessage(self):
        return self.msg

    # public
    def __init__(self, id, userData):
        self.SetUserData(userData)
        self.SetMessage("")
        self.id = id
        self.timeFirstConnected = time.time()

    def GetId(self):
        return self.id

    def GetTimeFirstConnected(self):
        return self.timeFirstConnected

    def GetTimeDurationConnectedSecs(self):
        return time.time() - self.GetTimeFirstConnected()

    def SetUserData(self, userData):
        self.userData = userData

    def GetUserData(self):
        return self.userData

    def Read(self):
        msg = self.GetMessage()
        self.SetMessage("")
        return msg

    def Write(self, msg):
        self.write_message(msg)

    def Close(self):
        self.close()


'''
This is the  event handler interface users of a WSNodeMgr will implement.
'''
class WSNodeMgrEventHandlerIface():
    def __init__(self):
        self.wsListInbound  = deque()
        self.wsListOutbound = deque()

    def OnWebSocketConnectedInbound(self, ws):
        pass
    def OnWebSocketConnectedOutbound(self, ws, userData):
        pass
    def OnWebSocketReadable(self, ws, userData):
        pass
    def OnWebSocketClosed(self, ws, userData):
        pass
    def OnWebSocketError(self, ws, userData):
        pass

    # private
    def AddWebSocketInbound(self, ws):
        self.wsListInbound.append(ws)
    def RemWebSocketInbound(self, ws):
        try:
            self.wsListInbound.remove(ws)
        except:
            pass
    def AddWebSocketOutbound(self, ws):
        self.wsListOutbound.append(ws)
    def RemWebSocketOutbound(self, ws):
        try:
            self.wsListOutbound.remove(ws)
        except:
            pass
    def GetWebSocketInboundList(self):
        return self.wsListInbound
    def GetWebSocketOutboundList(self):
        return self.wsListOutbound
    def GetCountWebSocketInbound(self):
        return len(self.wsListInbound)
    def GetCountWebSocketOutbound(self):
        return len(self.wsListOutbound)
    def GetCountWebSocketAll(self):
        return self.GetCountWebSocketInbound() + \
               self.GetCountWebSocketOutbound()
    def LogState(self):
        print("Count Inbound : " + str(self.GetCountWebSocketInbound()))
        print("Count Outbound: " + str(self.GetCountWebSocketOutbound()))
        print("Count All     : " + str(self.GetCountWebSocketAll()))



'''
Manages creation of new WebSockets.
Handles connecting outwardly, and receiving inwardly.
In both directions, a single simple class interface is used for the websockets
returned.

There can be only one instance of a node manager.
'''
class WSNodeMgr():
    def __init__(self, handler):
        self.handler = handler
        self.webApp = None

    def connect(self, url, userData):
        mwso = ManagedWSOutbound(url, self.handler, userData)
        mwso.connect()
        return True

    # can only do this once
    def listen(self, port, path):
        retVal = True

        if not self.webApp:
            ManagedWSInbound.SetHandler(self.handler)

            self.webApp = tornado.web.Application([
                (path, ManagedWSInbound)
            ])

            httpServer = tornado.httpserver.HTTPServer(self.webApp)
            httpServer.listen(port)
        else:
            retVal = False

        return retVal





##########################################################################
#
# Implementation details, including interacing with Tornado
#
##########################################################################


class ManagedWSInbound(tornado.websocket.WebSocketHandler, WSIface):
    HANDLER = None
    COUNT   = 0

    @classmethod
    def GetNextId(cls):
        cls.COUNT += 1
        return "Inbound #" + str(cls.COUNT)

    @classmethod
    def SetHandler(cls, handler):
        cls.HANDLER = handler

    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self,
                                            application,
                                            request,
                                            **kwargs)
        WSIface.__init__(self, ManagedWSInbound.GetNextId(), None)

        # seems to break on ubuntu without this, despite running 4.1 ...
        if hasattr(self, "_on_close_called") == False:
            self._on_close_called = False

        # and one spotted on raspberry pi ...
        if hasattr(self, "close_code") == False:
            self.close_code = False

    def open(self):
        ManagedWSInbound.HANDLER.AddWebSocketInbound(self)
        ManagedWSInbound.HANDLER.OnWebSocketConnectedInbound(self)

    def on_message(self, msg):
        self.SetMessage(msg)
        ManagedWSInbound.HANDLER.OnWebSocketReadable(self, self.GetUserData())

    def on_close(self):
        ManagedWSInbound.HANDLER.RemWebSocketInbound(self)
        ManagedWSInbound.HANDLER.OnWebSocketClosed(self, self.GetUserData())




'''
Adapter around Tornado outbound websocket interface.
Leads to objects which get callbacks sent to themselves.
Must inherit from this class as it does nothing by itself.
'''
class WSOutbound():
    @staticmethod
    @gen.coroutine
    def Connect(ws, url):
        try:
            conn = yield tornado.websocket.websocket_connect(url)
        except:
            ws.on_error()
            return

        ws.set_conn(conn)
        ws.on_connect()

        while True:
            msg = yield conn.read_message()
            if msg is None:
                ws.on_close()
                break
            ws.on_message(msg)

    def __init__(self, url):
        self.url  = url
        self.conn = None

    # basically a private function to be called by Connect
    def set_conn(self, conn):
        self.conn = conn

    def connect(self):
        WSOutbound.Connect(self, self.url)

    def close(self):
        self.conn.close()

    def on_connect(self):
        pass

    def on_message(self, msg):
        pass

    def on_close(self):
        pass

    def on_error(self):
        pass



'''
Test class
'''
class WSOutboundTest(WSOutbound):
    def __init__(self, url):
        WSOutbound.__init__(self, url)

    def on_connect(self):
        print("on_connect")

    def on_message(self, msg):
        print("on_message")

    def on_close(self):
        print("on_close")

    def on_error(self):
        print("on_error")


'''
Class to help achieve the interface of the WSNodeMgr and callback behavior.
WSNodeMgr will use this with knowledge of how it works.
External consumers will perceive this as a WSIface object.
'''
class ManagedWSOutbound(WSOutbound, WSIface):
    COUNT = 0

    @classmethod
    def GetNextId(cls):
        cls.COUNT += 1
        return "Outbound #" + str(cls.COUNT)

    def __init__(self, url, handler, userData):
        WSOutbound.__init__(self, url)
        WSIface.__init__(self, ManagedWSOutbound.GetNextId(), userData)

        self.handler = handler

    def on_connect(self):
        self.handler.AddWebSocketOutbound(self)
        self.handler.OnWebSocketConnectedOutbound(self, self.GetUserData())

    def on_message(self, msg):
        self.SetMessage(msg)
        self.handler.OnWebSocketReadable(self, self.GetUserData())

    def on_close(self):
        self.handler.RemWebSocketOutbound(self)
        self.handler.OnWebSocketClosed(self, self.GetUserData())

    def on_error(self):
        self.handler.OnWebSocketError(self, self.GetUserData())





















import os
import time

import json

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

    def SetSuppressEvents(self, val):
        self.suppressEvents = val

    def GetSuppressEvents(self):
        return self.suppressEvents

    # public
    def __init__(self, id, userData):
        self.SetUserData(userData)
        self.SetMessage("")
        self.SetSuppressEvents(False)
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
        self.SetSuppressEvents(True)
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
    def OnWebSocketConnectedOutbound(self, ws):
        pass
    def OnWebSocketReadable(self, ws):
        pass
    def OnWebSocketClosed(self, ws):
        pass
    def OnWebSocketError(self, ws):
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

    def connect(self, url, userData=None):
        mwso = ManagedWSOutbound(url, self.handler, userData)
        mwso.connect()
        return mwso

    def connect_cancel(self, handle):
        mwso = handle
        mwso.connect_cancel()

    # can only do this once
    def listen(self, port, wsPath = "/ws", localDirAsWebRoot=None, sslOptions=None):
        retVal = True

        if not self.webApp:
            ManagedWSInbound.SetHandler(self.handler)

            # unconditionally support websocket handler
            handlerList = [
                (wsPath, ManagedWSInbound)
            ]

            # conditionally support http
            if localDirAsWebRoot:
                handlerList.append(
                    (r"/(.*)",
                     tornado.web.StaticFileHandler,
                     {
                        "path" : localDirAsWebRoot
                     }
                    )
                )

            self.webApp = tornado.web.Application(handlerList)

            httpServer = tornado.httpserver.HTTPServer(self.webApp)
            httpServer.listen(port)

            if sslOptions:
                sslPort     = sslOptions["sslPort"]
                sslCertFile = sslOptions["sslCertFile"]
                sslKeyFile  = sslOptions["sslKeyFile"]

                sslHttpServer = tornado.httpserver.HTTPServer(self.webApp,
                                                              ssl_options={
                    "certfile" : sslCertFile,
                    "keyfile"  : sslKeyFile
                })

                sslHttpServer.listen(sslPort)

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

    def check_origin(self, origin):
        return True

    def open(self):
        self.set_nodelay(True)

        ManagedWSInbound.HANDLER.AddWebSocketInbound(self)
        if not self.GetSuppressEvents():
            ManagedWSInbound.HANDLER.OnWebSocketConnectedInbound(self)

    def on_message(self, msg):
        self.SetMessage(msg)
        if not self.GetSuppressEvents():
            ManagedWSInbound.HANDLER.OnWebSocketReadable(self)

    def on_close(self):
        ManagedWSInbound.HANDLER.RemWebSocketInbound(self)
        if not self.GetSuppressEvents():
            ManagedWSInbound.HANDLER.OnWebSocketClosed(self)




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
            fut = tornado.websocket.websocket_connect(url)
            conn = yield fut
        except:
            if not ws.cancelled:
                ws.on_error()
            return

        if ws.cancelled:
            conn.close()
            return

        ws.set_conn(conn)
        ws.on_connect()

        while True:
            msg = yield conn.read_message()
            if msg is None:
                ws.on_close()
                break
            ws.on_message(msg)

    # basically a private function to be called by Connect
    def set_conn(self, conn):
        self.conn = conn

    def __init__(self, url):
        self.url  = url
        self.conn = None
        self.cancelled = False

    def connect(self):
        WSOutbound.Connect(self, self.url)

    def connect_cancel(self):
        self.cancelled = True

    def write_message(self, msg):
        self.conn.write_message(msg)

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
        if not self.GetSuppressEvents():
            self.handler.OnWebSocketConnectedOutbound(self)

    def on_message(self, msg):
        self.SetMessage(msg)
        if not self.GetSuppressEvents():
            self.handler.OnWebSocketReadable(self)

    def on_close(self):
        self.handler.RemWebSocketOutbound(self)
        if not self.GetSuppressEvents():
            self.handler.OnWebSocketClosed(self)

    def on_error(self):
        if not self.GetSuppressEvents():
            self.handler.OnWebSocketError(self)


##########################################################################
#
# Convenience Application Interface
#
##########################################################################

class WSApp(WSNodeMgrEventHandlerIface, WSNodeMgr):
    def __init__(self, serviceOrPort = None):
        WSNodeMgrEventHandlerIface.__init__(self)
        WSNodeMgr.__init__(self, self)
        
        self.serviceOrPort = serviceOrPort
        
        self.service__data = dict()
        self.ok = self.ReadServiceDirectory()
        
        self.service = None
        self.port    = None
        if self.serviceOrPort:
            self.service, self.port = self.LookupService(self.serviceOrPort)
            
            if self.service == None or self.port == None:
                self.ok = None
        else:
            self.service = "SERVICE_%s" % str(os.getpid())
        
    def IsOk(self):
        return self.ok
        
    def GetServiceAndPort(self):
        return self.service, self.port
        
    def Listen(self):
        if self.IsOk():
            data = self.GetServiceData(self.service)
            
            self.listen(data["port"], data["wsPath"])
    
    def Connect(self, serviceOrAddrOrPort):
        handle = None
        
        isAddr = False
        try:
            if serviceOrAddrOrPort.index("ws://") == 0:
                isAddr = True
        except:
            pass
            
        if isAddr:
            addr   = serviceOrAddrOrPort
            handle = self.connect(addr)
        else:
            service, port = self.LookupService(serviceOrAddrOrPort)
            
            if service:
                addr   = self.GetServiceAddr(service)
                handle = self.connect(addr)
            elif port:
                addr   = "ws://127.0.0.1:%s/ws" % port
                handle = self.connect(addr)
            
        return handle
    
    def ReadServiceDirectory(self):
        ok = True
        
        with open('WSServices.txt', 'r') as file:
            fileData = file.read().rstrip('\n')
        
            lineList = fileData.split("\n")
            
            for line in lineList:
                line = line.strip()
                
                if len(line):
                    if line[0] != "#":
                        linePartList = line.split(" ")
                        
                        if len(linePartList) == 4:
                            service = linePartList[0]
                            host    = linePartList[1]
                            port    = linePartList[2]
                            wsPath  = linePartList[3]
                            
                            data = {
                                "service" : service,
                                "host"    : host,
                                "port"    : port,
                                "wsPath"  : wsPath,
                                "addr"    : "ws://" + host + ":" + port + wsPath,
                            }
                            
                            if service in self.service__data:
                                ok = False
                            else:
                                self.service__data[service] = data
        
        return ok
    
    # pass in either a service name or port
    #
    # if service name:
    #   and found -- return set service and port
    #   not found -- service is set
    #
    # if port:
    #   and found -- bad, that's a clash
    #     return service name = None, port = port
    #   not found -- good, not a clash
    #     return synthetic service name and the port passed in
    #
    # So basically:
    # - success is when both service and port are set
    # - if only service set, no port could be found
    # - if only port set, it's a port conflict
    #
    def LookupService(self, serviceOrPort):
        service = None
        port    = None
        
        if not serviceOrPort.isdigit():
            if serviceOrPort in self.service__data:
                data = self.service__data[serviceOrPort]
                
                service = serviceOrPort
                port    = data["port"]
            else:
                service = serviceOrPort
        else:
            for tmpService in self.service__data.keys():
                data = self.service__data[tmpService]
                tmpPort = data["port"]
                
                if tmpPort == serviceOrPort:
                    port = tmpPort
            
            if not port:
                service = "SERVICE:%s" % serviceOrPort
                port    = serviceOrPort
    
        return service, port

    def GetServiceAddr(self, service):
        addr = None
        
        if service in self.service__data:
            data = self.service__data[service]
            addr = "ws://" + data["host"] + ":" + data["port"] + data["wsPath"]
        
        return addr


    def GetServiceData(self, service):
        data = None
        
        if service in self.service__data:
            data = self.service__data[service]
            
        return data











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

    def ReadRaw(self):
        msg = self.GetMessage()
        self.SetMessage("")
        return msg

    def WriteRaw(self, msg):
        self.write_message(msg)

    def Read(self):
        buf = self.ReadRaw()
        try:
            jsonObj = json.loads(buf)
        except:
            jsonObj = json.loads("{}")

        msg = jsonObj
        return msg

    def Write(self, msg):
        self.WriteRaw(json.dumps(msg))

    def Close(self):
        self.SetSuppressEvents(True)
        self.close()

    def DumpMsg(self, msg):
        print(json.dumps(msg,
                         sort_keys=True,
                         indent=4,
                         separators=(',', ': ')))
 


        
        


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

    def connect(self, url, userData=None, handler=None):
        handlerToPass = self.handler
        if handler:
            handlerToPass = handler

        mwso = ManagedWSOutbound(url, handlerToPass, userData)
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
        
        self.service__data = dict()
        self.serviceData = None

        self.ok = self.ReadServiceDirectory()

        # On startup, a WSApp will init.
        # Servers will identify their service name or port.
        # Clients won't.
        #
        # If we're a server, we want to identify our own service details so
        # when the server tries to Listen later, it has its details sorted

        if serviceOrPort:
            # Maybe the name of a service
            if not self.serviceData:
                self.serviceData = self.LookupServiceByName(serviceOrPort)
                
            # Or maybe the port of a service
            if not self.serviceData:
                self.serviceData = self.LookupServiceByPort(serviceOrPort)

            # Or maybe just a port not defined, so we make up an address
            if not self.serviceData:
                if serviceOrPort.isdigit():
                    self.serviceData = \
                        self.MakeServiceDataByPort(serviceOrPort)
        else:
            self.serviceData = self.MakeServiceDataClient()
        

    def IsOk(self):
        return self.ok

    def GetSelfServiceData(self):
        return self.serviceData
        

    def Listen(self):
        if self.IsOk():
            self.listen(self.serviceData["port"], self.serviceData["wsPath"])

    
    def Connect(self, serviceOrAddrOrPort, handler = None):
        handle = None
        addr   = None
        
        # Check first maybe it's an already-formed websocket address
        try:
            if serviceOrAddrOrPort.index("ws://") == 0:
                addr = serviceOrAddrOrPort
        except:
            pass

        # Or maybe the name of a service
        if not addr:
            data = self.LookupServiceByName(serviceOrAddrOrPort)
            
            if data:
                addr = data["addr"]

        # Or maybe the port of a service
        if not addr:
            data = self.LookupServiceByPort(serviceOrAddrOrPort)

            if data:
                addr = data["addr"]

        # Or maybe just a port not defined, so we make up an address
        if not addr:
            if serviceOrAddrOrPort.isdigit():
                addr = "ws://127.0.0.1:%s/ws" % serviceOrAddrOrPort
            else:
                pass

        # Try to connect to whatever we came up with
        if addr:
            handle = self.connect(addr, handler = handler)
            
        return handle
    

    def ReadServiceDirectory(self):
        ok = True

        core = os.environ["CORE"]
        serviceFile = core + "/generated-cfg/WSServices.txt"

        with open(serviceFile, 'r') as file:
            fileData = file.read().rstrip('\n')
        
            lineList = fileData.split("\n")
            
            port__seen = dict()

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
                                "addr"    : "ws://" + host + ":" + \
                                            port + wsPath,
                            }
                            
                            if service in self.service__data:
                                ok = False
                            elif port in port__seen:
                                ok = False
                            else:
                                self.service__data[service] = data
                                port__seen[port] = 1
        
        return ok


    def MakeServiceDataByPort(self, port):
        data = dict()

        data["service"] = "SERVICE_%s:%s" % (str(os.getpid()), port)
        data["host"]    = "127.0.0.1"
        data["port"]    = port
        data["wsPath"]  = "/ws"
        data["addr"]    = "ws://" + data["host"] + ":" + \
                          data["port"] + data["wsPath"]

        return data

    def MakeServiceDataClient(self):
        data = dict()

        data["service"] = "SERVICE_%s" % (str(os.getpid()))
        data["host"]    = "127.0.0.1"
        data["port"]    = "NA"
        data["wsPath"]  = "NA"
        data["addr"]    = "ws://" + data["host"] + ":" + \
                          data["port"] + data["wsPath"]

        return data


    def LookupServiceByName(self, service):
        data = None

        if service in self.service__data:
            data = self.service__data[service]

        return data


    def LookupServiceByPort(self, portSearch):
        data = None

        service = None
        port    = None
        
        for service in self.service__data.keys():
            tmpData = self.service__data[service]
            tmpPort = tmpData["port"]
            
            if tmpPort == portSearch:
                data = tmpData
            
        return data


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











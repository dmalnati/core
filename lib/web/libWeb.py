import sys
import os
import re

import mimetypes

from libDbManaged import *
from libWSApp import *
from libWebPythonPage import *



class AsyncGetter():
    def Start(self):
        pass

    def Stop(self):
        pass

        

class AsyncGetterEventHandler():
    def OnData(self, buf):
        pass

        
        
        
class AsyncGetterCmdInterval(AsyncGetter):
    def __init__(self, handler, cmd, intervalSec):
        self.handler     = handler
        self.cmd         = cmd
        self.cmdHandle   = None
        self.intervalSec = intervalSec
        self.timer       = None
        self.bufTotal    = ""
        
    def Start(self):
        self.CancelTimerIfAny()
        
        if not self.cmdHandle:
            self.bufTotal = ""
            self.cmdHandle = evm_WatchCommand(self.OnCmdData, self.cmd)

    def Stop(self):
        self.CancelTimerIfAny()
    
        if self.cmdHandle:
            evm_UnWatchCommand(self.cmdHandle)
            self.cmdHandle = None
        
        
    def OnCmdData(self, buf):
        if buf:
            self.bufTotal += buf
        else:
            self.handler.OnData(self.bufTotal)
            self.bufTotal = ""
            self.cmdHandle = None
            
            self.timer = evm_SetTimeout(self.OnTimeout, self.intervalSec * 1000)
    
    def OnTimeout(self):
        self.timer = None
        self.Start()
        
    def CancelTimerIfAny(self):
        if self.timer:
            evm_CancelTimeout(self.timer)
            self.timer = None
        

        
        
        


class WSPublisher(WSEventHandler, AsyncGetterEventHandler):
    def __init__(self, getter):
        self.getter = getter
        
        self.updLast = None
        
        self.ws__data = dict()
        
    ################################
    #
    # Distribute updates
    #
    ################################
        
    def SendUpdate(self, ws, upd):
        msg = {
            "MESSAGE_TYPE" : "PUB_UPDATE", 
            "UPDATE"       : upd,
        }
        
        ws.Write(msg)
        
    def BroadcastUpdate(self, upd):
        for ws in self.ws__data:
            self.SendUpdate(ws, upd)
    
    
    ################################
    #
    # Handle WebSocket events
    #
    ################################

    def OnWSConnectIn(self, ws):
        self.ws__data[ws] = True
        
        if len(self.ws__data.keys()) != 0:
            self.getter.Start()
        else:
            if self.updLast:
                self.SendUpdate(ws, self.updLast)

    def OnClose(self, ws):
        self.ws__data.pop(ws)
        
        if len(self.ws__data.keys()) == 0:
            self.getter.Stop()
            self.updLast = None

        
    ################################
    #
    # Handle AsyncGetterEventHandler updates
    #
    ################################
    
    def OnData(self, buf):
        if buf != None:
            self.updLast = buf
            self.BroadcastUpdate(self.updLast)
        else:
            self.updLast = None
            
            for ws in list(self.ws__data.keys()):
                ws.Close()
                self.ws__data.pop(ws)
    


class WSPublisherCommandInterval(WSPublisher, AsyncGetterEventHandler):
    def __init__(self, cmd, intervalSec):
        self.getter = AsyncGetterCmdInterval(self, cmd, intervalSec)
        WSPublisher.__init__(self, self.getter)


        
        
        
        
        
        
class AsyncGetterDatabaseCount(AsyncGetter):
    def __init__(self, db, handler, intervalSec):
        self.handler     = handler
        self.intervalSec = intervalSec
        self.timer       = None
        
        self.db = db
        
    def Start(self):
        self.CancelTimerIfAny()
        
        # schedule the first one immediately
        self.ScheduleNext(0)

    def Stop(self):
        self.CancelTimerIfAny()
    
    def ScheduleNext(self, durationSec):
        self.timer = evm_SetTimeout(self.OnTimeout, durationSec * 1000)
    
    def OnTimeout(self):
        name__value = dict()
        
        for table in self.db.GetTableList():
            count = self.db.GetTable(table).Count()
            
            name__value[table] = count
        
        self.handler.OnData(name__value)
        
        self.ScheduleNext(self.intervalSec)
        
    def CancelTimerIfAny(self):
        if self.timer:
            evm_CancelTimeout(self.timer)
            self.timer = None
        
        
        
        
        
        
        

class WSPublisherDatabaseCountInterval(WSPublisher, AsyncGetterEventHandler):
    def __init__(self, db, intervalSec):
        self.getter = AsyncGetterDatabaseCount(db, self, intervalSec)
        WSPublisher.__init__(self, self.getter)



        

class WSAppWebserver(WSApp):
    def __init__(self):
        WSApp.__init__(self)
        
        self.redirectPath = None
        self.db = ManagedDatabase(self)
        
        self.SetupFavicon()
        self.SetupRootRedirector()
        self.SetupMimeTypes()
        
        
    def SetupMimeTypes(self):
        mimetypes.add_type("text/html", ".pyp")

    
    def SetupFavicon(self):
        class FaviconHandler(WebRequestHandler):
            def get(self, *args, **kwargs):
                pass

        self.AddWebRequestHandler(r"/favicon.ico", FaviconHandler)
        
        
    def GetRootRedirectPath(self):
        return self.redirectPath
        
    def SetRootRedirectPath(self, redirectPath):
        self.redirectPath = redirectPath
        
    def SetupRootRedirector(self):
        class BaseUrlRedirector(WebRequestHandler):
            def initialize(self, **name__value):
                self.webserver = name__value["webserver"]
        
            def get(self):
                redirectPath = self.webserver.GetRootRedirectPath()
                
                if redirectPath:
                    self.redirect(redirectPath)
                else:
                    self.write("Webserver not ready")
        
        self.AddWebRequestHandler(r"/$", BaseUrlRedirector, **{
            "webserver" : self,
        })
        
        
    def Run(self):
        Log("Waiting for Database Available to begin")
        Log("")
        
        self.db.SetCbOnDatabaseStateChange(self.OnDatabaseStateChange)
        
        evm_MainLoop()

    def OnWebserverReady(self):
        pass
        
    def OnDatabaseAvaiable(self):
        Log("Database Available, starting")
        Log("")
        self.OnWebserverReady()

    def OnDatabaseClosing(self):
        Log("Database Closing, exiting")
        
    def OnDatabaseStateChange(self, dbState):
        if dbState == "DATABASE_AVAILABLE":
            self.OnDatabaseAvaiable()
        if dbState == "DATABASE_CLOSING":
            self.OnDatabaseClosing()

    def EnableStaticFileHandlerForProduct(self, product):
        webRoot = CorePath("/%s/web" % product)
        
        
        regex = r"/" + re.escape(product) + "/(.*\.pyp)$"
        self.AddWebRequestHandler(regex, PythonPageFileHandler, **{
            "path" : webRoot,
            "db"   : self.db,  
        })
        
        regex = r"/" + re.escape(product) + "/(.*)$"
        self.AddWebRequestHandler(regex, StaticFileHandler, **{
            "path"             : webRoot,
            "default_filename" : "index.pyp",
        })

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            
import sys
import os
import re

from libDbManaged import *
from libWSApp import *


class WSAppWebserver(WSApp):
    def __init__(self):
        WSApp.__init__(self)
        
        self.redirectPath = None
        self.db = ManagedDatabase(self)
        
        self.SetupFavicon()
        self.SetupRootRedirector()

    
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
        
            def get(self, *argList):
                redirectPath = self.webserver.GetRootRedirectPath()
                
                if redirectPath:
                    self.redirect(redirectPath)
                else:
                    self.write("Webserver not ready")
        
        self.AddWebRequestHandler(r"/()$", BaseUrlRedirector, **{
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
        
        # make something like "/product/(.*)$
        regex = r"/" + re.escape(product) + "/(.*)$"
        
        self.AddWebRequestHandler(regex, StaticFileHandler, **{
            "path"             : webRoot,
            "default_filename" : "index.html",
        })
            
            
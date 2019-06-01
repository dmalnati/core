#!/usr/bin/python -u

import sys
import os

from libCore import *


class App(WSApp):
    def __init__(self):
        WSApp.__init__(self)
        
        self.webRoot = CorePath("/core/web")
        Log("Serving pages from: %s" % self.webRoot)

        self.db = ManagedDatabase(self)
        
        app = self
        
        class FaviconHandler(WebRequestHandler):
            def get(self, *args, **kwargs):
                pass

        self.AddWebRequestHandler(r"/favicon.ico", FaviconHandler)
        self.AddWebRequestHandler(r"/()", StaticFileHandler, **{
            "path"             : self.webRoot,
            "default_filename" : "index.html",
        })
        self.AddWebRequestHandler(r"/(index.html)$", StaticFileHandler, **{
            "path"             : self.webRoot,
            "default_filename" : "index.html",
        })
        
        
        
        
    def Run(self):
        Log("Waiting for Database Available to begin")
        Log("")
        
        self.db.SetCbOnDatabaseStateChange(self.OnDatabaseStateChange)
        
        evm_MainLoop()

    def OnDatabaseAvaiable(self):
        Log("Database Available, starting")

    def OnDatabaseClosing(self):
        Log("Database Closing, no action taken")
        
    def OnDatabaseStateChange(self, dbState):
        if dbState == "DATABASE_AVAILABLE":
            self.OnDatabaseAvaiable()
        if dbState == "DATABASE_CLOSING":
            self.OnDatabaseClosing()

        
        

def Main():
    if len(sys.argv) < 1 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s" % os.path.basename(sys.argv[0]))
        sys.exit(-1)

    retVal = App().Run()

    return retVal == False


sys.exit(Main())















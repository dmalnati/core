#!/usr/bin/python -u

import sys
import os

from libCore import *


class App(WSAppWebserver):
    def __init__(self):
        WSAppWebserver.__init__(self)
        
        self.productLoadedList = []
        

    def OnWebserverReady(self):
        Log("Loading extensions")
    
        # As the core webserver, default to directing to the core web
        self.SetRootRedirectPath("/core/")
        
        # Load extensions
        productList = GetProductList()
    
        for product in productList:
            # Set up any dynamic handlers
            Log("Attempting to import %s" % product)
            module = None
            try:
                module = __import__("%s_Web" % product)
                Log("  Success")
            except Exception as e:
                Log("  Failure: %s" % e)
                
            if module:
                moduleOk = True
                try:
                    module.Init(self)
                except Exception as e:
                    Log("Error initializing: %s" % e)
                    moduleOk = False
                
                if moduleOk:
                    self.productLoadedList.append(product)
                
                    try:
                        self.EnableStaticFileHandlerForProduct(product)
                    except Exception as e:
                        Log("Failed to register static handler: %s" % e)

                        
        Log("Done imports")
        Log("Webserver ready")
        Log("")
        
        
        
        

def Main():
    if len(sys.argv) < 1 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s" % os.path.basename(sys.argv[0]))
        sys.exit(-1)

    retVal = App().Run()

    return retVal == False


sys.exit(Main())















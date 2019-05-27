#!/usr/bin/python -u

import sys
import os

from libCore import *


class App():
    def __init__(self):
        pass
        
    def Run(self):
        retVal = True

        # Read database configuration
        cfg = ConfigReader().ReadConfigOrAbort("Dct.master.json")

        # check if offline database exists, should thanks to Remap, or abort
        dbOffline = Database.GetDatabaseClosedFullPath()

        Log("Managing offline db: %s" % dbOffline)

        if not FileExists(dbOffline):
            Log("Offline db does not yet exist, creating")
        else:
            Log("Offline db exists, managing")

        # configure internal libraries
        Log("Opening database")
        self.db = Database()
        self.db.Connect(dbOffline)

        if self.db.Init(cfg, verbose=True):
            Log("Database ok")
        else:
            Log("Database NOT ok")
            retVal = False

        return retVal


def Main():
    if len(sys.argv) < 1 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s" % os.path.basename(sys.argv[0]))
        sys.exit(-1)

    retVal = App().Run()

    return retVal == False


sys.exit(Main())















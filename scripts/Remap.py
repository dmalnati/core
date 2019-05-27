#!/usr/bin/python -u

import sys
import os

from libCore import *


class App():
    def __init__(self):
        self.dbOffline = Database.GetDatabaseClosedFullPath()
        dbOfflineDir   = DirectoryPart(self.dbOffline)

        self.cfgName          = "Dct.master.json"
        self.cfgNameCached    = dbOfflineDir + "/" + self.cfgName
        self.cfgNameGenerated = CorePath("/generated-cfg/" + self.cfgName)

    # Cached Dct should exist if this function is being called
    def CachedDctValid(self):
        retVal = True

        # Compare $GC version to cached version
        Log("Checking consistency between Cached and Generated %s" %
            self.cfgName)
        Log("Cached   : %s" % self.cfgNameCached)
        Log("Generated: %s" % self.cfgNameGenerated)

        if ConfigReader().SelectConfigLocation(self.cfgNameGenerated):
            Log("Both Dct files exist")
            # compare contents regardless of whether older or newer

            cfgGenerated = \
                ConfigReader().ReadConfigOrAbort(self.cfgNameGenerated)
            cfgCached    = ConfigReader().ReadConfigOrAbort(self.cfgNameCached)

            if not ConfigReader().Equal(cfgGenerated, cfgCached):
                Log("Dct files NOT equal, inconsistent")
                retVal = False
            else:
                Log("Dct files equal")
        else:
            Log("%s missing, inconsistency between generated and cached Dct" %
                self.cfgNameGenerated)
            retVal = False

        if retVal:
            Log("OK")
        else:
            Log("NOT OK")

        return retVal


    def OfflineDbConsistent(self):
        retVal = True

        # check if offline database exists, should thanks to Remap, or abort
        dbOfflineExists = FileExists(self.dbOffline)
        cachedDctExists = FileExists(self.cfgNameCached)

        # they can both exist
        # they can both not exist
        # but it can't be one does and one doesn't

        if dbOfflineExists == True and cachedDctExists == False:
            Log("ERR: Offline db exists but cached %s missing, quitting" %
                self.cfgName)
            retVal = False
        elif dbOfflineExists == False and cachedDctExists == True:
            Log("ERR: Offline db missing but cached %s exists, quitting" %
                self.cfgName)
            retVal = False
        elif dbOfflineExists == False and cachedDctExists == False:
            Log("Offline db does not yet exist, creating")
            # copy Dct
            SafeCopyFileIfExists(self.cfgNameGenerated, self.cfgNameCached)
        elif dbOfflineExists == True  and cachedDctExists == True:
            # now check consistency to $GC
            if not self.CachedDctValid():
                Log("Cached Dct not valid")
                retVal = False
            else:
                Log("Offline db exists, managing")

        return retVal

        
    def Run(self):
        retVal = True

        ss = ServerState()
        state = ss.GetState()

        if state == "CLOSED":
            if self.OfflineDbConsistent():
                Log("Offline database consistent")

                # Read cached database configuration
                cfg = ConfigReader().ReadConfigOrAbort(self.cfgNameCached)

                Log("Managing offline db: %s" % self.dbOffline)

                # configure internal libraries
                Log("Opening database")
                self.db = Database()
                self.db.Connect(self.dbOffline)

                if self.db.Init(cfg, verbose=True):
                    Log("Database ok")
                else:
                    Log("Database NOT ok")
                    retVal = False
            else:
                Log("Offline database NOT consistent")
                retVal = False
        else:
            Log("Server state %s not CLOSED, quitting" % state)
            retVal = False

        return retVal


def Main():
    if len(sys.argv) < 1 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s" % os.path.basename(sys.argv[0]))
        sys.exit(-1)

    retVal = App().Run()

    return retVal == False


sys.exit(Main())















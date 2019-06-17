#!/usr/bin/python3.5 -u

import datetime
import sys
import os

from libCore import *


class App(WSApp, WSEventHandler):
    def __init__(self):
        WSApp.__init__(self)

        self.db = None
        self.dbState = "DATABASE_CLOSED"
        self.backupIntervalMin         = float(SysDef().Get("CORE_DATABASE_BACKUP_INTERVAL_MIN"))
        self.capacityCheckIntervalMin  = float(SysDef().Get("CORE_DATABASE_CAPACITY_CHECK_INTERVAL_MIN"))
        self.capacityCheckThresholdPct = int(SysDef().Get("CORE_DATABASE_CAPACITY_CHECK_THRESHOLD_PCT"))
        
        Log("Configured for:")
        Log("Backup interval min              : %s" % int(self.backupIntervalMin))
        Log("Disk capacity check interval min : %s" % int(self.capacityCheckIntervalMin))
        Log("Disk capacity check threshold pct: %s%%" % self.capacityCheckThresholdPct)
        Log("")
        
    def Run(self):
        ok = True

        if ok:
            # check if offline database exists, should thanks to Remap, or abort
            dbOffline = Database.GetDatabaseClosedFullPath()
            Log("Checking offline db exists: %s" % dbOffline)
            if not FileExists(dbOffline):
                Log("ERR: Offline db file does not exist: %s" % dbOffline)
                ok = False
            else:
                Log("Offline db OK")
            Log("")

        if ok:
            # move it to ram
            dbOnline = Database.GetDatabaseRunningFullPath()
            Log("Preparing to bring database online")
            SafeMakeDir(DirectoryPart(dbOnline))

            if FileExists(dbOnline):
                Log("ERR: Online database already exists, not a clean shutdown")

                backupFile = dbOffline + '.backup.' + datetime.datetime.now().strftime("%Y_%m_%d__%H_%M_%S")

                Log("Moving existing online to backup %s and starting from last good" % backupFile)

                if SafeMoveFileIfExists(dbOnline, backupFile):
                    Log("Backup succeeded")
                else:
                    Log("ERR: Backup failed, pressing on anyway")
                    SafeRemoveFileIfExists(dbOnline)
            else:
                Log("Prepare OK")
            Log("")

        if ok:
            Log("Copying offline db to online runtime: %s" % dbOnline)
            if not SafeCopyFileIfExists(dbOffline, dbOnline):
                Log("ERR: Unable to put database online")
                ok = False
            else:
                Log("Copy OK")
            Log("")

        if ok:
            self.db = Database()
            Log("Opening database")
            if self.db.Connect(forcedDbFullPath=Database.GetDatabaseRunningFullPath()):
                Log("Open OK")
                Log("")

                self.dbState = "DATABASE_AVAILABLE"
                
                self.ScheduleNextBackup()
                self.ScheduleNextDatabaseCapacityCheck()
                
                # Handle events
                Log("Running")
                Log("")
            else:
                Log("ERR: Could not open database, shutting down")
                self.OnDoDatabaseClose()
            
            evm_MainLoop()

        Log("Done")

        return ok

    def OnShutdown(self):
        Log("SHUTDOWN received, closing database")
        self.OnDoDatabaseClose()

    def SendState(self, ws, state):
        ws.Write({
            "MESSAGE_TYPE" : "DATABASE_STATE",
            "STATE"        : state,
            "DATABASE_PATH": Database.GetDatabaseRunningFullPath()
        })

    def AnnounceState(self, state):
        numConnected = len(self.GetWSInboundList())
        Log("Announcing state %s to %s clients" % (state, numConnected))
        for ws in self.GetWSInboundList():
            self.SendState(ws, state)

    def OnCheckAllDisconnected(self):
        secCheckAgain = 1

        numConnected = len(self.GetWSInboundList())
        if numConnected:
            Log("%s database state handlers still connected" % numConnected)
            Log("Checking again in %s" % secCheckAgain)

            evm_SetTimeout(self.OnCheckAllDisconnected, secCheckAgain * 1000)
        else:
            Log("All database state handlers have disconnected")
            Log("")
            self.OnAllDiconnectedSoCloseDatabase()

        Log("")
        
        
    def OnDoBackup(self):
        Log("Backing up database")
        Database.DoRunningBackup()
        
    def ScheduleNextBackup(self):
        def OnTimeout():
            self.OnDoBackup()
            self.ScheduleNextBackup()
        
        if self.dbState == "DATABASE_AVAILABLE":
            Log("Scheduling next database backup for %s minutes" % int(self.backupIntervalMin))
            Log("")
            evm_SetTimeout(OnTimeout, int(self.backupIntervalMin * 60 * 1000))
        
    def OnDoDatabaseCapacityCheck(self):
        pct = GetDiskUsagePct(Database.GetDatabaseRunningFullPath())
        
        if pct:
            if pct >= self.capacityCheckThresholdPct:
                Log("Disk capacity at %s%%, exceeds threshold of %s%%, taking database offline" %
                    (pct, self.capacityCheckThresholdPct))
                self.OnDoDatabaseClose()
            else:
                pass
        else:
            Log("Unable to get disk capacity for database, taking database offline")
            self.OnDoDatabaseClose()
        
        
    def ScheduleNextDatabaseCapacityCheck(self):
        def OnTimeout():
            self.OnDoDatabaseCapacityCheck()
            self.ScheduleNextDatabaseCapacityCheck()
        
        if self.dbState == "DATABASE_AVAILABLE":
            evm_SetTimeout(OnTimeout, int(self.capacityCheckIntervalMin * 60 * 1000))
        
        
    def OnAllDiconnectedSoCloseDatabase(self):
        ok = True

        # move online database offline
        Log("Copying online db offline")
        Log("")
        dbOnline  = Database.GetDatabaseRunningFullPath()
        dbOffline = Database.GetDatabaseClosedFullPath()
        if not SafeCopyFileIfExists(dbOnline, dbOffline):
            Log("Unable to copy online database offline")
            Log("")
            ok = False


        # remove ram version
        if ok:
            Log("Removing online database")
            Log("")
            SafeRemoveFileIfExists(dbOnline)

        if ok:
            Log("Database now offline, exiting")
        else:
            Log("Failed to take database offline, exiting")

        Log("")
        evm_MainLoopFinish()


    def OnDoDatabaseClose(self):
        Log("Database closing")
        Log("")

        # tell everyone
        self.dbState = "DATABASE_CLOSING"
        self.AnnounceState(self.dbState)

        # set timer to check that everyone has disconnected
        evm_SetTimeout(self.OnCheckAllDisconnected, 1000)

        
    ######################################################################
    #
    # Implementing WSApp Events
    #
    ######################################################################
        
    def OnWSConnectIn(self, ws):
        ws.SetHandler(self)
    
        numConnected = len(self.GetWSInboundList())
        Log("New inbound connection, total %s" % numConnected)
        Log("Sending state %s" % self.dbState)
        self.SendState(ws, self.dbState)
        Log("")

    def OnMessage(self, ws, msg):
        Log("Ignoring message received:")
        ws.DumpMsg(msg)

    def OnClose(self, ws):
        numConnected = len(self.GetWSInboundList())
        Log("Prior connection closed, total %s" % numConnected)
        Log("")
        
    def OnError(self, ws):
        pass
        
        
        

def Main():
    if len(sys.argv) < 1 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s" % os.path.basename(sys.argv[0]))
        sys.exit(-1)

    retVal = App().Run()

    return retVal == False


sys.exit(Main())















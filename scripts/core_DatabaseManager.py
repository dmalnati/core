#!/usr/bin/python -u

import sys
import os

from libCore import *


class App(WSApp, WSEventHandler):
    def __init__(self):
        WSApp.__init__(self)

        self.dbState = "DATABASE_CLOSED"
        
    def Run(self):
        ok = True

        if ok:
            # check if offline database exists, should thanks to Remap, or abort
            dbOffline = Database.GetDatabaseClosedFullPath()
            Log("Checking offline db exists: %s" % dbOffline)
            Log("")
            if not FileExists(dbOffline):
                Log("ERR: Offline db file does not exist: %s" % dbOffline)
                Log("")
                ok = False

        if ok:
            # move it to ram
            dbOnline = Database.GetDatabaseRunningFullPath()
            Log("Moving offline db to online runtime: %s" % dbOnline)
            Log("")
            SafeMakeDir(DirectoryPart(dbOnline))

            if FileExists(dbOnline):
                Log("ERR: Online database already exists")
                Log("")
                ok = False

        if ok:
            if not SafeCopyFileIfExists(dbOffline, dbOnline):
                Log("ERR: Unable to put database online")
                Log("")
                ok = False

        if ok:
            self.dbState = "DATABASE_AVAILABLE"

            # Handle events
            Log("Running")
            Log("")
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
        evm_SetTimeout(self.OnCheckAllDisconnected, 500)

        
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















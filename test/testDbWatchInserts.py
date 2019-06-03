#!/usr/bin/python -u

import os
import subprocess
import time
import sys

from libCore import *


class App(WSApp):
    def __init__(self, table, intervalSec):
        WSApp.__init__(self)

        self.table       = table
        self.intervalSec = intervalSec
        
        # get handles to database
        self.db = ManagedDatabase(self)

    def Run(self):
        Log("Waiting for Database Available to begin")
        Log("")
        
        self.db.SetCbOnDatabaseStateChange(self.OnDatabaseStateChange)
        
        evm_MainLoop()

    def OnDatabaseAvaiable(self):
        Log("Database Available, starting")

        Log("Watching %s" % self.table)
        self.t         = self.db.GetTable(self.table)
        self.rowIdLast = self.t.GetHighestRowId() - 20
        
        evm_SetTimeout(self.OnTimeout, 0)


    def OnDatabaseClosing(self):
        Log("Database Closing, exiting")
        
    def OnDatabaseStateChange(self, dbState):
        if dbState == "DATABASE_AVAILABLE":
            self.OnDatabaseAvaiable()
        if dbState == "DATABASE_CLOSING":
            self.OnDatabaseClosing()

    def CheckForUpdates(self):
        # Prepare to walk records
        rec = self.t.GetRecordAccessor()
        rec.SetRowId(self.rowIdLast)
        
        # Walk list of records starting from last seen
        while rec.ReadNextInLinearScan():
            #rec.DumpVertical(Log)
            rec.DumpHorizontal(8, Log)
        
        self.rowIdLast = rec.GetRowId()
    
    def OnTimeout(self):
        self.CheckForUpdates()
        
        timeoutMs = self.intervalSec * 1000
        
        evm_SetTimeout(self.OnTimeout, timeoutMs)

    
    

def Main():
    # default arguments
    intervalSec = 1

    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <table> <intervalSec=%s>" % (sys.argv[0], intervalSec))
        sys.exit(-1)

    table = sys.argv[1]

    # pull out arguments
    if len(sys.argv) >= 3:
        intervalSec = int(sys.argv[2])
        
    # create and run app
    app = App(table, intervalSec)
    app.Run()



Main()













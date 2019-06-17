#!/usr/bin/python3.5 -u

import os
import subprocess
import time
import sys

from libCore import *


class App(WSApp):
    def __init__(self, table):
        WSApp.__init__(self)

        self.table = table
        
        # get handles to database
        self.db = ManagedDatabase(self)

    def Run(self):
        Log("Waiting for Database Available to begin")
        Log("")
        
        self.db.SetCbOnDatabaseStateChange(self.OnDatabaseStateChange)
        
        evm_MainLoop()

    def OnDatabaseAvaiable(self):
        Log("Database Available, starting")

        Log("Clearing %s" % self.table)
        self.t         = self.db.GetTable(self.table)

        delCount = self.t.DeleteOlderThan(0)

        Log("Deleted %s records" % delCount)

        evm_MainLoopFinish()


    def OnDatabaseClosing(self):
        Log("Database Closing, exiting")
        
    def OnDatabaseStateChange(self, dbState):
        if dbState == "DATABASE_AVAILABLE":
            self.OnDatabaseAvaiable()
        if dbState == "DATABASE_CLOSING":
            self.OnDatabaseClosing()


def Main():
    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <table>" % (sys.argv[0]))
        sys.exit(-1)

    table = sys.argv[1]

    # create and run app
    app = App(table)
    app.Run()



Main()













#!/usr/bin/python -u

import sys
import os

from libCore import *


class App(WSApp):
    def __init__(self):
        WSApp.__init__(self)

        self.db = ManagedDatabase(self)
        self.db.SetCbOnDatabaseStateChange(self.OnDatabaseStateChange)

    def OnDatabaseAvaiable(self):
        Log("OnDatabaseAvailable")

        tableList = self.db.GetTableList()
        tableListLen = len(tableList)

        Log("%s tables" % tableListLen)
        for table in tableList:
            dbTable = self.db.GetTable(table)
            count = dbTable.Count()

            Log("Table %s - %s records" % (table, count))


    def OnDatabaseClosing(self):
        Log("OnDatabaseClosing")

    def OnDatabaseStateChange(self, dbState):
        Log("DB State: %s" % dbState)

        if dbState == "DATABASE_AVAILABLE":
            self.OnDatabaseAvaiable()
        if dbState == "DATABASE_CLOSING":
            self.OnDatabaseClosing()

    def OnExit(self):
        Log("Exiting")

    def Run(self):
        evm_MainLoop()
        self.OnExit()


def Main():
    if len(sys.argv) < 1 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %" %  os.path.basename(sys.argv[0]))
        sys.exit(-1)

    retVal = App().Run()

    return retVal == False


sys.exit(Main())















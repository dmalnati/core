#!/usr/bin/python3.5 -u

import os
import subprocess
import datetime
import sys

from libCore import *


class App(WSApp):
    def __init__(self, intervalSec):
        WSApp.__init__(self)

        self.intervalSec = intervalSec

        self.firstRun          = True
        self.table__countFirst = dict()
        self.table__countLast  = dict()
        
        # get handles to database
        self.db = ManagedDatabase(self)

    def Run(self):
        Log("Waiting for Database Available to begin")
        Log("")
        
        self.db.SetCbOnDatabaseStateChange(self.OnDatabaseStateChange)
        
        evm_MainLoop()

    def OnDatabaseAvaiable(self):
        Log("Database Available, starting")

        evm_SetTimeout(self.OnTimeout, 0)

    def OnDatabaseClosing(self):
        Log("Database Closing, exiting")
        
    def OnDatabaseStateChange(self, dbState):
        if dbState == "DATABASE_AVAILABLE":
            self.OnDatabaseAvaiable()
        if dbState == "DATABASE_CLOSING":
            self.OnDatabaseClosing()

    def OnTimeout(self):
        table__count = dict()

        # Gather current counts and table/count lengths for formatting
        maxTableLen = 0
        maxCountLen = 0
        for table in self.db.GetTableList():
            count               = self.db.GetTable(table).Count()
            table__count[table] = count

            strLen = len(table)
            if strLen > maxTableLen:
                maxTableLen = strLen

            strLen = len(Commas(str(count)))
            if strLen > maxCountLen:
                maxCountLen = strLen

        # Keep track of initial sizes if this is the first time
        # Initialize last if this is the first time
        if self.firstRun:
            self.firstRun = False

            for table in table__count:
                self.table__countFirst[table] = table__count[table]
                self.table__countLast[table]  = table__count[table]

        # Display
        tableList = sorted(table__count.keys())

        strLen = len("TABLE")
        if strLen > maxTableLen:
            maxTableLen = strLen

        strLen = len("DELTA_FIRST")
        if strLen > maxCountLen:
            maxCountLen = strLen

        if sys.stdout.isatty():
            subprocess.call("tput clear".split())

        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        print("Interval: {}s".format(self.intervalSec))
        print()

        print("%-*s : %*s  %*s   %*s " % \
              (maxTableLen, "TABLE", \
               maxCountLen, "COUNT", \
               maxCountLen, "DELTA_LAST", \
               maxCountLen, "DELTA_FIRST"))
        print("%-*s : %*s  %*s   %*s " % \
              (maxTableLen, "-----", \
               maxCountLen, "-----", \
               maxCountLen, "----------", \
               maxCountLen, "-----------"))

        for table in tableList:
            count = table__count[table]

            deltaLast  = count - self.table__countLast[table]
            deltaFirst = count - self.table__countFirst[table]

            #print("{} : {} {} {}".format(table, count, deltaLast, deltaFirst))


            print("%-*s : %*s (%*s) (%*s)" % \
                  (maxTableLen, table, \
                   maxCountLen, Commas(count), \
                   maxCountLen, Commas(deltaLast), \
                   maxCountLen, Commas(deltaFirst)))

        print()

        # Keep track of last
        for table in table__count:
            self.table__countLast[table]  = table__count[table]


        # Schedule next
        timeoutMs = self.intervalSec * 1000
        
        evm_SetTimeout(self.OnTimeout, timeoutMs)

    
    

def Main():
    # default arguments
    intervalSec = 5

    if len(sys.argv) >= 3 or (len(sys.argv) > 1 and sys.argv[1] == "--help"):
        print("Usage: %s <intervalSec=%s>" % (sys.argv[0], intervalSec))
        sys.exit(-1)

    # pull out arguments
    if len(sys.argv) == 2:
        intervalSec = int(sys.argv[1])
        
    # create and run app
    app = App(intervalSec)
    app.Run()



Main()













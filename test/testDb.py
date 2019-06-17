#!/usr/bin/python3.5 -u

import sys
import os

from libCore import *


class App:
    def __init__(self):
        self.db = Database()
        
    def OnTimeout(self):
        Log("App Connecting to database: %s")

        if self.db.Connect():
            Log("App Connected to database")
        else:
            Log("App Could not connect to database")
        
    def OnStdIn(self, line):
        linePartList = line.split()

        cmd = linePartList[0]
        arg1 = None
        arg2 = None

        if len(linePartList) >= 2:
            arg1 = linePartList[1]

        if len(linePartList) >= 3:
            arg2 = linePartList[2]


    def OnExit(self):
        pass

    def Run(self):
        evm_SetTimeout(self.OnTimeout, 0)
        WatchStdinLinesEndLoopOnEOF(self.OnStdIn)
        evm_MainLoop()
        self.OnExit()


def Main():
    if len(sys.argv) < 1 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %" %  os.path.basename(sys.argv[0]))
        sys.exit(-1)

    retVal = App().Run()

    return retVal == False


sys.exit(Main())















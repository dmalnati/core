#!/usr/bin/python3.5 -u

import sys
import os

from libCore import *


class App:
    def __init__(self):
        self.ss = ServerState()
        
    def OnTimeout(self):
        pass
        
    def OnStdIn(self, line):
        linePartList = line.split()

        cmd = linePartList[0]
        arg = ""
        if len(linePartList) >= 2:
            arg = linePartList[1]

        if cmd == "get":
            print("State: " + self.ss.GetState())
        if cmd == "gettime":
            retVal = self.ss.GetTimeOfLastChange()

            timeStr = "??"

            if retVal:
                timeStr = retVal

            secs = self.ss.GetDurationOfCurrentStateSecs()
            dur  = self.ss.GetDurationOfCurrentStateFormatted()

            print("LastChange: %s (%s sec, %s duration)" % (timeStr, secs,dur))
        elif cmd == "lock":
            retVal = self.ss.GetStateLock()
            print("Locking: %s" % retVal)
        elif cmd == "set":
            retVal = self.ss.SetState(arg)
            print("Setting state %s: %s" % (arg, retVal))
        elif cmd == "unlock":
            retVal = self.ss.ReleaseStateLock()
            print("UnLocking: %s" % retVal)

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















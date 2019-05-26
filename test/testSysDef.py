#!/usr/bin/python -u

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
        arg1 = None
        arg2 = None

        if len(linePartList) >= 2:
            arg1 = linePartList[1]

        if len(linePartList) >= 3:
            arg2 = linePartList[2]


        if cmd == "get":
            print("Get(%s, %s) = %s" % (arg1, arg2, SysDef.Get(arg1, arg2)))
        elif cmd == "list":
            print("GetParamList() = %s" % (SysDef.GetParamList()))

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















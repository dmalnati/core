#!/usr/bin/python3.5 -u

import sys
import os

from libCore import *


class App:
    def __init__(self):
        pass
        
    def OnTimeout(self):
        pass
        
    def OnStdIn(self, line):
        pass
        
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















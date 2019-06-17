#!/usr/bin/python3.5 -u

import sys
import os

from libCore import *


class App():
    def __init__(self, cmd):
        self.cmd = cmd
        
    def Run(self):
        def Handler(buf):
            if buf:
                print(buf, end="")
            else:
                evm_MainLoopFinish()

        evm_WatchCommand(Handler, self.cmd)

        evm_MainLoop()
        

def Main():
    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <cmd>" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    cmd = sys.argv[1]

    app = App(cmd)
    app.Run()


Main()















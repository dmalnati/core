#!/usr/bin/python -u

import os
import subprocess
import time
import sys

from libCore import *


class App(WSApp):
    def __init__(self):
        WSApp.__init__(self)

    def Run(self):
        evm_SetTimeout(self.OnTimeout, 0)
        evm_MainLoop()

    
    def OnTimeout(self):
        val = 10 / 0
        evm_SetTimeout(self.OnTimeout, 1000)

    
    

def Main():
    if len(sys.argv) < 1 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s" % (sys.argv[0]))
        sys.exit(-1)

    app = App()
    app.Run()



Main()













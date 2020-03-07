#!/usr/bin/python -u

import datetime
import os
import sys
import time

#from libCore import *


class App():
    def __init__(self, dir):
        self.dir = dir

    def Run(self):
        for path, dirList, fileList in os.walk(self.dir, followlinks =True):
            for dir in dirList:
                print(path + '/' + dir)


    def OnKeyboardInput(self, line):
        pass
    
    def OnTimeout(self):
        pass




def Main():
    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <dir>" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    dir = sys.argv[1]
    app = App(dir)

    return app.Run() == False


sys.exit(Main())















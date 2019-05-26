#!/usr/bin/python -u

import sys
import os

from libCore import *


def Main():
    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <cfg.json>" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    cfgFile = sys.argv[1]

    cfgReader = ConfigReader()
    cfg = cfgReader.ReadConfig(cfgFile, verbose=True)


Main()















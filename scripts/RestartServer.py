#!/usr/bin/python3.5 -u

import os
import subprocess
import sys
import time

from libCore import *


def Main():
    retVal = True

    if len(sys.argv) > 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s" %  os.path.basename(sys.argv[0]))
        sys.exit(-1)

    forceFlag = False
    if len(sys.argv) == 2 and sys.argv[1] == "--force":
        forceFlag = True


    # CloseServer
    try:
        subprocess.check_call("CloseServer.py".split())
        retVal &= True
    except Exception as e:
        Log("Could not close server: %s" % e)
        retVal &= False


    # StartServer
    try:
        if forceFlag:
            subprocess.check_call("StartServer.py --force".split())
        else:
            subprocess.check_call("StartServer.py".split())

        retVal &= True
    except Exception as e:
        Log("Could not start server: %s" % e)
        retVal &= False

    return retVal == False


sys.exit(Main())














#!/usr/bin/python3.5 -u

import os
import subprocess
import sys

from libCore import *


def MoveOldLogFiles(service):
    pathFrom = CorePath("/runtime/logs")
    pathTo   = CorePath("/runtime/logs/currentRun")

    for srcFile in Glob(pathFrom + "/" + service + ".*"):
        filePart = FilePart(srcFile)
        SafeMoveFileIfExists(srcFile, pathTo + "/" + filePart)
    

def Main():
    retVal = False

    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <service>" %  os.path.basename(sys.argv[0]))
        sys.exit(-1)

    service = sys.argv[1]

    if RunInfo.ServiceExists(service):
        if not RunInfo.ServiceIsRunning(service):
            MoveOldLogFiles(service)

            try:
                subprocess.check_call(("Run.py "+ service).split())

                Log("Service %s started" % service)

                retVal = True
            except:
                Log("Service %s could not be started" % service)
        else:
            Log("Service %s already running" % service)
    else:
        Log("Service %s does not exist" % service)

    return retVal == False


sys.exit(Main())














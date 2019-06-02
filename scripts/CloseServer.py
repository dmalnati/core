#!/usr/bin/python -u

import os
import subprocess
import sys
import time

from libCore import *


def Archive(timeOfCurrentState):
    archiveDir = timeOfCurrentState
    archiveDir = archiveDir.replace("-", "_")
    archiveDir = archiveDir.replace(" ", "__")
    archiveDir = archiveDir.replace(":", "_")

    # Archive logs
    srcDir = CorePath("/runtime/logs")
    dstDir = CorePath("/archive/" + archiveDir + "/logs")

    SafeRecursiveDirectoryCopy(srcDir, dstDir)
    DeleteFilesInDir(srcDir)
    DeleteFilesInDir(srcDir + "/currentRun")

    # Keep a record of the generated config at the time
    srcDir = CorePath("/generated-cfg")
    dstDir = CorePath("/archive/" + archiveDir + "/generated-cfg")
    SafeRecursiveDirectoryCopy(srcDir, dstDir)




def Main():
    retVal = False

    if len(sys.argv) < 1 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s" %  os.path.basename(sys.argv[0]))
        sys.exit(-1)

    forceFlag = False
    if len(sys.argv) >= 2:
        if sys.argv[1] == "--force":
            forceFlag = True

    service__serviceDetail = RunInfo.GetServiceMap()

    serviceList = sorted(service__serviceDetail.keys())

    ss = ServerState()

    if ss.GetStateLock():
        state = ss.GetState()

        close = False
        if state == "STARTED":
            close = True

        if not close and forceFlag:
            close = True
            Log("Force closing despite state %s not being STARTED" % state)

        if close:
            timeOfCurrentState = ss.GetTimeOfLastChange()

            ss.SetState("CLOSING")

            Log("Closing all running services")
            for service in serviceList:
                if RunInfo.ServiceIsRunning(service):
                    try:
                        cmd = "KillProcess.py " + service
                        subprocess.check_call(cmd.split())
                        retVal = True
                    except Exception as e:
                        retVal = False
                else:
                    retVal = True

            ss.SetState("CLOSED")

            Archive(timeOfCurrentState)
        else:
            Log("State %s, needs to be STARTED, quitting" % state)

        ss.ReleaseStateLock()
    else:
        Log("State locked, operation in progress elsewhere, quitting")

    Log("Done")

    return retVal == False


sys.exit(Main())














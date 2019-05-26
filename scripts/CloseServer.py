#!/usr/bin/python -u

import os
import subprocess
import sys
import time

from libCore import *


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

    serviceList = service__serviceDetail.keys()
    serviceList.sort()

    ss = ServerState()

    if ss.GetStateLock():
        state = ss.GetState()

        close = False
        if state == "STARTED":
            close = True

        if not close and forceFlag:
            close = True
            print("Force closing despite state %s not being STARTED" % state)

        if close:
            ss.SetState("CLOSING")

            print("Closing all running services")
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
        else:
            print("State %s, needs to be STARTED, quitting" % state)

        ss.ReleaseStateLock()
    else:
        print("State locked, operation in progress elsewhere, quitting")

    print("Done")

    return retVal == False


sys.exit(Main())














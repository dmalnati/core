#!/usr/bin/python -u

import os
import subprocess
import sys
import time

from libCore import *


def RunRemap():
    retVal = True

    Log("Running Remap.py")
    try:
        subprocess.check_call(("Remap.py").split())
    except Exception as e:
        retVal = False

    return retVal


def Main():
    retVal = False

    if len(sys.argv) < 1 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s" %  os.path.basename(sys.argv[0]))
        sys.exit(-1)

    service__serviceDetail = RunInfo.GetServiceMap()

    serviceList = sorted(service__serviceDetail.keys())

    ss = ServerState()

    if ss.GetStateLock():
        state = ss.GetState()

        if state == "CLOSED":
            if RunRemap():
                ss.SetState("STARTING")

                Log("Starting all services")
                for service in serviceList:
                    if not RunInfo.ServiceIsRunning(service):
                        try:
                            cmd = "StartProcess.py " + service
                            subprocess.check_call(cmd.split())
                            retVal = True
                        except Exception as e:
                            retVal = False
                    else:
                        Log("Service %s already running, no action taken" % service)
                        retVal = True

                ss.SetState("STARTED")
            else:
                Log("Remap failed, quitting")
        else:
            Log("State %s, needs to be CLOSED, quitting" % state)

        ss.ReleaseStateLock()
    else:
        Log("State locked, operation in progress elsewhere, quitting")

    Log("Done")

    return retVal == False


sys.exit(Main())














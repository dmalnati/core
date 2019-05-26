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

    service__serviceDetail = RunInfo.GetServiceMap()

    serviceList = service__serviceDetail.keys()
    serviceList.sort()

    print("Starting all services")
    for service in serviceList:
        if not RunInfo.ServiceIsRunning(service):
            try:
                subprocess.check_call(("StartProcess.py " + service).split())
                retVal = True
            except Exception as e:
                retVal = False
        else:
            print("Service %s already running, no action taken" % service)
            retVal = True

    print("Done")

    return retVal == False


sys.exit(Main())














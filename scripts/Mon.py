#!/usr/bin/python -u

import os
import subprocess
import sys
import time

from libCore import *


def Mon():
    service__serviceDetail = RunInfo.GetServiceMap()
    service__process       = RunInfo.GetServiceProcessMap()

    serviceList = service__serviceDetail.keys()
    serviceList.sort()
    
    subprocess.call("tput clear".split())
    for service in serviceList:
        serviceDetail = service__serviceDetail[service]
        process       = service__process[service]

        pid  = "-"
        cpu  = "-"
        mem  = "-"
        desc = serviceDetail["desc"]

        if process:
            pid = process["PID"]
            cpu = process["CPU"]
            mem = process["MEM"]

        print("%6s %6s %6s    %-25s %-s" % (pid, cpu, mem, service, desc))


def Main():
    intervalSec = None

    if len(sys.argv) > 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s <intervalSec=None>" %  os.path.basename(sys.argv[0]))
        sys.exit(-1)

    if len(sys.argv) > 1:
        intervalSec = int(sys.argv[1])

    Mon()
    if intervalSec:
        while True:
            try:
                time.sleep(intervalSec)
            except:
                break
            Mon()

Main()
sys.exit(0)













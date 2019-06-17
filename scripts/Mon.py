#!/usr/bin/python3.5 -u

import os
import subprocess
import sys
import time

from libCore import *


def Mon():
    service__serviceDetail = RunInfo.GetServiceMap()
    service__process       = RunInfo.GetServiceProcessMap()

    serviceList = sorted(service__serviceDetail.keys())

    state         = ServerState().GetState()
    stateDuration = ServerState().GetDurationOfCurrentStateFormatted()

    dbBackupList = Glob(CorePath('/runtime/db/*.backup.*'))

    capacityCheckThresholdPct = int(SysDef().Get("CORE_DATABASE_CAPACITY_CHECK_THRESHOLD_PCT"))
    pct = GetDiskUsagePct(Database.GetDatabaseRunningFullPath())
    pctStr = "-"
    if pct != None:
        pctStr = "%s%%" % pct


    if sys.stdout.isatty():
        subprocess.call("tput clear".split())

    
    print("State: %s (for %s)" % (state, stateDuration))
    print("DB: %s / %s%%" %(pctStr, capacityCheckThresholdPct))

    if len(dbBackupList):
        print("")
        print("WARN: %s DB backup files present" % str(len(dbBackupList)))
        for dbBackup in dbBackupList:
            print("    %s" % dbBackup)

    print("")

    print("%6s %6s %6s    %-25s %-s" % ("pid", "cpu", "mem", "service", "desc"))
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














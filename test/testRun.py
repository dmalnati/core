#!/usr/bin/python3.5 -u

import sys
import os

from libCore import *


def Main():
    if len(sys.argv) < 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s cmd" %  os.path.basename(sys.argv[0]))
        sys.exit(-1)

    cmd = sys.argv[1]

    if cmd == "user":
        Log("User: %s" % GetUser())
    elif cmd == "pt":
        processList = RunInfo.GetProcessTable()
        for process in processList:
            Log("proc:")
            for key in process.keys():
                Log("  %s : %s" % (key, process[key]))
            Log("")
    elif cmd == "st":
        service__process = RunInfo.GetServiceProcessMap()
        
        for service in service__process.keys():
            Log("service: %s" % service)

            process = service__process[service]
            if process:
                for key in process.keys():
                    Log("%s - %s" % (key, process[key]))
            else:
                Log("NOT RUNNING")
            Log("")
    else:
        Log("%s not supported" % cmd)

Main()















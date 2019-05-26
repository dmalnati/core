import os

import json
import getpass
import subprocess

from libCore import *



class RunInfo():
    def __init__(self):
        pass

    @staticmethod
    def GetUser():
        return getpass.getuser()

    # PPID PID %CPU %MEM CMD
    @staticmethod
    def GetProcessTable():
        processList = []

        user = RunInfo.GetUser()
        output = \
            subprocess.check_output(['ps',
                                     '-U', user,
                                     '-o', 'ppid,pid,%cpu,%mem,cmd']).strip()
        lineList = output.split("\n")

        # ignore the header line
        for line in lineList[1:]:
            linePartList = line.split()

            process = dict()
            process["PPID"] = linePartList[0]
            process["PID"]  = linePartList[1]
            process["CPU"]  = linePartList[2]
            process["MEM"]  = linePartList[3]
            process["CMD"]  = " ".join(linePartList[4:])

            processList.append(process)

        return processList


    # return dict of all services
    #
    # if not running, maps to None
    # if running, maps to process
    #
    # eg:
    # NAME __ PPID PID %CPU %MEM CMD
    #
    @staticmethod
    def GetServiceProcessMap():
        service__process = dict()

        # First, find the name of all service names
        cfg = ConfigReader().ReadConfig("ProcessDetails.master.json")

        nameList = []
        for processDetail in cfg["processDetailsList"]:
            name = processDetail["name"]
            service__process[name] = None
            nameList.append(name)


        # Now walk the list of actual running processes and spots ones
        # which include the process name
        if len(nameList):
            service__ppid = dict()

            processTable = RunInfo.GetProcessTable()

            for process in processTable:
                pid  = process["PID"]
                ppid = process["PPID"]

                cmd = process["CMD"]
                cmdLastElement = cmd.split()[-1]

                # Check if something like this going on
                # /usr/bin/python -u /home/pi/run/core/scripts/Run.py SVC 
                if cmdLastElement in nameList:
                    # confirm that it's the Run.py command doing it
                    secondLast = os.path.basename(cmd.split()[-2])

                    if secondLast == "Run.py":
                        # ok, we now know we want this process' child, which is
                        # whatever the actual command is
                        service__ppid[cmdLastElement] = pid

            # now go find the actual command
            for service in service__ppid.keys():
                ppidOfService = service__ppid[service]

                for process in processTable:
                    ppid = process["PPID"]

                    if ppid == ppidOfService:
                        service__process[service] = process

        return service__process


    @staticmethod
    def GetServiceMap():
        cfg = ConfigReader().ReadConfig("ProcessDetails.master.json")

        service__serviceDetail = dict()

        for serviceDetail in cfg["processDetailsList"]:
            name = serviceDetail["name"]

            service__serviceDetail[name] = serviceDetail

        return service__serviceDetail


    @staticmethod
    def ServiceExists(service):
        retVal = False

        service__process = RunInfo.GetServiceMap()

        if service in service__process:
            retVal = True

        return retVal


    @staticmethod
    def ServiceIsRunning(service):
        retVal = False

        service__process = RunInfo.GetServiceProcessMap()

        if service in service__process:
            if service__process[service]:
                retVal = True

        return retVal

    @staticmethod
    def GetServicePid(service):
        retVal = None

        service__process = RunInfo.GetServiceProcessMap()

        if service in service__process:
            if service__process[service]:
                retVal = service__process[service]["PID"]

        return retVal
















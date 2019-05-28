import os

from libConfig import *


processDetailsConfig = None

class ProcessDetails():
    @staticmethod
    def Get(process):
        global processDetailsConfig
        ProcessDetails.InitIfNecessary()

        val = None
        
        for processDetails in processDetailsConfig:
            if process == processDetails["name"]:
                val = processDetails
                break
        
        return val

    @staticmethod
    def GetParamList():
        global processDetailsConfig
        ProcessDetails.InitIfNecessary()

        return processDetailsConfig.keys()
    

    @staticmethod
    def InitIfNecessary():
        global processDetailsConfig
        if processDetailsConfig == None:
            processDetailsConfig = ConfigReader().ReadConfigOrAbort("ProcessDetails.master.json")
            processDetailsConfig = processDetailsConfig["processDetailsList"]













import os

from libConfig import *


sysDefConfig = None
sysDefDirectory = None

class SysDef():
    @staticmethod
    def SetDir(sysDefDir):
        global sysDefDirectory
        sysDefDirectory = sysDefDir

    @staticmethod
    def Get(param, default=None):
        global sysDefConfig
        SysDef.InitIfNecessary()

        val = default

        if param in sysDefConfig:
            val = sysDefConfig[param]

        return val

    @staticmethod
    def GetParamList():
        global sysDefConfig
        SysDef.InitIfNecessary()

        return list(sysDefConfig.keys())
    

    @staticmethod
    def InitIfNecessary():
        global sysDefConfig
        global sysDefDirectory
        if sysDefConfig == None:
            if sysDefDirectory:
                sysDefConfig = ConfigReader().ReadConfigOrAbort(sysDefDirectory + "/SystemDefinition.master.json")
            else:
                sysDefConfig = ConfigReader().ReadConfigOrAbort("SystemDefinition.master.json")














import os

from libConfig import *


sysDefConfig = None

class SysDef():
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

        return sysDefConfig.keys()
    

    @staticmethod
    def InitIfNecessary():
        global sysDefConfig
        if sysDefConfig == None:
            sysDefConfig = ConfigReader().ReadConfigOrAbort("SystemDefinition.master.json")














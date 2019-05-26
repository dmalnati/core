import os

import json

from libCore import *


class ConfigReader():
    def __init__(self):
        self.e       = None
        self.cfg     = None
        self.jsonObj = None

        self.cfgPathList = os.environ["CORE_CFG_PATH"].split(":")


    def IsOk(self):
        return self.cfg != None


    def ReadConfig(self, cfgName, verbose = False):
        cfgFile = None

        # if absolute path, try that file
        # otherwise go through search path

        if verbose:
            Log("Searching for %s" % cfgName)

        if cfgName[0] == "/":
            if verbose:
                Log("%s is absolute" % cfgName)

            if os.path.isfile(cfgName):
                cfgFile = cfgName
        else:
            if verbose:
                Log("%s is relative" % cfgName)
                Log("Searching %s paths" % str(len(self.cfgPathList)))

            if len(self.cfgPathList):
                cont = True
                i    = 0

                while cont:
                    path = self.cfgPathList[i]
                    i += 1

                    tmpCfgFile = path + "/" + cfgName
                    
                    if os.path.isfile(tmpCfgFile):
                        cfgFile = tmpCfgFile

                        cont = False

                    if verbose:
                        Log("  Checking %s" % tmpCfgFile)
                        if cont:
                            Log("    Not Found")
                        else:
                            Log("    Found")

        if cfgFile:
            if verbose:
                Log("%s selected" % cfgFile)

            fileData = ""

            try:
                with open(cfgFile, 'r') as file:
                    fileData = file.read().rstrip('\n')
            except:
                pass

            jsonObj = None
            try:
                jsonObj = json.loads(fileData)

                if verbose:
                    Log("Read:")
                    print(json.dumps(jsonObj,
                                     sort_keys=True,
                                     indent=4,
                                     separators=(',', ': ')))
            except Exception as e:
                self.e = e
                if verbose:
                    Log("Could not read %s: %s" % (cfgFile, e))

        self.cfg = jsonObj

        return self.cfg

    def GetLastError(self):
        return self.e



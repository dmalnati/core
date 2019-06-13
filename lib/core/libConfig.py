import os
import sys

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

    def ReadConfigOrAbort(self, cfgName, verbose = False):
        cfg = self.ReadConfig(cfgName, verbose)

        if cfg == None:
           Log("Could not read %s: %s" % (cfgName, self.GetLastError())) 
           sys.exit(1)

        return cfg

    def SelectConfigLocation(self, cfgName, verbose = False):
        cfgFile = None

        # if absolute path, try that file
        # otherwise go through search path

        if verbose:
            Log("Searching for %s" % cfgName)

        if cfgName[0] == "/":
            if verbose:
                Log("%s is absolute" % cfgName)

            if FileExists(cfgName):
                cfgFile = cfgName
            else:
                self.e = "%s is not a file or non-existant" % cfgName
                if verbose:
                    Log(self.e)

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
                    
                    if FileExists(tmpCfgFile):
                        cfgFile = tmpCfgFile

                        cont = False

                    if verbose:
                        Log("  Checking %s" % tmpCfgFile)
                        if cont:
                            Log("    Not Found")
                        else:
                            Log("    Found")

                    if i == len(self.cfgPathList):
                        cont = False

        return cfgFile

    def ReadConfig(self, cfgName, verbose = False):
        cfgFile = None
        jsonObj = None

        cfgFile = self.SelectConfigLocation(cfgName, verbose)

        if cfgFile:
            if verbose:
                Log("%s selected" % cfgFile)

            fileData = ""

            try:
                with open(cfgFile, 'r') as file:
                    fileData = file.read().rstrip('\n')
                    fileData = self.StripComments(fileData)
            except:
                pass

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

    def StripComments(self, fileData):
        retVal = ""

        for line in fileData.split("\n"):
            lineStripped = line.strip()
            if len(lineStripped) >= 1:
                if lineStripped[0] == "#":
                    pass
                else:
                    retVal += line + "\n"

        return retVal

    def CfgToStr(self, cfg):
       return json.dumps(cfg,
                         sort_keys=True,
                         indent=4,
                         separators=(',', ': '))

    def CfgDump(self, cfg):
        print(self.CfgToStr(cfg))

    def Equal(self, cfg1, cfg2):
        return self.CfgToStr(cfg1) == self.CfgToStr(cfg2)


    def GetLastError(self):
        return self.e



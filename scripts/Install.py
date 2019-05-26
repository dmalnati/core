#!/usr/bin/python -u


import re
import os
import sys




#
# Two modes of operation
# - first is to assist environment setup
#   - therefore libCore won't be available yet as the paths are being created
# - second is to run as actual installer
#   - libCore expected to exist at that time
#
try:
    from libCore import *
except:
    pass


NON_PRODUCT_SUBDIR_LIST = [
    "/archive",
    "/generated-cfg",
    "/site-specific",
    "/site-specific/cfg",
    "/runtime",
    "/runtime/logs",
    "/runtime/logs/currentRun",
    "/runtime/working",
]


def GetProductDirectoryList():
    core = os.environ["CORE"]

    nonProductDirectoryList = GetNonProductDirectoryList()
    productDirectoryList    = []
    coreProductDir          = core + "/core"

    for name in os.listdir(core):
        directory = core + "/" + name
        if os.path.isdir(directory):
            if directory not in nonProductDirectoryList:
                if directory != coreProductDir:
                    productDirectoryList.append(directory)

    # put in alphabetical order
    productDirectoryList.sort()

    # put core first
    productDirectoryList = [coreProductDir] + productDirectoryList

    return productDirectoryList

def GetProductList():
    productList = []

    for productDirectory in GetProductDirectoryList():
        product = os.path.basename(os.path.normpath(productDirectory))
        productList.append(product)

    return productList

def GetProductListReversed():
    return GetProductList()[::-1]

def GetProductDirectoryListReversed():
    return GetProductDirectoryList()[::-1]


def GetNonProductDirectoryList():
    directoryList = []

    core = os.environ["CORE"]

    for nonProductSubdir in NON_PRODUCT_SUBDIR_LIST:
        directoryList.append(core + nonProductSubdir)

    return directoryList


def SetupDirectories():
    retVal = False

    Log("Setting up directories")

    directoryList = GetNonProductDirectoryList()

    try:
        for directory in directoryList:
            Log(directory)

            SafeMakeDir(directory)

        retVal = True
    except:
        pass

    if retVal:
        Log("  OK")
    else:
        Log("  NOT OK")

    return retVal




def DoSysDefSubstitution(file, cfg):
    try:
        fdIn = open(file, "r")
        buf = fdIn.read()
        fdIn.close()

        matchList = re.findall(r"%(.*?)%", buf)

        if len(matchList):
            matchList.sort()

            Log("")
            Log("%s ->" % file)
            Log("%s.presysdef" % file)
            didMatch = False
            for match in matchList:
                if match in cfg:
                    didMatch = True
                    val = cfg[match]
                    buf = buf.replace("%%%s%%" % (match), val)
                    Log("  %%%s%% -> \"%s\"" % (match, val))
                else:
                    Log("  %%%s%% -> [NO VALUE FOUND]" % match)

            SafeCopyFileIfExists(file, file + ".presysdef")
            fd = open(file, "w")
            fd.write(buf)
            fd.close()

    except Exception as e:
        Log("Failed to do substitution for %s: %s" % (file, e))
        sys.exit(1)




def ApplySysDefSubstitution(tmpDir):
    srcFile = tmpDir + "/SystemDefinition.master.json"
    cfg     = ConfigReader().ReadConfigOrAbort(srcFile)

    fileListSuffixNoSub = [
        "SystemDefinition.json"
        "SystemDefinition.master.json"
    ]

    for file in Glob(tmpDir + "/*"):
        filePartList = file.split("_")

        if filePartList[-1] not in fileListSuffixNoSub:
            DoSysDefSubstitution(file, cfg)




def MergeSysDefDetails(directory, fileSuffix, fileOut):
    productList = GetProductListReversed()
    srcFileList = []

    # find all product files which match the file suffix
    for product in productList:
        fFullPath = directory + "/" + product + "_" + fileSuffix

        if os.path.isfile(fFullPath):
            srcFileList.append(fFullPath)

    # add the master SysDef also
    fFullPath = directory + "/" + fileSuffix

    if os.path.isfile(fFullPath):
        srcFileList.append(fFullPath)

    # start crafting combined file
    cfgReader = ConfigReader()

    dataOut  = ""
    dataOut += "{"

    # read in all the process details entries and merge to one master
    sep = ""
    for srcFile in srcFileList:
        cfg = cfgReader.ReadConfigOrAbort(srcFile)

        dataStr = json.dumps(cfg)
        # the json will have starting { and } chars, so drop them, and combine
        dataStr = dataStr[1:-1].strip()
        if len(dataStr):
            dataOut += sep + dataStr
            sep = ","


    dataOut += "}"

    # prettify output
    jsonObj = json.loads(dataOut)
    dataOutFormated = (json.dumps(jsonObj,
                                  sort_keys=True,
                                  indent=4,
                                  separators=(',', ': ')))

    # write output file
    fFullPath = directory + "/" + fileOut
    with open(fFullPath, 'w') as file:
        file.write(dataOutFormated)


def MergeProcessDetails(directory, fileSuffix, fileOut):
    productList = GetProductList()
    srcFileList = []

    # find all product files which match the file suffix
    for product in productList:
        fFullPath = directory + "/" + product + "_" + fileSuffix

        if os.path.isfile(fFullPath):
            srcFileList.append(fFullPath)

    # handle the special case of this being about ProcessDetails
    if fileSuffix == "ProcessDetails.json":
        cfgReader = ConfigReader()

        dataOut  = ""
        dataOut += "{ \"processDetailsList\" : ["

        # read in all the process details entries and merge to one master
        sep = ""
        for srcFile in srcFileList:
            cfg = cfgReader.ReadConfigOrAbort(srcFile)

            processDetailList = cfg["processDetailsList"]
            for processDetail in processDetailList:
                processDetailStr = json.dumps(processDetail)

                dataOut += sep + processDetailStr

                sep = ","

        dataOut += "] }"

        # prettify output
        jsonObj = json.loads(dataOut)
        dataOutFormated = (json.dumps(jsonObj,
                                      sort_keys=True,
                                      indent=4,
                                      separators=(',', ': ')))

        # write output file
        fFullPath = directory + "/" + fileOut
        with open(fFullPath, 'w') as file:
            file.write(dataOutFormated)


# expected output format:
# <service> <host> <port> <wsPath>
def GenerateWSServices(directory):
    basePort = int(SysDef.Get("CORE_BASE_PORT"))

    cfgReader = ConfigReader()
    srcFile   = directory + "/ProcessDetails.master.json"
    cfg       = cfgReader.ReadConfigOrAbort(srcFile)

    try:
        fFullPath = directory + "/" + "WSServices.txt"
        with open(fFullPath, 'w') as file:

            file.write("\n\n")
            file.write("#######################################\n")
            file.write("# Auto-generated\n")
            file.write("#######################################\n")
            file.write("\n")


            # only processes which have a specific need for a port will be given
            # the one they want.
            # everything else will be auto-applied.

            port__reservedBy = dict()
            for processDetail in cfg["processDetailsList"]:
                if "port" in processDetail:
                    name = processDetail["name"]
                    port = processDetail["port"]
                    
                    if port in port__reservedBy:
                        Log("Error: ID %s reserved by %s, also by %s" %
                            (port, port__reservedBy[port], name))
                        sys.exit(1)

                    port__reservedBy[port] = name

            # auto-generate
            portAssignNext = basePort
            for processDetail in cfg["processDetailsList"]:
                if "port" in processDetail:
                    portAssign = int(processDetail["port"])
                else:
                    while portAssignNext in port__reservedBy:
                        portAssignNext += 1

                    portAssign = portAssignNext
                    portAssignNext += 1

                entry  = ""
                entry +=       processDetail["name"]
                entry += " " + "127.0.0.1"
                entry += " " + str(portAssign)
                entry += " " + "/ws"

                file.write(entry + "\n")
                file.write("\n")

            # copy in contents from product files
            productList = GetProductList()
            srcFileList = []

            # find all product files which match the file suffix
            for product in productList:
                fFullPath = directory + "/" + product + "_" + "WSServices.txt"

                if os.path.isfile(fFullPath):
                    file.write("\n")
                    file.write("#######################################\n")
                    file.write("# From product %s\n" % product)
                    file.write("#######################################\n")

                    with open(fFullPath) as fileProduct:
                        buf = fileProduct.read()
                        fileProduct.close()

                        file.write(buf)
                        file.write("\n")

    except Exception as e:
        Log("Couldn't generate WSServices: %s" % e)


def GenerateConfig():
    retVal = True

    Log("Assembling Configuration")
    Log("")

    core = os.environ["CORE"]

    productDirList = GetProductDirectoryListReversed()
    copyFromToList = []

    # make temporary directory after removing old if it exists
    tmpDir = core + "/generated-cfg/tmp"
    Log("Creating temporary folder %s" % tmpDir)
    RemoveDir(tmpDir)
    SafeMakeDir(tmpDir)

    # Do file copies
    Log("Creating temporary file set")
    Log("")
    for productDir in productDirList:
        productCfgDir = productDir + "/cfg"
        retVal &= CopyFiles(productCfgDir, tmpDir, verbose=True)

    retVal &= CopyFiles(core + "/site-specific/cfg", tmpDir, verbose=True)

    # Do file generation
    Log("Generating SystemDefinition.master.json")
    MergeSysDefDetails(tmpDir,
                       "SystemDefinition.json",
                       "SystemDefinition.master.json")
    Log("")

    Log("Applying SysDef substitutions")
    ApplySysDefSubstitution(tmpDir)
    Log("")

    Log("Generating ProcessDetials.master.json")
    MergeProcessDetails(tmpDir,
                        "ProcessDetails.json",
                        "ProcessDetails.master.json")
    Log("")

    Log("Generating WSServices.txt")
    GenerateWSServices(tmpDir)
    Log("")


    # if successful, replace current gencfg with new
    # then remove temporary
    if retVal:
        gcDir = core + "/generated-cfg"

        Log("Assembly succssful, moving to %s" % gcDir)

        DeleteFilesInDir(gcDir)
        CopyFiles(tmpDir, gcDir)
        RemoveDir(tmpDir)
    else:
        Log("Failed to generate config properly")

    Log("")

    return retVal







def Main():
    retVal = True

    if len(sys.argv) > 2 or (len(sys.argv) >= 2 and sys.argv[1] == "--help"):
        print("Usage: %s" % (os.path.basename(sys.argv[0])))
        sys.exit(-1)

    if "CORE" in os.environ:
        if len(sys.argv) == 2 and sys.argv[1] == "-getProductDirListReversed":
            print(" ".join(GetProductDirectoryListReversed()))
        else:
            forceFlag = False
            if len(sys.argv) == 2 and sys.argv[1] == "--force":
                forceFlag = True

            ss = ServerState()

            # check if state lock acquired, allow force
            movePastLock = True
            if not ss.GetStateLock():
                movePastLock = False

                if forceFlag:
                    movePastLock = True
                    Log("Force installing despite not acquiring lock")

            if movePastLock:
                state = ss.GetState()

                # check if state correct, allow force
                movePastState = True
                if not state == "CLOSED":
                    movePastState = False

                    if forceFlag:
                        movePastState = True
                        Log("Force installing despite state %s "
                            "not being CLOSED" % state)

                if movePastState:
                    retValSD = SetupDirectories()
                    Log("")
                    retValGC = GenerateConfig()

                    Log("DONE")

                    retVal = retValSD and retValGC
                else:
                    Log("State %s, needs to be CLOSED, quitting" % state)
                    retVal = False

                ss.ReleaseStateLock()
            else:
                Log("State locked, operation in progress elsewhere, quitting")
                retVal = False


    return retVal == False

sys.exit(Main())











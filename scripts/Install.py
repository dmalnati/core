#!/usr/bin/python3.5 -u


import getpass
import re
import os
import subprocess
import sys

from io import StringIO
import contextlib


#
# Two modes of operation
# - first is to assist environment setup
#   - therefore libCore won't be available yet as the paths are being created
# - second is to run as actual installer
#   - libCore expected to exist at that time
#
try:
    from libCore import *
    libCoreLoaded = True
except Exception as e:
    libCoreLoaded = False
    

# this is for when bootstrapping, manually import specific library
from importlib.machinery import SourceFileLoader
libCoreProduct = SourceFileLoader("module.name", os.environ["CORE"] + "/core/lib/core/libCoreProduct.py").load_module()

    

def CanSudo():
    result = subprocess.Popen("sudo -n ls".split(),
                              stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    result.wait()

    return result.returncode == 0

    
def CreateEnvironmentMap():
    envmapDir = libCoreProduct.CorePath('/runtime/working/')
    envmapName = envmapDir + '/core_envmap.env'

    if not os.path.exists(envmapDir):
        os.makedirs(envmapDir)

    envMap = libCoreProduct.GetEnvironmentMap()

    fd = open(envmapName, 'w')
    for key in envMap:
        print('%s="%s"' % (key, envMap[key]), file=fd)
    fd.close()


    
    
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




@contextlib.contextmanager
def stdoutIO(stdout=None):
    old = sys.stdout
    if stdout is None:
        stdout = StringIO()
    sys.stdout = stdout
    yield stdout
    sys.stdout = old


def DoDynamicSubstitution(file, cfg):
        # Pull the sourc file
        fd = open(file)
        buf = fd.read()
        fd.close()

        if buf.find("<?") != -1:
            Log("")
            Log("%s ->" % file)
            Log("%s.predyn" % file)

            strLen = len(buf)

            bufNew = ""

            # walk through file contents and look for executable sections.
            idx = 0
            cont = True
            while cont:
                # look for data leading up to first tag
                # then get the stuff between tags
                # repeat
                idxTagStart = buf.find("<?", idx)
                if idxTagStart != -1:
                    idxTagEnd = buf.find("?>", idxTagStart)

                    if idxTagEnd != -1:
                        rawOutput = buf[idx:idxTagStart]
                        dynCode   = buf[idxTagStart + 2:idxTagEnd]

                        idx = idxTagEnd + 2

                        bufNew += rawOutput

                        if dynCode.find("print") == -1:
                            try:
                                result = str(eval(dynCode))
                                bufNew += result
                            except Exception as e:
                                Log("Failed to do dynamic eval substitution for %s: %s" % (file, e))
                                print("\"" + dynCode + "\"")
                                sys.exit(1)
                        else:
                            with stdoutIO() as s:
                                try:
                                    exec(dynCode)
                                    result = s.getvalue()
                                    bufNew += result
                                except Exception as e:
                                    Log("Failed to do dynamic exec substitution for %s: %s" % (file, e))
                                    Log(dynCode)
                                    sys.exit(1)

                    else:
                        # that's not good -- author missed the close tag somehow
                        cont = False
                else:
                    cont = False


                if idx >= strLen:
                    cont = False

            if idx != strLen:
                bufNew += buf[idx:]


            if buf != bufNew:
                SafeCopyFileIfExists(file, file + ".predyn")
                fd = open(file, "w")
                fd.write(bufNew)
                fd.close()





def DoSysDefEnvironSubstitution(file, cfg):
    try:
        fdIn = open(file, "r")
        buf = fdIn.read()
        fdIn.close()

        matchList = re.findall(r"%(.*?)%", buf)

        if len(matchList):
            matchList.sort()

            Log("")
            Log("%s ->" % file)
            Log("%s.presub" % file)
            for match in matchList:
                if match in cfg:
                    val = cfg[match]
                    buf = buf.replace("%%%s%%" % (match), val)
                    Log("  %%%s%% -> \"%s\"" % (match, val))
                elif match[0] == "$" and match[1:] in os.environ:
                    val = os.environ[match[1:]]
                    buf = buf.replace("%%%s%%" % (match), val)
                    Log("  %%%s%% -> \"%s\"" % (match, val))
                else:
                    Log("  %%%s%% -> [NO VALUE FOUND]" % match)

            SafeCopyFileIfExists(file, file + ".presub")
            fd = open(file, "w")
            fd.write(buf)
            fd.close()

    except Exception as e:
        Log("Failed to do substitution for %s: %s" % (file, e))
        sys.exit(1)




def ApplySysDefEnvironSubstitution(tmpDir):
    srcFile = tmpDir + "/SystemDefinition.master.json"
    cfg     = ConfigReader().ReadConfigOrAbort(srcFile)

    fileListSuffixNoSub = [
        "SystemDefinition.json"
        "SystemDefinition.master.json"
    ]

    for file in sorted(Glob(tmpDir + "/*")):
        filePartList = file.split("_")

        if filePartList[-1] not in fileListSuffixNoSub:
            DoSysDefEnvironSubstitution(file, cfg)
            DoDynamicSubstitution(file, cfg)




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

    # read in this file and create simple text file of all
    # known services for tab completion (or other) purposes
    cfg = ConfigReader().ReadConfigOrAbort(directory + "/" + "ProcessDetails.master.json")

    nameList = []
    for processDetail in cfg["processDetailsList"]:
        nameList.append(processDetail["name"])
    nameList.sort()

    Log("Creating ProcessList.txt")
    fd = open(directory + "/" + "ProcessList.txt", "w")
    fd.write(" ".join(nameList) + "\n")
    fd.close()


def MergeDct(directory, fileSuffix, fileOut):
    productList = GetProductList()
    srcFileList = []

    # find all product files which match the file suffix
    for product in productList:
        fFullPath = directory + "/" + product + "_" + fileSuffix

        if os.path.isfile(fFullPath):
            srcFileList.append(fFullPath)

    cfgReader = ConfigReader()

    dataOut  = ""
    dataOut += "{ \"tableList\" : ["

    # read in all the details and merge to one master
    sep = ""
    for srcFile in srcFileList:
        cfg = cfgReader.ReadConfigOrAbort(srcFile)

        entryList = cfg["tableList"]
        for entry in entryList:
            entryStr = json.dumps(entry)

            dataOut += sep + entryStr

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

                    if port[0] == "+":
                        port = basePort + int(port[1:])
                    
                    if port in port__reservedBy:
                        Log("Error: ID %s reserved by %s, also by %s" %
                            (port, port__reservedBy[port], name))
                        sys.exit(1)

                    port__reservedBy[port] = name

            # auto-generate
            portAssignNext = basePort
            for processDetail in cfg["processDetailsList"]:
                if "port" in processDetail:
                    port = processDetail["port"]
                    if port[0] == "+":
                        port = basePort + int(port[1:])
                    else:
                        port = int(port)
                    portAssign = port
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


# https://www.brendanlong.com/systemd-user-services-are-amazing.html
def InstallService():
    service             = "core_systemd.service"
    user                = getpass.getuser()
    dirSystemd          = GetHomeDirectory() + "/.config/systemd/user"
    serviceFileFullPath = dirSystemd + '/' + service

    SafeMakeDir(dirSystemd)
    SafeRemoveFileIfExists(serviceFileFullPath)

    os.symlink(CorePath('/generated-cfg/core_systemd.service'), serviceFileFullPath)

    ok = True

    # this enables the user service described in the service file
    if ok:
        try:
            RunCommand("systemctl --user enable %s" % service)
        except Exception as e:
            ok = False
            Log("Could not enable service: %s" % e)

    # this enables bootup running of the service despite the user not being logged in
    if ok:
        try:
            RunCommand("sudo loginctl enable-linger %s" % user)
        except Exception as e:
            ok = False
            Log("Could not enable boot start for user %s: %s" % (user, e))

    # this is necessary after each change of the service file, which will happen
    # each time Install is run, as the prior file is overwritten.
    # necessary even if exactly the same file contents.
    if ok:
        try:
            RunCommand("systemctl --user daemon-reload")
        except Exception as e:
            ok = False
            Log("Could not reload user daemon: %s" % e)

    # now you can start the user service by hand by doing this
    # (though it will happen automatically on boot)
    #
    # systemctl --user start core_systemd.service
    #
    # To see the output, run:
    # sudo journalctl
    #


def GenerateConfig():
    retVal = True

    Log("Assembling Configuration")
    Log("")

    core = os.environ["CORE"]

    productDirList = libCoreProduct.GetProductDirectoryListReversed()
    copyFromToList = []

    # Create environment map
    Log("Creating environment map")
    CreateEnvironmentMap()
    Log("")

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

    # Cause SysDef accessor working off of generated copy
    SysDef.SetDir(tmpDir)

    # Do file generation
    Log("Generating SystemDefinition.master.json")
    MergeSysDefDetails(tmpDir,
                       "SystemDefinition.json",
                       "SystemDefinition.master.json")
    Log("")

    Log("Applying SysDef/Environ/Dyn substitutions")
    ApplySysDefEnvironSubstitution(tmpDir)
    Log("")

    Log("Generating ProcessDetials.master.json")
    MergeProcessDetails(tmpDir,
                        "ProcessDetails.json",
                        "ProcessDetails.master.json")

    Log("")
    Log("Generating Dct.master.json")
    MergeDct(tmpDir, "Dct.json", "Dct.master.json")
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
        Log("")

        Log("Enabling systemd service")
        InstallService()
        Log("")
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
        if len(sys.argv) == 2 and sys.argv[1] == "-createEnvironmentMap":
            CreateEnvironmentMap()
        else:
            if libCoreLoaded == False:
                print("ERR: libCore not loaded")
                print("Please install missing libraries")
                print("- tornado")
                print("- pytz")
                sys.exit(1)

            if CanSudo() == False:
                print("ERR: user %s not able to sudo, but needs to" % getpass.getuser())
                print("Have a privileged user run the following:")
                print("")
                print("sudo sh -c ", end='')
                print("'echo \"%s ALL=(ALL) NOPASSWD: ALL\" " %
                      getpass.getuser(), end='')
                print("> /etc/sudoers.d/%s_nopasswd'" % getpass.getuser())
                print("")

                sys.exit(1)


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











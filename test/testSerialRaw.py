#!/usr/bin/python -u

import sys
import os
import time

import pigpio

from libCore import *
from libSerialRaw import *


def GroupArgs(argv):
    argList  = []
    flagList = []

    argLast = ""
    if len(argv):
        for arg in argv:
            if (arg[0] == "-" and arg != "-") or argLast == "-c":
                flagList.append(arg)
            else:
                argList.append(arg)

            argLast = arg

    return (argList, flagList)


FLAG_NNL  = False
FLAG_NTOR = False
FLAG_TS   = False
FLAG_TS_CSV = False
CMD_LIST = []
def ProcessFlags(flagList):
    global FLAG_NNL
    global FLAG_NTOR
    global FLAG_TS
    global FLAG_TS_CSV
    global CMD_LIST

    i = 0
    flagListLen = len(flagList)

    while i < flagListLen:
        flag = flagList[i]

        if flag == "-nnl":
            FLAG_NNL = True
        elif flag == "-ntor":
            FLAG_NTOR = True
        elif flag == "-ts":
            FLAG_TS = True
        elif flag == "-tsCsv":
            FLAG_TS_CSV = True
        elif flag == "-c":
            i = i + 1
            CMD_LIST = flagList[i].split(";")
            CMD_LIST = map(str.strip, CMD_LIST)

        i = i + 1


BUF_OUT = bytearray()
def PreprocessOutput(byteList):
    global BUF_OUT

    BUF_OUT.extend(byteList)

def HasWholeLine():
    global BUF_OUT

    retVal = False

    partList = BUF_OUT.split(b'\n')

    if len(partList) > 1:
        retVal = True

    return retVal


# Escape sequence looks like
# <27>[31m (so 5 bytes)
def StripControlSequences(stripMe):
    esc = chr(27)

    strRemaining = stripMe

    while esc in strRemaining:
        idx = strRemaining.find(esc)

        strRemaining = strRemaining[0:idx] + strRemaining[idx + 5:]

    return strRemaining


def GetNextWholeLine():
    global BUF_OUT

    line     = ""
    partList = BUF_OUT.split(b'\n')

    if len(partList) > 1:
        for b in partList[0]:
            try:
                bConverted = "".join(map(chr, [b]))

                line = line + bConverted
            except:
                pass

        # prevent control characters from getting to log files
        # this would likely be from coloring output
        # going to the terminal is ok, though, so we check if it's a terminal
        # that the output is headed for
        if not sys.stdout.isatty():
            line = StripControlSequences(line)

        BUF_OUT = BUF_OUT[len(partList[0]) + 1:]

    return line


def PreprocessInput(byteList):
    global FLAG_NNL
    global FLAG_NTOR

    byteListNew = bytearray()

    useByte = True

    for byte in byteList:
        useByte = True

        if FLAG_NNL:
            if byte == "\n":
                useByte = False

        if FLAG_NTOR:
            if byte == "\n":
                byte = "\r"

        if useByte:
            byteListNew.append(byte)

    return byteListNew


def Main():
    global CMD_LIST

    argList, flagList = GroupArgs(sys.argv)

    ProcessFlags(flagList)

    if len(argList) < 2 or len(argList) > 4:
        print("Usage: "   +
              os.path.basename(sys.argv[0]) +
              " <bcPinRx> [<bcPinTx=->] [<baud=9600>] [-ntor]")
        print("    bcPinRx can be - if not in use (write only)")
        print("    bcPinTx can be - if not in use (read only)")
        print("    use -nnl flag to strip off trailing \\n")
        print("    use -ntor flag to convert \\n to \\r")
        print("    use -ts flag to timestamp each line")
        print("    use -tsCsv flag to timestamp each line, separated by comma")
        print("    use -c to specify (;)delimited cmd list to send on startup")
        sys.exit(-1)

    # set default arguments
    bcPinRx = argList[1]
    bcPinTx = "-"
    baud    = 9600

    if len(argList) > 2:
        bcPinTx = argList[2]

        if len(argList) > 3:
            baud = argList[3]

    # parse arguments
    bcPinRx = None if bcPinRx == "-" else int(bcPinRx)
    bcPinTx = None if bcPinTx == "-" else int(bcPinTx)
    baud    = int(baud)

    # create serial comms object
    ser = SerialRaw(bcPinRx, bcPinTx, baud, 5)

    # create callbacks
    def OnSerialReadable(byteList):
        global FLAG_TS
        global FLAG_TS_CSV
        global BUF_OUT

        lineBuffered = True
        if sys.stdout.isatty():
            lineBuffered = False

        if lineBuffered or FLAG_TS or FLAG_TS_CSV:
            PreprocessOutput(byteList)            

            while HasWholeLine():
                line = GetNextWholeLine()

                if FLAG_TS:
                    Log(line)
                elif FLAG_TS_CSV:
                    LogCsv(line)
                else:
                    sys.stdout.write(line)
                    sys.stdout.write("\n")
                    sys.stdout.flush()
        else:
            data = ""
            try:
                data = byteList.decode()
            except:
                pass

            sys.stdout.write(data)
            sys.stdout.flush()

    def OnKeyboardReadable(byteList):
        byteList = PreprocessInput(byteList.encode())

        if len(byteList):
            ser.Send(byteList)

    # register callbacks
    ser.SetCbOnRxAvailable(OnSerialReadable)
    WatchStdinEndLoopOnEOF(OnKeyboardReadable, binary=True)

    # pass along any commands specified
    if bcPinTx:
        for cmd in CMD_LIST:
            print(cmd)
            ser.Send(cmd + "\n")

    evm_MainLoop()

    ser.Stop()


Main()



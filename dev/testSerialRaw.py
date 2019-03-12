#!/usr/bin/python -u

import sys
import os
import time

import pigpio

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.serial import *


def GroupArgs(argv):
    argList  = []
    flagList = []

    if len(argv):
        for arg in argv:
            if arg[0] == "-" and arg != "-":
                flagList.append(arg)
            else:
                argList.append(arg)

    return (argList, flagList)


FLAG_NNL  = False
FLAG_NTOR = False
FLAG_TS   = False
FLAG_TS_CSV = False
def ProcessFlags(flagList):
    global FLAG_NNL
    global FLAG_NTOR
    global FLAG_TS
    global FLAG_TS_CSV

    for flag in flagList:
        if flag == "-nnl":
            FLAG_NNL = True
        elif flag == "-ntor":
            FLAG_NTOR = True
        elif flag == "-ts":
            FLAG_TS = True
        elif flag == "-tsCsv":
            FLAG_TS_CSV = True



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
            byteListNew.extend(byte)

    return byteListNew


def Main():
    argList, flagList = GroupArgs(sys.argv)

    ProcessFlags(flagList)

    if len(argList) < 2 or len(argList) > 4:
        print("Usage: "   +
              sys.argv[0] +
              " <bcPinRx> [<bcPinTx=->] [<baud=9600>] [-ntor]")
        print("    bcPinRx can be - if not in use (write only)")
        print("    bcPinTx can be - if not in use (read only)")
        print("    use -nnl flag to strip off trailing \\n")
        print("    use -ntor flag to convert \\n to \\r")
        print("    use -ts flag to timestamp each line")
        print("    use -tsCsv flag to timestamp each line, separated by comma")
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

        if FLAG_TS or FLAG_TS_CSV:
            PreprocessOutput(byteList)            

            while HasWholeLine():
                line = GetNextWholeLine()

                if FLAG_TS:
                    Log(line)
                else:
                    LogCsv(line)
        else:
            sys.stdout.write(byteList)
            sys.stdout.flush()

    def OnKeyboardReadable(byteList):
        byteList = PreprocessInput(byteList)

        if len(byteList):
            ser.Send(byteList)

    # register callbacks
    ser.SetCbOnRxAvailable(OnSerialReadable)
    WatchStdinEndLoopOnEOF(OnKeyboardReadable, binary=True)

    evm_MainLoop()

    ser.Stop()


Main()



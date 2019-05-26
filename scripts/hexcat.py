#!/usr/bin/python

import signal
import string
import sys
import os

from struct import *


def OnDone():
    if len(LINE_BUFFER) != 0:
        sys.stdout.write("\n")


def ShowLine(byteStart, byteList):
    byteListLen = len(byteList)

    # bring cursor back to start of line
    sys.stdout.write("\r")

    # line number
    sys.stdout.write("{:08X}:".format(byteStart))

    # hex bytes
    for byte in byteList:
        sys.stdout.write(" {:02X}".format(byte))

    for i in range(8 - byteListLen):
        sys.stdout.write("   ")

    sys.stdout.write(" | ")

    # printable chars
    for byte in byteList:
        c = chr(byte)

        if c in string.digits or \
           c in string.letters or \
           c in string.punctuation or \
           c == " ":
            sys.stdout.write(c)
        else:
            sys.stdout.write(".")
            
    for i in range(8 - byteListLen):
        sys.stdout.write(" ")

    sys.stdout.flush()



BYTE_START  = 0
LINE_BUFFER = bytearray()

def OnByte(byte):
    global BYTE_START
    global LINE_BUFFER

    # add byte to buffer
    LINE_BUFFER.extend(byte)

    # display
    ShowLine(BYTE_START, LINE_BUFFER)

    # check if new line
    if len(LINE_BUFFER) == 8:
        BYTE_START += 8
        LINE_BUFFER = bytearray()

        sys.stdout.write("\n")
        sys.stdout.flush()


def HexCat(filename):
    fd = None
    if filename == "-":
        fd = sys.stdin
    else:
        fd = open(filename, "r")

    cont = 1
    while cont:
        byte = fd.read(1)

        if not byte:
            cont = 0
        else:
            OnByte(byte)

    OnDone()


def SetupSignalHandler():
    def SignalHandler(signal, frame):
        OnDone()
        sys.exit(0)

    # handle ctl-c
    signal.signal(signal.SIGINT, SignalHandler)


def Main():
    if len(sys.argv) != 2:
        print("Usage: " + (os.path.basename(sys.argv[0]) + " <file>")
        print("    use '-' for stdin")
        sys.exit(-1)

    filename = sys.argv[1] 

    SetupSignalHandler()
    HexCat(filename)


Main()




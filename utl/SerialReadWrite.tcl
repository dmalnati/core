#!/usr/bin/env python

import time 
import sys
import serial
import string


baud = 600
serialPort = None

def IsPrintable(str):
    printset = set(string.printable)
    isprintable = set(str).issubset(printset)
    
    return isprintable

def WriteToSerial():
    while True:
        line    = sys.stdin.readline()
        lineLen = len(line)
        
        if lineLen == 0:
            # stdin closed, end it all
            break
        else:
            # Print intentionally poorly-formatted strings that will be discarded
            # on the receiving side.  This primes the receiver chip to get the
            # automatic gain control ready to know noise from signal.
            serialPort.write('\0');
            serialPort.write('\n');
            serialPort.flush()
            serialPort.write('\0');
            serialPort.write('\n');
            serialPort.flush()
            serialPort.write('\0');
            serialPort.write('\n');
            serialPort.flush()
            
            # write the actual data.
            #print "Writing to serial [" + str(lineLen) + " bytes]: " + line
            print line[0:lineLen-1]
            sys.stdout.flush()
            serialPort.write(line)
            serialPort.flush()
            

def ReadFromSerial():
    while True:
        line = serialPort.readline()
        
        if IsPrintable(line):
            lineLen = len(line)
            
            serialPort.reset_input_buffer()

            #print "Read from serial [" + str(lineLen) + " bytes]: " + line
            print line[0:lineLen-1]
            sys.stdout.flush()


def Main():
    global baud
    global serialPort

    # Assume arguments are ok to begin with
    argsOk = True

    # Confirm that arguments look ok
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        argsOk = False
    else:
        if sys.argv[1] != "read" and sys.argv[1] != "write":
            argsOk = False

    # If arguments weren't ok, complain and quit, otherwise proceed
    if argsOk != True:
        print "Usage: " + sys.argv[0] + " <read|write> [<baud>]"
        sys.exit(-1)
    else:
        readOrWrite = sys.argv[1]

    # default baud to 600
    baud = 600
    if len(sys.argv) == 3:
        baud = int(sys.argv[2])
        
        # Create serial interface
        serialPort = serial.Serial(
#            port='/dev/ttyS0',
            port='/dev/ttyAMA0',
            baudrate = baud,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )
        

    if readOrWrite == "read":
        ReadFromSerial()
    else: 
        WriteToSerial()





try:
    Main()
except KeyboardInterrupt:
    pass

if serialPort != None:
    serialPort.close()        







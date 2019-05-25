#!/usr/bin/env python

import time 
import sys
import select
import serial
import string



#
# API used for sys.stdin.* (IO module)
# https://docs.python.org/3/library/io.html#module-io
#   readable()
#
# API used for 
# http://pyserial.readthedocs.io/en/latest/pyserial_api.html
# http://pyserial.readthedocs.io/en/latest/shortintro.html#readline
#   in_waiting()
#



serialPort = None

def IsPrintable(str):
    printset = set(string.printable)
    isprintable = set(str).issubset(printset)
    
    return isprintable



def Communicate():
    global serialPort

    while True:
        if serialPort.inWaiting():
#        if serialPort.in_waiting:
            line = serialPort.readline()

            if IsPrintable(line):
#                serialPort.reset_input_buffer()

                lineLen = len(line)
                print line[0:lineLen-1]
                sys.stdout.flush()

#        elif sys.stdin.readable():
        elif select.select([sys.stdin,],[],[],0.0)[0]:
            line = sys.stdin.readline()
            lineLen = len(line)

            print line[0:lineLen-1]
            sys.stdout.flush()

            serialPort.write(line)
            serialPort.flush()

        time.sleep(0.10)





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
    global serialPort

    # Assume arguments are ok to begin with
    argsOk = True

    # Confirm that arguments look ok
    if len(sys.argv) != 1 and len(sys.argv) != 2:
        argsOk = False

    # If arguments weren't ok, complain and quit, otherwise proceed
    if argsOk != True:
        print "Usage: " + sys.argv[0] + " [<baud>]"
        sys.exit(-1)

    # default baud to 600
    baud = 9600
    if len(sys.argv) == 2:
        baud = int(sys.argv[1])
        
    # Create serial interface
    serialPort = serial.Serial(
#        port='/dev/ttyS0',
        port='/dev/ttyAMA0',
        baudrate = baud,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS
    )

    Communicate()




try:
    Main()
except KeyboardInterrupt:
    pass

if serialPort != None:
    serialPort.close()        







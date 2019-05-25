import fcntl
import os
import signal
import sys
import time


import tornado.ioloop
from tornado import gen


#######################################################################
#
# Event Manager
#
#######################################################################

def evm_PeriodicCallback(cbFn, msTimeout):
    tornado.ioloop.PeriodicCallback(cbFn, msTimeout).start()

def evm_SetTimeout(cbFn, msTimeout):
    deadline = time.time() + (float(msTimeout) / 1000)
    handle = tornado.ioloop.IOLoop.instance().add_timeout(deadline, cbFn)
    return handle

def evm_CancelTimeout(handle):
    tornado.ioloop.IOLoop.instance().remove_timeout(handle)

def evm_MainLoopFinish():
    tornado.ioloop.IOLoop.instance().stop()

def evm_MainLoop(stopOnCtlC=True):
    if stopOnCtlC:
        def SignalHandler(signal, frame):
            evm_MainLoopFinish()

        signal.signal(signal.SIGINT, SignalHandler)

    tornado.ioloop.IOLoop.instance().start()


#######################################################################
#
# Keyboard interface
#
#######################################################################

def HandleSignals():
    def SignalHandler(signal, frame):
        sys.exit(0);

    # handle ctl-c
    signal.signal(signal.SIGINT, SignalHandler)

def WatchStdinRaw(cbFn):
    def Handler(fd, events):
        cbFn()

    loop = tornado.ioloop.IOLoop.instance()
    loop.add_handler(sys.stdin, Handler, tornado.ioloop.IOLoop.READ)

def WatchStdin(cbFn, binary=False):
    def Handler():
        line = ""

        if binary:
            line = sys.stdin.read()
        else:
            line = sys.stdin.readline()

        closed = False

        if not line:
            closed = True
        else:
            if not binary:
                line = line.rstrip("\n")

        cbFn(closed, line)

    if binary:
        fd = sys.stdin.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    WatchStdinRaw(Handler)

def WatchStdinEndLoopOnEOF(cbFn, binary=False):
    def Handler(closed, line):
        if not closed:
            cbFn(line)
        else:
            evm_MainLoopFinish()

    WatchStdin(Handler, binary)

def WatchStdinLinesEndLoopOnEOF(cbFn, binary=False):
    def OnStdIn(inputStr):
        inputStr = inputStr.strip()

        if inputStr != "":
            cbFn(inputStr)
            
    WatchStdinEndLoopOnEOF(OnStdIn, binary)



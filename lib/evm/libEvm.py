import fcntl
import os
import signal
import sys
import time

import fcntl
import subprocess

from libUtl import *

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

def evm_MainLoop():
    def SignalHandler(signal, frame):
        loop = tornado.ioloop.IOLoop.instance()
        loop.add_callback_from_signal(evm_MainLoopFinish)

    signal.signal(signal.SIGINT, SignalHandler)

    def SignalHandlerTerm(signal, frame):
        Log("Terminated, quitting")
        loop = tornado.ioloop.IOLoop.instance()
        loop.add_callback_from_signal(evm_MainLoopFinish)

    signal.signal(signal.SIGTERM, SignalHandlerTerm)

    # tornado catches exceptions and logs but never raises them further.
    # this leads to applications dying and never quitting, hiding the issue.
    # here I intercept those logging calls and do the quitting myself
    tornadoAppLogError = tornado.log.app_log.error
    def MyAppLogError(*args, **kwargs):
        tornadoAppLogError(*args, **kwargs)

        if args[0].find("Exception") != -1:
            Log("Intercepted uncaught exception, exiting")
            sys.exit(1)
    tornado.log.app_log.error = MyAppLogError

    tornadoGenLogError = tornado.log.gen_log.error
    def MyGenLogError(*args, **kwargs):
        tornadoAppLogError(*args, **kwargs)
        if args[0].find("Exception") != -1:
            Log("Intercepted uncaught exception, exiting")
            sys.exit(1)
    tornado.log.gen_log.error = MyGenLogError

    # start handling events
    tornado.ioloop.IOLoop.instance().start()



# expect to get async buffers back, until closed, then get None.
# returns a handle you can stop watching with.
def evm_WatchCommand(handler, cmd):
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)

    def Handler(fd):
        bufTotal = ""

        READ_SIZE = 8192
        buf = fd.read(READ_SIZE)
        while buf and len(buf) == READ_SIZE:
            bufTotal += buf.decode()

            buf = fd.read(READ_SIZE)
        if buf:
            bufTotal += buf.decode()

        if len(bufTotal) == 0:
            evm_UnWatchFd(fd)
            process.wait()
            handler(None)
        else:
            handler(bufTotal)

    evm_WatchFd(Handler, process.stdout)

    return process


def evm_UnWatchCommand(handle):
    process = handle

    evm_UnWatchFd(process.stdout)
    process.kill()


# assumes you want async
def evm_WatchFd(handler, fd):
    def Handler(fd, events):
        handler(fd)

    # make non-blocking
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    # add to fd monitoring
    loop = tornado.ioloop.IOLoop.instance()
    loop.add_handler(fd, Handler, tornado.ioloop.IOLoop.READ)


def evm_UnWatchFd(fd):
    loop = tornado.ioloop.IOLoop.instance()
    loop.remove_handler(fd)
    


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



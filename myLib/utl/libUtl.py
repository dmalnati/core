import signal
import sys
import time
import datetime

import json

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

def WatchStdin(cbFn):
    def Handler():
        line   = sys.stdin.readline()
        closed = False

        if not line:
            closed = True
        else:
            line = line.rstrip("\n")

        cbFn(closed, line)

    WatchStdinRaw(Handler)

def WatchStdinEndLoopOnEOF(cbFn):
    def Handler(closed, line):
        if not closed:
            cbFn(line)
        else:
            evm_MainLoopFinish()

    WatchStdin(Handler)


#######################################################################
#
# Utility
#
#######################################################################

def TimeNow():
    return datetime.datetime.now().time().isoformat()

def Log(msg):
    print("[" + str(TimeNow()) + "]: " + msg)


def GetPrettyJSON(jsonObj):
    return json.dumps(jsonObj,
                      sort_keys=True,
                      indent=4,
                      separators=(',', ': '))

















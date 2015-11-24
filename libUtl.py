import signal
import sys
import time
import datetime

import tornado.ioloop
from tornado import gen


def evm_PeriodicCallback(cbFn, msTimeout):
    tornado.ioloop.PeriodicCallback(cbFn, msTimeout).start()

def evm_SetTimeout(cbFn, msTimeout):
    deadline = time.time() + (float(msTimeout) / 1000)
    handle = tornado.ioloop.IOLoop.instance().add_timeout(deadline, cbFn)
    return handle

def evm_CancelTimeout(handle):
    tornado.ioloop.IOLoop.instance().remove_timeout(handle)

def evm_MainLoop():
    tornado.ioloop.IOLoop.instance().start()

def SignalHandler(signal, frame):
    print "Exiting via Ctl+C"
    sys.exit(0);

def HandleSignals():
    # handle ctl-c
    signal.signal(signal.SIGINT, SignalHandler)


def HandleStdin(cbFn):
    def Handler(fd, events):
        line = sys.stdin.readline()
        cbFn(line)

    loop = tornado.ioloop.IOLoop.instance()
    loop.add_handler(sys.stdin, Handler, tornado.ioloop.IOLoop.READ)





def TimeNow():
    return datetime.datetime.now().time().isoformat()

def Log(msg):
    print("[" + str(TimeNow()) + "]: " + msg)




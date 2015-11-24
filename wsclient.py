#!/usr/bin/python

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
from tornado import gen
import os
import json
import signal
import sys
import time

from collections import deque
 
def SignalHandler(signal, frame):
    print "Exiting via Ctl+C"
    sys.exit(0);


@gen.coroutine
def Connect(url):
    conn = yield tornado.websocket.websocket_connect(url)
    print("got %s" % ( conn ))

    conn.write_message(json.dumps({
        "MESSAGE_TYPE" : "REQ_LOGIN",
        "USER_NAME"    : "vooleroo",
        "PASSWORD"     : "BBQ"
    }))

    conn.write_message(json.dumps({
        "MESSAGE_TYPE" : "REQ_SEND_CHAT_MESSAGE",
        "USER_NAME"    : "vooleroo",
        "PASSWORD"     : "BBQ",
        "TIMESTAMP"    : 1448120502011,
        "MESSAGE"      : "look at me I'm automated"
    }))

    while True:
        msg = yield conn.read_message()
        if msg is None:
            print("other side closed connection")
            break
        print("got message: %s" % (msg))
        #print("about to close")
        #conn.close()
        #print("closed it")



def Main():
    print "five"
    # handle ctl-c
    signal.signal(signal.SIGINT, SignalHandler)
    print "six"

    print("installed signal handler")

    print("about to call connect")
    url = sys.argv[1]
    print ("Connecting to url: " + url)
    Connect(url)
    print("after connect call")
    
    tornado.ioloop.IOLoop.instance().start()
    
    print("ending")



print("Before Main")
Main()
print("After Main")

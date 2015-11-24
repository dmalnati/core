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
import datetime

from collections import deque
 
def SignalHandler(signal, frame):
    print "Exiting via Ctl+C"
    sys.exit(0);


class WSBaseClass():
    @staticmethod
    @gen.coroutine
    def Connect(ws, url):
        try:
            conn = yield tornado.websocket.websocket_connect(url)
        except:
            ws.on_error()
            return

        ws.set_conn(conn)
        ws.on_connect()

        while True:
            msg = yield conn.read_message()
            if msg is None:
                ws.on_close()
                break
            ws.on_message(msg)

    def __init__(self, url):
        self.url  = url
        self.conn = None

    # basically a private function to be called by Connect
    def set_conn(self, conn):
        self.conn = conn

    def connect(self):
        WSBaseClass.Connect(self, self.url)

    def close(self):
        self.conn.close()

    def on_connect(self):
        pass

    def on_message(self, msg):
        pass

    def on_close(self):
        pass

    def on_error(self):
        pass




class MyWS(WSBaseClass):
    def __init__(self, url, user):
        WSBaseClass.__init__(self, url)

        self.user = user

    def on_connect(self):
        print("on_connect: " + self.user + "@" + self.url)

        self.conn.write_message(json.dumps({
            "MESSAGE_TYPE" : "REQ_LOGIN",
            "USER_NAME"    : self.user,
            "PASSWORD"     : "BBQ"
        }))

        self.conn.write_message(json.dumps({
            "MESSAGE_TYPE" : "REQ_SEND_CHAT_MESSAGE",
            "USER_NAME"    : self.user,
            "PASSWORD"     : "BBQ",
            "TIMESTAMP"    : 1448120502011,
            "MESSAGE"      : "name: " + self.user
        }))

    def on_message(self, msg):
        print("on_message: " + self.user + "@" + self.url + ", msg: " + msg)

    def on_close(self):
        print("on_close: " + self.user + "@" + self.url)

    def on_error(self):
        print("on_error: " + self.user + "@" + self.url)

    def get_id(self):
        return self.user + "@" + self.url



def TimeNow():
    return datetime.datetime.now().time().isoformat()

def Log(msg):
    print("[" + str(TimeNow()) + "]: " + msg)

def SetUpTimer(msTimeout):
    print("Setting up interval timer for " + str(msTimeout) + "ms")

    def Timeout():
        Log("Timeout")

    tornado.ioloop.PeriodicCallback(Timeout, msTimeout).start()


def Main():
    url = sys.argv[1]

    # handle ctl-c
    signal.signal(signal.SIGINT, SignalHandler)

    SetUpTimer(1000)

    print ("Connecting to url: " + url)
    ws = MyWS(url, "auto1")
    ws.connect()
    
    tornado.ioloop.IOLoop.instance().start()


Main()

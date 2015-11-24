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



class WS():
    @staticmethod
    def GetConnectingWs(url, user):
        ws = WS(url, user)
        WS.Connect(ws, url, user)
        return ws

    @staticmethod
    @gen.coroutine
    def Connect(ws, url, user):
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

    def __init__(self, url, user):
        self.url = url
        self.user = user

    def set_conn(self, conn):
        self.conn = conn

    def close(self):
        self.conn.close()

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

class WS2():
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

    def __init__(self, url, user):
        self.url = url
        self.user = user

    def connect(self):
        WS2.Connect(self, self.url)

    def set_conn(self, conn):
        self.conn = conn

    def close(self):
        self.conn.close()

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


class MyWS(WS2):
    def on_message(self, msg):
        print("SUBCLASS MSG!!!")





def Main():
    print "five"
    # handle ctl-c
    signal.signal(signal.SIGINT, SignalHandler)
    print "six"

    print("installed signal handler")

    print("about to call connect")
    url = sys.argv[1]
    print ("Connecting to url: " + url)
    #Connect(url, "auto1")
    #ws = WS.GetConnectingWs(url, "auto1")
#    ws = MyWS.GetConnectingWs(url, "auto1")

    #ws = WS2(url, "auto1")
    ws = MyWS(url, "auto1")
    ws.connect()

    print("Got a WS back, and it is named: " + ws.get_id())
#    Connect(url, "auto2")
    print("after connect call")
    
    tornado.ioloop.IOLoop.instance().start()
    
    print("ending")



print("Before Main")
Main()
print("After Main")

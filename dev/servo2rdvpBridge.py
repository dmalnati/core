#!/usr/bin/python

import sys
import os

import subprocess

import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *
from myLib.ws import *



class Handler(WSBridgeLoggerIface, WSBridge):
    def __init__(self, urlWs, urlRDVPServer, clientId, password):
        WSBridgeLoggerIface.__init__(self)
        WSBridge.__init__(self, urlWs, urlRDVPServer)

        self.clientId = clientId
        self.password = password

    def OnBridgeUp(self):
        Log("Bridge Up, logging on as " + self.clientId +
            ", password " + self.password)

        self.GetWsSecond().Write(json.dumps({
            "MESSAGE_TYPE"       : "REQ_LOGIN_SC",
            "ID"                 : self.clientId,
            "PASSWORD"           : self.password
        }))


    def OnStartOrRestart(self):
        # kill any running uv4l procs
        Log("Killing any running servoNode procs")
        subprocess.call("ps -ef | grep servoNode | grep sudo | grep -v grep | awk '{ print $2 }' | sudo xargs kill",shell=True)

        # start it up again
        Log("Starting servoNode")
        subprocess.call("sudo /home/pi/py/demo/servoNode.py 1500 / &",shell=True)

        time.sleep(2)



def Main():
    if len(sys.argv) != 5:
        print("Usage: " + sys.argv[0] +
              " <urlWs> <urlRDVPServer> <clientId> <password>")
        sys.exit(-1)

    urlWs         = sys.argv[1]
    urlRDVPServer = sys.argv[2]
    clientId      = sys.argv[3]
    password      = sys.argv[4]

    b = Handler(urlWs, urlRDVPServer, clientId, password)
    Log("Bridge Starting: (" + urlWs + ", " + urlRDVPServer + ")")
    b.Start()

    evm_MainLoop()


Main()

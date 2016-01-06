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

    def GetWsUV4L(self):
        return self.GetWsFirst()

    def GetWsRDVP(self):
        return self.GetWsSecond()

    def OnBridgeUp(self):
        Log("Bridge Up, logging on as " + self.clientId +
            ", password " + self.password)

        self.GetWsRDVP().Write(json.dumps({
            "MESSAGE_TYPE"       : "REQ_LOGIN_SC",
            "ID"                 : self.clientId,
            "PASSWORD"           : self.password,
            "EVENT_ON_BRIDGE_UP" : 1
        }))


    #
    # This is the UV4L <- RDVP converter
    #
    def OnMessageFromSecondToFirst(self, msg):
        try:
            jsonObj = json.loads(msg)
        except:
            Log("Unknown non-JSON message received from RDVP, not forwarding")
            print(msg)
        else:
            self.OnMessageFromRDVPToUV4L(jsonObj)

    def OnMessageFromRDVPToUV4L(self, jsonObj):
        messageType = jsonObj["MESSAGE_TYPE"]

        wsUV4L = self.GetWsUV4L()
        wsRDVP = self.GetWsRDVP()

        if messageType == "EVENT_BRIDGE_UP":
            # we knows someone connected, so provoke UV4L to make an offer
            # which we will relay
            wsUV4L.Write(json.dumps({
                "command_id" : "offer"
            }))
        elif messageType == "WEBRTC_SDP_DESCRIPTION":
            wsUV4L.Write(json.dumps({
                "command_id" : "answer",
                "data"       : json.dumps({
                    "sdp"  : jsonObj["SDP"],
                    "type" : jsonObj["TYPE"]
                })
            }))
        elif messageType == "WEBRTC_ADD_ICE_CANDIDATE":
            wsUV4L.Write(json.dumps({
                "command_id" : "addicecandidate",
                "data"       : json.dumps({
                    "candidate"     : jsonObj["CANDIDATE"],
                    "sdpMLineIndex" : jsonObj["SDP_MLINE_INDEX"],
                    "sdpMid"        : jsonObj["SDP_MID"],
                })
            }))
        else:
            Log("Unknown message received from RDVP, not forwarding")
            print(GetPrettyJSON(jsonObj))

        return None

    #
    # This is the UV4L -> RDVP converter
    #
    def OnMessageFromFirstToSecond(self, msg):
        try:
            jsonObj = json.loads(msg)
        except:
            Log("Unknown non-JSON message received from UV4L, not forwarding")
            print(msg)
        else:
            self.OnMessageFromUV4LToRDVP(jsonObj)

    def OnMessageFromUV4LToRDVP(self, jsonObj):
        messageType = jsonObj["type"]

        wsUV4L = self.GetWsUV4L()
        wsRDVP = self.GetWsRDVP()

        if messageType == "offer":
            # we relay the UV4L offer, but convert message format
            # the sdp text is plaintext, and appropriate to send as-is
            wsRDVP.Write(json.dumps({
                "MESSAGE_TYPE" : "WEBRTC_SDP_DESCRIPTION",
                "SDP"          : jsonObj["sdp"],
                "TYPE"         : jsonObj["type"]
            }))

            # we additionally issue the command to UV4L to get its
            # ICE candidates at this time.
            # this mimics the behavior that ships with UV4L javascript
            wsUV4L.Write(json.dumps({
                "command_id" : "geticecandidate"
            }))
        elif messageType == "geticecandidate":
            # we relay the UV4L ice candidates
            # they are all bundled together in a single message, so we
            # break them apart and send individually

            candidateObjList = json.loads(jsonObj["data"])
            for candidateObj in candidateObjList:
                wsRDVP.Write(json.dumps({
                    "MESSAGE_TYPE"    : "WEBRTC_ADD_ICE_CANDIDATE",
                    "CANDIDATE"       : candidateObj["candidate"],
                    "SDP_MLINE_INDEX" : candidateObj["sdpMLineIndex"],
                    "SDP_MID"         : candidateObj["sdpMid"]
                }))
        elif messageType == "message":
            Log("Message from UV4L: " + jsonObj["data"])
        else:
            Log("Unknown message received from UV4L, not forwarding")
            print(GetPrettyJSON(jsonObj))

        return None

    def OnStartOrRestart(self):
        # kill any running uv4l procs
        Log("Killing any running UV4L procs")
        subprocess.call("sudo killall uv4l",shell=True)        

        # start it up again
        Log("Starting UV4L")
        #subprocess.call("sudo /usr/bin/uv4l -f --auto-video_nr yes -k --sched-rr --mem-lock  --driver uvc --device-id 046d:0990 --server-option '--port=9000' &",shell=True)
        subprocess.call("uv4l --foreground --auto-video_nr yes --driver uvc --device-id 046d:0990  --server-option='--port=9000' --server-option='--webrtc-cpu-overuse-detection=no' --server-option='--enable-webrtc-audio=no' --server-option='--webrtc-receive-audio=no' &",shell=True)

        time.sleep(5)



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

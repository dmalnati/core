


//////////////////////////////////////////////////////////////////////////
//
// WebRTC functionality
//
//////////////////////////////////////////////////////////////////////////


function WebRTC_GetICEConfiguration()
{
    var configuration = {
        iceServers: [
            {"url": "stun:stun.l.google.com:19302"},
            {"url": "stun:stun1.l.google.com:19302"},
            {"url": "stun:stun2.l.google.com:19302"},
            {"url": "stun:stun3.l.google.com:19302"},
            {"url": "stun:stun4.l.google.com:19302"}
        ]
    };

    return configuration;
}





//
// Assume:
// - ws already fired onopen and logged in and good
// - mediaStream already approved and ready
// - the other side of the websocket will make the offer
//
function WebRTC_Receiver(ws, mediaStream, cbObj)
{
    var t = this;




    // Deal with prefixed implementations
    RTCPeerConnection     = window.mozRTCPeerConnection ||
                            window.webkitRTCPeerConnection;
    RTCSessionDescription = window.mozRTCSessionDescription ||
                            window.RTCSessionDescription;
    RTCIceCandidate       = window.mozRTCIceCandidate ||
                            window.RTCIceCandidate;




    // Get configuration for peer connection
    var cfgPc = WebRTC_GetICEConfiguration();
    
    // Actually create a peer connection
    pc = new RTCPeerConnection(cfgPc);

    // Make the peer connection aware of local stream
    if (mediaStream)
    {
        pc.addStream(mediaStream);
    }




    // Set up listeners to the peer connection
    pc.onicecandidate = function(evt) {
        // Send it to the other side
        if (evt.candidate)
        {
            ws.send(JSON.stringify({
                "MESSAGE_TYPE"    : "WEBRTC_ADD_ICE_CANDIDATE",
                "CANDIDATE"       : evt.candidate.candidate,
                "SDP_MLINE_INDEX" : evt.candidate.sdpMLineIndex,
                "SDP_MID"         : evt.candidate.sdpMid
            }));
        }
    }

    pc.onaddstream = function(evt) {
        cbObj.OnStreamAdded(evt.stream);
    }

    pc.onremovestream = function(evt) {
        cbObj.OnStreamRemoved();
    }







    // Set up listeners to the signaling system
    ws.onmessage = function(evt) {
        var jsonObj = JSON.parse(evt.data);

        var messageType = jsonObj["MESSAGE_TYPE"]

        if (messageType == "WEBRTC_SDP_DESCRIPTION")
        {
            var sdpDescription = {
                sdp  : jsonObj["SDP"],
                type : jsonObj["TYPE"]
            };

            var errStr = null;

            pc.setRemoteDescription(
                new RTCSessionDescription(sdpDescription),
                function OnSuccess() {
                    console.log("SUCCESS - setRemoteDescription");
                    // then create answer.
                    pc.createAnswer(
                        function OnLocalDescriptionAvailable(nativeLocalDescription) {
                            console.log("SUCCESS - createAnswer");

                            pc.setLocalDescription(
                                nativeLocalDescription,
                                function OnSuccess() {
                                    console.log("SUCCESS - setLocalDescription");
                                    // should now send this description to
                                    //other side
                                    ws.send(JSON.stringify({
                                        "MESSAGE_TYPE" :
                                            "WEBRTC_SDP_DESCRIPTION",
                                        "SDP"  : pc.localDescription.sdp,
                                        "TYPE" : pc.localDescription.type
                                    }));
                                }, function OnError() {
                                    errStr = "FAILURE - setLocalDescription";
                                }
                            )
                        }, function OnError() {
                            errStr = "FAILURE - createAnswer";
                        }
                    )
                }, function OnError() {
                    errStr = "FAILURE - setRemoteDescription";
                }
            );

            if (errStr)
            {
                console.log(errStr);

                ws.close();
            }
        }
        else if (messageType == "WEBRTC_ADD_ICE_CANDIDATE")
        {
            candidate = new RTCIceCandidate({
                candidate     : jsonObj["CANDIDATE"],
                sdpMLineIndex : jsonObj["SDP_MLINE_INDEX"],
                sdpMid        : jsonObj["SDP_MID"]
            });

            pc.addIceCandidate(candidate, function() {}, function() {});
        }
        else
        {
            console.log("Unknown message type: " + messageType);
            console.log("msg: " + evt.data);
        }
    }

    ws.onclose = function() {
        cbObj.OnStreamRemoved();
        pc.close();
    }



    return {
        close : function() {
            pc.close();
        }
    }
}



























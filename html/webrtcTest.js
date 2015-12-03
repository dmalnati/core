

function Log(str)
{
    console.log(clientId + ": " + str);
}


////////////////////////////////////////////////////////////////////////
//
// 
//
////////////////////////////////////////////////////////////////////////

var ws = null;
var remoteSdpDescription = null;
var clientId = null;
function OnClickConnect()
{
    clientId = document.getElementById("clientId").value;
    connectToId = document.getElementById("connectToId").value;
    domStatusConnect = document.getElementById("statusConnect");

    var clientType = "";

    ws = null;
    if (connectToId == "")
    {
        clientType = "SC";
        ws = RDVP_WebSocketThisHost(clientType, clientId, "");
    }
    else
    {
        clientType = "CC";
        ws = RDVP_WebSocketThisHost(clientType, clientId, "", connectToId);
    }

    domStatusConnect.innerHTML = clientType + "...";
    ws.onopen = function()
    {
        domStatusConnect.innerHTML = clientType + "... OK";
    }

    var count = 0;
    ws.onmessage = function(evt)
    {
        jsonObj = null;
        try {
            jsonObj = JSON.parse(evt.data);
        } catch (e) {
            Log("ERR: Couldn't JSON-parse msg(" + msg + ")");
            Log(msg);
            return;
        }
        Log("processing " + jsonObj["MESSAGE_TYPE"]);
        switch (jsonObj["MESSAGE_TYPE"])
        {
            case "EVENT_WEBRTC_REMOTE_SDP_DESCRIPTION":
            {
                remoteSdpDescription = jsonObj["SDP_DESCRIPTION"];
                break;
            }

            case "EVENT_WEBRTC_ADD_ICE_CANDIDATE":
            {
                iceCandidateListRemote.push(jsonObj["CANDIDATE"]);
                break;
            }

            default:
            {
                break;
            }
        }
    }

    ws.onclose = function()
    {
        domStatusConnect.innerHTML = clientType + "... Closed";
    }

    ws.onerror = function()
    {
        domStatusConnect.innerHTML = clientType + "... Error";
    }
}

function OnClickDisconnect()
{
    ws.close()

    document.getElementById("statusConnect").innerHTML = "Closed(by you)";
}



////////////////////////////////////////////////////////////////////////
//
// 
//
////////////////////////////////////////////////////////////////////////

function DumpMediaStreamTrack(track)
{
    console.log("kind      : " + track.kind);
    console.log("label     : " + track.label);
    console.log("id        : " + track.id);
    console.log("readyState: " + track.readyState);
    console.log("enabled   : " + track.enabled);
}

function DumpMediaStreamTrackList(trackList, header)
{
    console.log(header);
    console.log("len: " + trackList.length);

    var count = 0;
    for (var i = 0; i < trackList.length; ++i)
    {
        if (count)
        {
            console.log("");
        }
        ++count;

        DumpMediaStreamTrack(trackList[i]);
    }
}

function DumpMediaStream(mediaStream)
{
    console.log("Dumping Media Stream");

    console.log("label: " + mediaStream.label);

    console.log("");
    audioTrackList = mediaStream.getAudioTracks();
    DumpMediaStreamTrackList(audioTrackList, "----- getAudioTracks() -----");

    console.log("");
    videoTrackList = mediaStream.getVideoTracks();
    DumpMediaStreamTrackList(videoTrackList, "----- getVideoTracks() -----");

    console.log("");
    trackList = mediaStream.getTracks();
    DumpMediaStreamTrackList(trackList, "----- getTracks() -----");

}


var ms = null;
function OnClickGetUserMedia()
{
    var getAudio = document.getElementById("gumAudio").checked;
    var getVideo = document.getElementById("gumVideo").checked;

    var constraints = {
        audio: getAudio,
        video: getVideo
    };

    function OnSuccess(mediaStream)
    {
        Log("SUCCESS GetUserMedia");

        ms = mediaStream;

        OnLocalStream(ms);

        // DumpMediaStream(mediaStream);
    }

    function OnFailure(err)
    {
        Log("FAIL GetUserMedia: " + err);
    }

    navigator.getUserMedia = navigator.getUserMedia ||
                             navigator.webkitGetUserMedia;

    navigator.getUserMedia(constraints, OnSuccess, OnFailure);
}



////////////////////////////////////////////////////////////////////////
//
// 
//
////////////////////////////////////////////////////////////////////////


var pc = null;
var iceCandidateListSelf = [];
var iceCandidateListRemote = [];
function OnClickRTCPeerConnection()
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

    // var pc = null;
    pc = null;

    try {
        RTCPeerConnection = webkitRTCPeerConnection;
        pc = new RTCPeerConnection(configuration);

        Log("START RTCPeerConnection");
        Log("    state: " + pc.signalingState);
    } catch (e) {
        Log("RTC Peer Failure: " + e.message);
    }

    pc.onsignalingstatechange = function()
    {
        Log("RTCPeerConnection OnSignalingStateChange");
        Log("    state: " + pc.signalingState);
    }

    pc.onicecandidate = function(evt)
    {
        // Log("OnICECandidate");

        // have to check this, seems that possibly the last-in-the-series
        // of callbacks is null for this attribute.
        if (evt.candidate)
        {
            //Log(evt.candidate);

            iceCandidateListSelf.push(evt.candidate);
        }
    }

    pc.onnegotiationneeded = function()
    {
        Log("RTCPeerConnection OnNegotiationNeeded");
    }

    pc.onaddstream = function(evt)
    {
        Log("RTCPeerConnection OnAddStream");
        DumpMediaStream(evt.stream);

        OnWebRTCStream(evt.stream);
    }

}

function OnClickAddStream()
{
    Log("OnClickAddStream");
    pc.addStream(ms);
}

function OnClickCreateAndSendOffer()
{
    Log("CreateAndSendOffer");

    var configuration = {
        mandatory: {
            OfferToReceiveAudio: true,
            OfferToReceiveVideo: true
        }
    };

    pc.createOffer(
        function OnLocalDescriptionAvailable(nativeLocalDescription) {
            pc.setLocalDescription(
                nativeLocalDescription,

                function OnSuccess() {
                    Log("SUCCESS - setLocalDescription");

                    // should now send this description to other side
                    ws.send(JSON.stringify({
                        MESSAGE_TYPE    : "EVENT_WEBRTC_REMOTE_SDP_DESCRIPTION",
                        SDP_DESCRIPTION : pc.localDescription
                    }));

                }, function OnError() {
                    Log("FAILURE - setLocalDescription");
                })
        }, function OnError() {
            Log("FAILURE - createOffer");
        }, configuration)
}


function OnClickCreateAndSendAnswer()
{
    pc.setRemoteDescription(
        new RTCSessionDescription(remoteSdpDescription),
        function OnSuccess() {
            Log("SUCCESS - setRemoteDescription");
            // then create answer.
            pc.createAnswer(
                function OnLocalDescriptionAvailable(nativeLocalDescription) {
                    Log("SUCCESS - createAnswer");

                    pc.setLocalDescription(
                        nativeLocalDescription,

                        function OnSuccess() {
                            Log("SUCCESS - setLocalDescription");

                            // should now send this description to other side
                            ws.send(JSON.stringify({
                                MESSAGE_TYPE    : "EVENT_WEBRTC_REMOTE_SDP_DESCRIPTION",
                                SDP_DESCRIPTION : pc.localDescription
                            }));

                        }, function OnError() {
                            Log("FAILURE - setLocalDescription");
                        })


                }, function OnError() {
                    Log("FAILURE - createAnswer");
                })
        }, function OnError() {
            Log("FAILURE - setRemoteDescription");
        });
}

function OnClickProcessAnswer()
{
    pc.setRemoteDescription(
        new RTCSessionDescription(remoteSdpDescription),
        function OnSuccess() {
            Log("SUCCESS - setRemoteDescription");
        }, function OnError() {
            Log("FAILURE - setRemoteDescription");
        })
}

function OnClickSendMyIceCandidates()
{
    Log("===== OnClickSendMyIceCandidates =====");

    Log("    sending " + iceCandidateListSelf.length + " candidates");

    for (var i = 0; i < iceCandidateListSelf.length; ++i)
    {
        ws.send(JSON.stringify({
            MESSAGE_TYPE : "EVENT_WEBRTC_ADD_ICE_CANDIDATE",
            CANDIDATE    : iceCandidateListSelf[i]
        }));
    }
}


function OnClickProcessRemoteIceCandidates()
{
    Log("===== OnClickProcessRemoteIceCandidates =====");

    Log("    processing " +
                iceCandidateListRemote.length + " candidates");

    for (var i = 0; i < iceCandidateListRemote.length; ++i)
    {
        function OnSuccess()
        {
            Log("Successfully added ICE candidate");
        }

        function OnError(err)
        {
            Log("Could not add ICE candidate: " + msg);
        }

        pc.addIceCandidate(new RTCIceCandidate(iceCandidateListRemote[i]),
                           OnSuccess,
                           OnError);
    }
}









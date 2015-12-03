


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

function WebRTC_Initiatator(wsSignal, mediaStream)
{
    var t = this;

    var cfgPc = WebRTC_GetICEConfiguration();
    
    RTCPeerConnection = webkitRTCPeerConnection;
    pc = new RTCPeerConnection(cfgPc);

    
    // Add media which is available
    pc.addStream(mediaStream);

    // Create initiate creation of offer to other side

    var cfgCo = {
        mandatory: {
            OfferToReceiveAudio: true,
            OfferToReceiveVideo: true
        }
    };

    // Trigger the creation of a session description
    pc.createOffer(function OnSuccess(sessionDescription) {
        // record local session description
        pc.setLocalDescription(sessionDescription);

        // also send to other side for their need to record this info
        wsSignal.send(JSON.stringify({
            "MESSAGE_TYPE" : "EVENT_SESSION_DESCRIPTION",
            "SDP"          : sessionDescription
        }));
    }, function OnError(msg) {

        // nothing to do

    }, cfgCo);


    // handle candidates coming back
    // these arrive sporadically once createOffer has been called and either:
    // - mediaStream has already been added -and/or-
    // - createOffer had configuration offering to accept audio and/or video
    pc.onicecandidate = function(evt)
    {
        if (evt.candidate)
        {
            wsSignal.send(JSON.stringify({
                "MESSAGE_TYPE" : "EVENT_ICE_CANDIDATE",
                "SDP"          : evt.candidate
            }));
        }
    }


    // The final stage of WebRTC (I think) is this callback fires with the
    // now-WebRTC-handled stream of audio-and-or-video.
    pc.onaddstream = function(evt)
    {
        // what is in this object???
        // how to return to interested parties???
        var blob = URL.createObjectURL(evt.stream);
    }


}



























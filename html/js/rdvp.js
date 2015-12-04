


//////////////////////////////////////////////////////////////////////////
//
// RDVP functionality
//
//////////////////////////////////////////////////////////////////////////

function RDVP_WebSocketThisHost(clientType, clientId, password, connectToId)
{
    var browserUrl  = window.location.href;
    var arr         = browserUrl.split("/");
    var hostAndPort = arr[2];

    var wsUrl = "ws://" + hostAndPort + "/ws";

    return new RDVP_WebSocket(wsUrl,
                              clientType,
                              clientId,
                              password,
                              connectToId);
}

function RDVP_WebSocket(url, clientType, clientId, password, connectToId)
{
    var t = this;

    var ws = new WebSocket(url);

    // define some functions for this object just so something fires even
    // if the user doesn't define one of them.
    t.onopen    = function()    { };
    t.onmessage = function(evt) { };
    t.onclose   = function(evt) { };
    t.onerror   = function(evt) { };

    // define interfaces to use
    t.send  = function(msg) { ws.send(msg); }
    t.close = function()    { ws.close();   }

    // the functions which actually fire on real websocket events
    function myOnOpen()
    {
        // we slip in a RDVP login, the type depends on parameters
        if (connectToId)
        {
            ws.send(JSON.stringify({
                "MESSAGE_TYPE"  : "REQ_LOGIN_" + clientType,
                "ID"            : clientId,
                "PASSWORD"      : password,
                "CONNECT_TO_ID" : connectToId
            }));
        }
        else
        {
            ws.send(JSON.stringify({
                "MESSAGE_TYPE" : "REQ_LOGIN_" + clientType,
                "ID"           : clientId,
                "PASSWORD"     : password
            }));
        }

        t.onopen();
    }

    // pass-through
    function myOnMessage(evt) { t.onmessage(evt); }
    function myOnClose(evt)   { t.onclose(evt);   }
    function myOnError(evt)   { t.onerror(evt);   }

    // assign to real websocket
    ws.onopen    = myOnOpen;
    ws.onmessage = myOnMessage;
    ws.onclose   = myOnClose;
    ws.onerror   = myOnError;
}







//////////////////////////////////////////////////////////////////////////
//
// RDVP functionality planning
//
//////////////////////////////////////////////////////////////////////////


function RDVP_Manager()
{
    var t = this;
}



function ExpectedUse()
{
    mgr = new RDVP_Manager();

    // Scenario -- I want to connect to an SC which has a WebRTC stream
    mgr.EstablishAdminConnection().then(function() {
        mgr.GetClientSCList().then(function(scList) {
            if (scList.length)
            {
                sc = scList[0];

                // assume it has WebRTC capabilities
                mgr.GetWebRTCVideoStream(sc).then(function(stream) {
                    // success!
                });
            }
        });
    });



    // Scenario -- I want to advertise my WebRTC stream



}


























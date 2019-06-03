'use strict'


class WSEventHandler
{
    OnConnect(ws)
    {
    }
    
    OnMessage(ws, msg)
    {
    }
    
    OnClose(ws)
    {
    }
    
    OnError(ws)
    {
    }
}


class WS extends WebSocket
{
    constructor(handler, addr)
    {
        super(addr);
        
        this.handler = handler;
        this.addr    = addr;
    }
    
    Write(msg)
    {
        this.send(JSON.stringify(msg));
    }
    
    Close()
    {
        this.close();
    }
    
    OnOpen(event)
    {
        this.handler.OnConnect(this);
    }
    
    OnClose(event)
    {
        this.handler.OnClose(this);
    }
    
    OnMessage(event)
    {
        let msg = JSON.parse(event.data);

        this.handler.OnMessage(this, msg);
    }
    
    OnError(event)
    {
        this.handler.OnError(this);
    }
}


class WSManager
{
    static Connect(handler, addr)
    {
        let ws = new WS(handler, addr);

        // necessary because seemingly the base class is clobbering
        // the member functions of the same name (when I tried using them).
        ws.onopen    = ws.OnOpen;
        ws.onclose   = ws.OnClose;
        ws.onmessage = ws.OnMessage;
        ws.onerror   = ws.OnError;
        
        return ws;
    }
}





















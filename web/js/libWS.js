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
        console.log("onopen");
        this.handler.OnConnect(this);
    }
    
    OnMessage(event)
    {
        msg = JSON.parse(event.data);

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
        return new WS(handler, addr);
    }
}





















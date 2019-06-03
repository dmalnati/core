from libWeb import *


webHandler = None


class Handler():
    def __init__(self, webServer):
        self.webServer = webServer
        
        
    def Init(self):
        self.SetUpWebSocketHandler()
        self.SetUpWebSocketHandlerMon()
        self.SetUpDynamicStatusHandler()
    
    
    def SetUpWebSocketHandler(self):
        class WebSocketHandler(WSEventHandler):
            def OnWSConnectIn(self, ws):
                Log("CORE WebSocket connected")

            def OnMessage(self, ws, msg):
                Log("CORE WebSocket message:")
                ws.DumpMsg(msg)

            def OnClose(self, ws):
                Log("CORE WebSocket closed")

        handler = WebSocketHandler()
        self.webServer.AddWSListener(handler, "/core/ws")
        
    def SetUpWebSocketHandlerMon(self):
        pub = WSPublisherCommandInterval("Mon.py", 1)

        self.webServer.AddWSListener(pub, "/core/ws/mon")
        
        
    def SetUpDynamicStatusHandler(self):
        class StatusHandler(WebRequestHandler):
            def get(self):
                self.write("I'm dynamic")
        
        self.webServer.AddWebRequestHandler(r"/core/status/$", StatusHandler)
        


def Init(webServer):
    global webHandler
    
    if not webHandler:
        webHandler = Handler(webServer)
        
        webHandler.Init()






import inspect

import tornado.web
import tornado.httpserver
 
from ..utl import *
 
 
#
# This represents the set of functions which a class inheriting from the
# ApplicationBase is expected to have.
#
class ApplicationInterface():
    def __init__(self, *args, **kwargs):
        pass
 
    def Start(self, *args, **kwargs):
        pass
 
    def OnKeyboardInput(self, line):
        pass
 
 
#
# This is the basis of simplified applications who get, for free:
# - Event manager running at the completion of the Start() function
# - Keyboard callback
#
class ApplicationBase(ApplicationInterface):
    def __init__(self, *args, **kwargs):
        ApplicationInterface.__init__(self, *args, **kwargs)
 
        # capture base class Start function for calling later
        self.PrivateStartCaptured = self.Start
 
        # replace start function with interceptor
        self.Start = self.PrivateStart

        # Allow application to be non-interactive
        self.enableKeyboardInput = kwargs.get("enableKeyboardInput", True)
 
    # Step in between the base class and actual Start.
    def PrivateStart(self, *args, **kwargs):
        # Figure out how to call the function based on inspection.
        # For simplicity, *args will always be passed, but check to see if
        # the **kwargs can be passed or not
        (argsList, varargs, keywords, defaults) = \
            inspect.getargspec(self.PrivateStartCaptured)
 
        if keywords or defaults:
            self.PrivateStartCaptured(*args, **kwargs)
        else:
            self.PrivateStartCaptured(*args)
 
        # Set up keyboard handler

        if self.enableKeyboardInput:
            print("running it")
            WatchStdinEndLoopOnEOF(self.OnKeyboardInput)
 
        # Run main loop
        evm_MainLoop()
 
 
 
class WebApplicationInterface(ApplicationInterface):
    def __init__(self, *args, **kwargs):
        ApplicationInterface.__init__(self, *args, **kwargs)
 
    def OnInternetGet(self, name):
        pass
 
    def OnInternetSet(self, name, value):
        pass
 
 
class WebApplicationBase(ApplicationBase, WebApplicationInterface):
    def __init__(self, *args, **kwargs):
        ApplicationBase.__init__(self, *args, **kwargs)
        WebApplicationInterface.__init__(self, *args, **kwargs)
 
        self.webPort = int(kwargs.get("webPort", 8080))
        self.webRoot = kwargs.get("webRoot", os.getcwd() + "/html")

        wab = self
 
        # Set up webserver app
        class FaviconHandler(tornado.web.RequestHandler):
            def get(self, *args, **kwargs):
                pass

        class IndexHandler(tornado.web.RequestHandler):
            def get(self, *args, **kwargs):
                self.render(wab.webRoot + "/index.html")
 
        class GetHandler(tornado.web.RequestHandler):
            def get(self, *args, **kwargs):
                try:
                    name = self.get_argument("name")
 
                    retVal = wab.OnInternetGet(name)
 
                    if retVal:
                        self.write(retVal)
                    else:
                        self.write("")
                except:
                    pass
 
        class SetHandler(tornado.web.RequestHandler):
            def get(self, *args, **kwargs):
                try:
                    name  = self.get_argument("name")
                    value = self.get_argument("value")
 
                    retVal = wab.OnInternetSet(name, value)
 
                    if retVal:
                        self.write(retVal)
                    else:
                        self.write("")
                except:
                    pass
 
        self.webApp = tornado.web.Application([
            (r'/get/(.*)',    GetHandler),
            (r'/set/(.*)',    SetHandler),
            (r'/',            IndexHandler),
            (r'/favicon.ico', FaviconHandler),
            (r"/(.*)",        tornado.web.StaticFileHandler,
                              {"path": self.webRoot }),
        ])
 
        self.webServer = tornado.httpserver.HTTPServer(self.webApp)
        self.webServer.listen(self.webPort)
 
        Log("Web Application Details:")
        Log("  Listening on port: " + str(self.webPort))
        Log("  Serving files in : " + str(self.webRoot))
 

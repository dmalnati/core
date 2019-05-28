from libWS import *



###############################################################################
#
# This is the WSApp interface.
#
# Classes defined here:
#
#
# WSApp
# - Knows about services
# - Expects you are a service or a non-service client
# - If you pass in a service name or service port, you become that
# - If you pass in nothing, you are an anonymous service on a randomly
#   assigned port
# 
#
###############################################################################



class WSApp(WSManager):
    def __init__(self, serviceOrPort = None):
        self.service__data = dict()
        self.serviceData = None

        self.ReadServiceDirectory()
        
        # On startup, a WSApp will init.
        # Servers will identify their service name or port.
        # Clients won't.
        #
        # If we're a server, we want to identify our own service details so
        # when the server tries to Listen later, it has its details sorted

        if serviceOrPort:
            # Maybe the name of a service
            if not self.serviceData:
                self.serviceData = self.LookupServiceByName(serviceOrPort)
                
            # Or maybe the port of a service
            if not self.serviceData:
                self.serviceData = self.LookupServiceByPort(serviceOrPort)

            # Or maybe just a port not defined, so we make up an address
            if not self.serviceData:
                if serviceOrPort.isdigit():
                    self.serviceData = \
                        self.MakeServiceDataByPort(serviceOrPort)
        else:
            self.serviceData = self.MakeServiceDataClient()
            
        # finally know enough to be able to init base class
        WSManager.__init__(self, self.serviceData["service"])

        port = self.Listen()

        self.AffirmServiceDataWithPort(port)

        Log("PID: %s" % os.getpid())

        service = self.serviceData["service"]
        addr    = self.serviceData["addr"]
        Log("[%s :: %s]" % (service, addr))
        Log("")


    def GetSelfServiceData(self):
        return self.serviceData
        

    #############################
    # virtual -- implement if you're going to call Listen
    #############################
    def OnWSConnectIn(self, ws):
        ws.SendAbort("NOT ACCEPTING CONNECTIONS")
    
    
    def Listen(self):
        return WSManager.Listen(self,
                                self,
                                self.serviceData["port"], 
                                self.serviceData["wsPath"])
    
    
    def Connect(self, handler, serviceOrAddrOrPort):
        handle  = None
        addr    = None
        service = None
        
        # Check first maybe it's an already-formed websocket address
        try:
            if serviceOrAddrOrPort.index("ws://") == 0:
                addr    = serviceOrAddrOrPort
                service = addr
        except:
            pass

        # Or maybe the name of a service
        if not addr:
            data = self.LookupServiceByName(serviceOrAddrOrPort)
            
            if data:
                addr    = data["addr"]
                service = data["service"]

        # Or maybe the port of a service
        if not addr:
            data = self.LookupServiceByPort(serviceOrAddrOrPort)

            if data:
                addr    = data["addr"]
                service = data["service"]

        # Or maybe just a port not defined, so we make up an address
        if not addr:
            if serviceOrAddrOrPort.isdigit():
                addr    = "ws://127.0.0.1:%s/ws" % serviceOrAddrOrPort
                service = addr
            else:
                pass

        # Try to connect to whatever we came up with
        if addr:
            serviceStr = service
            if service == addr:
                serviceStr = "<?>"

            Log("Connecting to [%s :: %s]" % (serviceStr, addr))
            handle = WSManager.Connect(self, handler, addr)
            
        return handle
    

    def ReadServiceDirectory(self):
        ok = True

        core = os.environ["CORE"]
        serviceFile = core + "/generated-cfg/WSServices.txt"

        with open(serviceFile, 'r') as file:
            fileData = file.read().rstrip('\n')
        
            lineList = fileData.split("\n")
            
            port__seen = dict()

            for line in lineList:
                line = line.strip()
                
                if len(line):
                    if line[0] != "#":
                        linePartList = line.split(" ")
                        
                        if len(linePartList) == 4:
                            service = linePartList[0]
                            host    = linePartList[1]
                            port    = linePartList[2]
                            wsPath  = linePartList[3]
                            
                            data = {
                                "service" : service,
                                "host"    : host,
                                "port"    : str(port),
                                "wsPath"  : wsPath,
                                "addr"    : "ws://" + host + ":" + \
                                            port + wsPath,
                            }
                            
                            if service in self.service__data:
                                ok = False
                            elif port in port__seen:
                                ok = False
                            else:
                                self.service__data[service] = data
                                port__seen[port] = 1
        
        if not ok:
            Log("Could not read service directory, aborting")
            sys.exit(1)



    def MakeServiceDataByPort(self, port):
        data = dict()

        data["service"] = "SERVICE_%s:%s" % (str(os.getpid()), port)
        data["host"]    = "127.0.0.1"
        data["port"]    = str(port)
        data["wsPath"]  = "/ws"
        data["addr"]    = "ws://" + data["host"] + ":" + \
                          data["port"] + data["wsPath"]

        return data

    def MakeServiceDataClient(self):
        data = dict()

        data["service"] = "SERVICE_%s" % (str(os.getpid()))
        data["host"]    = "127.0.0.1"
        data["port"]    = "0"
        data["wsPath"]  = "/ws"
        data["addr"]    = "ws://" + data["host"] + ":" + \
                          data["port"] + data["wsPath"]

        return data

    def AffirmServiceDataWithPort(self, port):
        if self.serviceData["port"] == "0":
            self.serviceData["port"] = str(port)

            self.serviceData["service"]                   = \
                self.serviceData["service"].split(":")[0] + \
                ":"                                       + \
                self.serviceData["port"]


            self.serviceData["addr"]     = \
                "ws://"                  + \
                self.serviceData["host"] + \
                ":"                      + \
                self.serviceData["port"] + \
                self.serviceData["wsPath"]
            


    def LookupServiceByName(self, service):
        data = None

        if service in self.service__data:
            data = self.service__data[service]

        return data


    def LookupServiceByPort(self, portSearch):
        data = None

        service = None
        port    = None
        
        for service in self.service__data.keys():
            tmpData = self.service__data[service]
            tmpPort = tmpData["port"]
            
            if tmpPort == portSearch:
                data = tmpData
            
        return data


    def GetServiceAddr(self, service):
        addr = None
        
        if service in self.service__data:
            data = self.service__data[service]
            addr = "ws://" + data["host"] + ":" + data["port"] + data["wsPath"]
        
        return addr


    def GetServiceData(self, service):
        data = None
        
        if service in self.service__data:
            data = self.service__data[service]
            
        return data


        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

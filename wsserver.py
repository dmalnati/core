#!/usr/bin/python

import tornado.httpserver
import tornado.websocket
import tornado.ioloop
import tornado.web
import os
import json
import signal
import sys
import time

from collections import deque
 

'''
Basic objects representing the two types of clients possible
'''
class ChatClient():
    def __init__(self):
        self.timeOfLastContact = time.time()
        self.userName = ""
        self.type = ""
 
    def GetUserName(self):
        return self.userName

    def GetType(self):
        return self.type
        
    def GetSecsSinceLastContact(self):
        return time.time() - self.timeOfLastContact
        
    def SetTimeOfLastContactNow(self):
        self.timeOfLastContact = time.time()

    def GetJsonObjMessage(self):
        return dict()

    def Send(self, message):
        pass

        
        
class ChatClientWebSocket(ChatClient):
    def __init__(self, ws):
        ChatClient.__init__(self)
        self.type = "WEB_SOCKET"
        self.ws = ws
        self.jsonObj = {}
        
    def SetMessage(self, message):
        self.jsonObj = json.loads(message)
        
    def GetJsonObjMessage(self):
        return self.jsonObj

    def Send(self, message):
        self.ws.write_message(message)

        
class ChatClientPoll(ChatClient):
    def __init__(self, rh):
        ChatClient.__init__(self)
        self.type = "POLL"
        self.rh = rh
        self.chatMessageHistoryQueue = deque()

    def CopyFromNewInstance(self, ccp):
        self.rh = ccp.rh
        self.jsonDict = ccp.jsonDict

    def GetJsonObjMessage(self):
        # decode url query
        jsonString = self.rh.get_argument("json", default = "");
        
        # convert decoded json to dict
        self.jsonDict = json.loads(jsonString)

        return self.jsonDict

    def Send(self, message):
        self.rh.write(message)
        
    def StoreMessageHistory(self, timestamp, userName, message):
        chatTuple = timestamp, userName, message
        self.chatMessageHistoryQueue.append(chatTuple)
        
    def ClearHistory(self):
        self.chatMessageHistoryQueue.clear()
    
    def GetMessageHistory(self):
        chatHistoryList = []
        
        for timestamp, userName, message in self.chatMessageHistoryQueue:
            chatHistoryList.append({
                "TIMESTAMP": timestamp,
                "USER_NAME": userName,
                "MESSAGE"  : message
            })
        
        self.chatMessageHistoryQueue.clear()
        
        return chatHistoryList
    

class ChatRoom():
    def __init__(self, chatRoomName):
        self.PASSWORD = "BBQ"
        self.SECS_UNTIL_STALE = 30
        self.STALE_CLIENT_CHECK_FREQUENCY_MS = 1000
        self.HISTORY_SIZE = 500

        self.chatRoomName = chatRoomName
        self.chatMessageHistoryQueue = deque()

        # keep track of users.  Some are WS, some are POLL.
        self.userName__clientObj = {}
        
        # check for stale POLL users
        tornado.ioloop.PeriodicCallback(self.OnCheckForStaleChatClientPoll,
                                        self.STALE_CLIENT_CHECK_FREQUENCY_MS).start()
    

    

    ''' Callback for a request from a POLL Client '''
    def OnChatClientPoll(self, clientObj):
        # check password, bail out if not valid
        if self.ValidateChatClientPasswordOrSendError(clientObj) != True:
            return

        # get message
        jsonDict = clientObj.GetJsonObjMessage()

        # register new user if not known to us
        userName = jsonDict["USER_NAME"]
        userNeedsGlobalHistory = False
        if userName not in self.userName__clientObj:
            # announce new user
            self.OnUserNameAdd(userName)
        
            self.userName__clientObj[userName] = clientObj
            userNeedsGlobalHistory = True
        else:
            # newly-created client object should be incorporated into existing
            # object.  eg overwrite handle, but don't overwrite other data.
        
            # TODO - deal with poll users being able to override WS user usernames, and
            # even other poll users.  probably assign unique id on first login that is
            # required upon subsequent logins.  too complex for now.
            self.userName__clientObj[userName].CopyFromNewInstance(clientObj)
            clientObj = self.userName__clientObj[userName]
        
        # set last time of contact for this user
        self.userName__clientObj[userName].SetTimeOfLastContactNow()
        
        # examine message properties
        messageType = jsonDict["MESSAGE_TYPE"]
        
        if messageType == "REQ_POLL":
            # collect and return history from last requested point
            if userNeedsGlobalHistory:
                chatHistoryList = self.GetChatMessageHistoryList()
            else:
                chatHistoryList = self.userName__clientObj[userName].GetMessageHistory()
            
            clientObj.Send(json.dumps({
                "MESSAGE_TYPE"             : "REP_POLL",
                "ERROR"                    : 0,
                "USER_NAME_LIST"           : self.userName__clientObj.keys(),
                "CHAT_MESSAGE_HISTORY_LIST": chatHistoryList
            }))
        elif messageType == "REQ_SEND_CHAT_MESSAGE":
            self.OnChatMessageReceived(clientObj)
        elif messageType == "REQ_SERVER_COMMAND":
            self.OnServerCommandReceived(clientObj)
        else:
            pass
    
    
    
    ''' Functionality for Web Socket Clients '''
    def OnWebSocketClientOpen(self, clientObj):
        pass
    
    def OnWebSocketClientMessage(self, clientObj):
        # check if this socket has logged in already by looking at presence
        # in list of users
        jsonDict = clientObj.GetJsonObjMessage()
        messageType = jsonDict["MESSAGE_TYPE"]
        
        if messageType == "REQ_LOGIN":
            self.OnWebSocketClientLogIn(clientObj)
        elif messageType == "REQ_SEND_CHAT_MESSAGE":
            self.OnChatMessageReceived(clientObj)
        elif messageType == "REQ_SERVER_COMMAND":
            self.OnServerCommandReceived(clientObj)
        else:
            pass

    def OnWebSocketClientLogIn(self, clientObj):
        # check password, error out if not valid
        if self.ValidateChatClientPasswordOrSendError(clientObj) != True:
            return
            
        # check username not logged in, error out if not valid   
        if self.ValidateChatClientLoginOrSendError(clientObj) != True:
            return
            
        # register new user
        jsonObj = clientObj.GetJsonObjMessage()
        userName = jsonObj["USER_NAME"]
        
        # announce new user
        self.OnUserNameAdd(userName)
        
        # actually store new client object
        self.userName__clientObj[userName] = clientObj
        
        # send history to this user
        clientObj.Send(json.dumps({
            "MESSAGE_TYPE"             : "REP_LOGIN",
            "ERROR"                    : 0,
            "USER_NAME_LIST"           : self.userName__clientObj.keys(),
            "CHAT_MESSAGE_HISTORY_LIST": self.GetChatMessageHistoryList()
        }))
        
    def OnWebSocketClientClose(self, clientObj):
        for userName_, clientObj_ in self.userName__clientObj.items():
            if clientObj_ is clientObj:
                self.userName__clientObj.pop(userName_)
                
                # announce remove user
                self.OnUserNameRemove(userName_)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    ''' Core Chat Room Functionality '''
    
    def OnServerCommandReceived(self, clientObj):
        commandOk = True
    
        jsonDict = clientObj.GetJsonObjMessage()
        
        commandString = jsonDict["COMMAND_STRING"]
        commandStringArr = commandString.split(" ")
        command = commandStringArr[0]
        
        if command == "clear" and commandStringArr[1] == "history":
            self.ClearHistory()
        else:
            commandOk = False

        if commandOk:
            self.SendOk(clientObj)
        else:
            self.SendError(clientObj, "Command \"" + commandString + "\" unknown")
        
    def ClearHistory(self):
        # clear global history
        self.chatMessageHistoryQueue.clear()
        
        # clear per-poll-user history
        for userName, clientObj in self.userName__clientObj.items():
            if clientObj.GetType() == "POLL":
                clientObj.ClearHistory()
    
    ''' Periodically kick out stale POLL Clients '''
    def OnCheckForStaleChatClientPoll(self):
        userNameStaleList = []
        
        for userName, clientObj in self.userName__clientObj.items():
            if clientObj.GetType() == "POLL":
                if clientObj.GetSecsSinceLastContact() > self.SECS_UNTIL_STALE:
                    userNameStaleList.append(userName)
                    del self.userName__clientObj[userName]
        
        for userNameStale in userNameStaleList:
            # announce remove user
            self.OnUserNameRemove(userNameStale)
        
    def OnUserNameAdd(self, userName):
        for clientObj in self.userName__clientObj.values():
            if clientObj.GetType() != "POLL":
                clientObj.Send(json.dumps({
                    "MESSAGE_TYPE": "EVENT_USER_NAME_ADD",
                    "ERROR"       : 0,
                    "USER_NAME"   : userName,
                }))

    def OnUserNameRemove(self, userName):
        for clientObj in self.userName__clientObj.values():
            if clientObj.GetType() != "POLL":
                clientObj.Send(json.dumps({
                    "MESSAGE_TYPE": "EVENT_USER_NAME_REMOVE",
                    "ERROR"       : 0,
                    "USER_NAME"   : userName,
                }))
        
    ''' Convenience function to check password and reject if bad '''
    def ValidateChatClientPasswordOrSendError(self, clientObj):
        retVal = True

        jsonDict = clientObj.GetJsonObjMessage()
        password = jsonDict["PASSWORD"]

        if password != self.PASSWORD:
            self.SendError(clientObj, "Password \"" + password + "\" incorrect")
            retVal = False
        else:
            pass

        return retVal
        
    ''' Convenience function to check if username logged in already '''
    def ValidateChatClientLoginOrSendError(self, clientObj):
        retVal = True

        jsonDict = clientObj.GetJsonObjMessage()
        userName = jsonDict["USER_NAME"]

        if userName in self.userName__clientObj:
            self.SendError(clientObj, "Username \"" + userName + "\" already logged in")
            retVal = False
        else:
            pass

        return retVal
    
    ''' Convenience function to craft and send an error message '''
    def SendError(self, clientObj, errorText):
        jsonDict = clientObj.GetJsonObjMessage()
        messageType = jsonDict["MESSAGE_TYPE"]
        messageTypeRep = messageType.replace("REQ_", "REP_", 1)

        clientObj.Send(json.dumps({
            "MESSAGE_TYPE": messageTypeRep,
            "ERROR"       : 1,
            "ERROR_TEXT"  : errorText
        }))
    
    def SendOk(self, clientObj):
        jsonDict = clientObj.GetJsonObjMessage()
        messageType = jsonDict["MESSAGE_TYPE"]
        messageTypeRep = messageType.replace("REQ_", "REP_", 1)
    
        clientObj.Send(json.dumps({
            "MESSAGE_TYPE": messageTypeRep,
            "ERROR"       : 0
        }))
        
    def OnChatMessageReceived(self, clientObj):
        jsonDict = clientObj.GetJsonObjMessage()
    
        timestamp = jsonDict["TIMESTAMP"]
        userName  = jsonDict["USER_NAME"]
        message   = jsonDict["MESSAGE"]
        
        # store message in local cache
        self.SaveAndRelayChatMessage(timestamp, userName, message)
        
        # reply to client that message was sent
        self.SendOk(clientObj)
    
    ''' Store a message in global history '''
    def SaveAndRelayChatMessage(self, timestamp, userName, message):
        chatTuple = timestamp, userName, message
        
        # store global history
        self.chatMessageHistoryQueue.append(chatTuple)
        if len(self.chatMessageHistoryQueue) > self.HISTORY_SIZE:
            oldChatTuple = self.chatMessageHistoryQueue.popleft()
            
        # store history for each consumer
        for clientObj in self.userName__clientObj.values():
            if clientObj.GetType() == "POLL":
                clientObj.StoreMessageHistory(timestamp, userName, message)
            else:
                clientObj.Send(json.dumps({
                    "MESSAGE_TYPE": "EVENT_RELAY_CHAT_MESSAGE",
                    "ERROR"       : 0,
                    "TIMESTAMP"   : timestamp,
                    "USER_NAME"   : userName,
                    "MESSAGE"     : message
                }))

    ''' Retrieve all messages in global history '''
    def GetChatMessageHistoryList(self):
        chatHistoryList = []
        
        for timestamp, userName, message in self.chatMessageHistoryQueue:
            chatHistoryList.append({
                "TIMESTAMP": timestamp,
                "USER_NAME": userName,
                "MESSAGE"  : message
            })
            
        return chatHistoryList
    
    
'''
Manger of multiple chat rooms.
'''    
class ChatRoomManager():
    def __init__(self):
        self.chatRoomList = {}
    
    def GetChatRoom(self, chatRoomName = "Default"):
        chatRoom = None
        
        if chatRoomName in self.chatRoomList.keys():
            chatRoom = self.chatRoomList[chatRoomName]
        else:
            chatRoom = ChatRoom(chatRoomName)
            self.chatRoomList[chatRoomName] = chatRoom
            
        return chatRoom

'''
Application startup
'''        
TheChatRoomManager = ChatRoomManager()


class ChatClientViaWebSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        tornado.web.RequestHandler.__init__(self, application, request, **kwargs)
        self.chatRoom = TheChatRoomManager.GetChatRoom();
        self.clientObj = {}

        # seems to break on ubuntu without this, despite running 4.1 ...
        if hasattr(self, "_on_close_called") == False:
            self._on_close_called = False

    def open(self):
        print("got a connection")
        self.write_message("hello friend")
        self.close()
        return
        self.clientObj = ChatClientWebSocket(self)
        self.chatRoom.OnWebSocketClientOpen(self.clientObj)
      
    def on_message(self, message):
        self.clientObj.SetMessage(message)
        self.chatRoom.OnWebSocketClientMessage(self.clientObj)
 
    def on_close(self):
        self.chatRoom.OnWebSocketClientClose(self.clientObj)

class ChatClientViaPoll(tornado.web.RequestHandler):
    def get(self):
        clientObj = ChatClientPoll(self)
        TheChatRoomManager.GetChatRoom().OnChatClientPoll(clientObj)

class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render(os.getcwd() + "/./index.html")

def SignalHandler(signal, frame):
    print "Exiting via Ctl+C"
    sys.exit(0);
        
def Main():
    # handle ctl-c
    signal.signal(signal.SIGINT, SignalHandler)

    application = tornado.web.Application([
        (r'/ws', ChatClientViaWebSocket),
    ])
    
    # default port
    port = 8080

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(port)
    
    print 'Server started on port %i' % (port)
    
    tornado.ioloop.IOLoop.instance().start()
    
    
Main()

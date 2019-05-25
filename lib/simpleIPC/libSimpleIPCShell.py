#!/usr/bin/python

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from lib.utl import *
from lib.simpleIPC import *


#
# Class dedicated to helping the user operate the API for the Protocol Handler
#
class SimpleIPCShell():
    def __init__(self, ph):
        # Keep a reference to the protocol handler
        self.ph = ph

        self.hdr = None
        self.msg = None

        WatchStdinEndLoopOnEOF(self.OnStdin)

        self.ShowPrompt()

    def OnHandleUnknownMessage(self, hdr, msg):
        # If the shell is registered as a handler, just print

        print("")
        print("[Message Received]")

        hdr.Print()
        msg.Print()

        print("")
        self.ShowPrompt()

    def OnStdin(self, line):
        handled  = True
        wordList = line.split(" ")

        if len(wordList) == 1:
            word = wordList[0]

            if word == "help":
                print("ls")
                print("- show all messages and types, select with 'msg'")
                print("")
                print("msg <num>")
                print("-- select a message by number")
                print("")
                print("show")
                print("-- show fields of currently selected message")
                print("")
                print("set <field> <value>")
                print("-- set field of selected message")
                print("")
                print("addr")
                print("-- display addressing information")
                print("send")
                print("-- send message")
                print("")
                print("clear")
                print("-- clear the screen")
                print("")
                print("exit / quit")
                print("-- quit")
            elif word == "ls":
                self.ph.PrintMessageTypes()
            elif word == "show":
                if self.msg:
                    self.msg.Print()
                else:
                    print("[no msg selected, type 'ls' to see message types]")
            elif word == "addr":
                self.ph.PrintAddr()
            elif word == "send":
                if self.msg:
                    self.ph.Send(self.msg)
                else:
                    print("[no msg selected]")
            elif word == "clear":
                os.system("clear")
            elif word == "exit" or word == "quit":
                sys.exit(0)
            else:
                handled = False
        elif len(wordList) == 2:
            if wordList[0] == "msg":
                msgType = wordList[1]

                msg = self.ph.GetSimpleIPCMessageByMessageType(msgType)

                if msg:
                    self.msg = msg
                else:
                    print("[msg '" + msgType + "' does not exist]")
            else:
                handled = False
        elif len(wordList) == 3:
            if wordList[0] == "set":
                if self.msg:
                    field = wordList[1]
                    value = wordList[2]

                    if not self.msg.Set(field, value):
                        print("[field '" + str(field) + "' does not exist]")
                else:
                    print("[no msg selected]")
            else:
                handled = False
        else:
            handled = False


        if not handled:
            if not line == "":
                print("[cmd not understood: '" + line + "']")


        self.ShowPrompt()

    def ShowPrompt(self):
        prompt = "msgsh: "

        if self.msg:
            prompt += "[%i]%s " % (self.msg.GetMessageType(), \
                                   self.msg.GetClassName())

        prompt += "> "

        sys.stdout.write(prompt)
        sys.stdout.flush()




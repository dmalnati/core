#!/usr/bin/python

import os
import time
import sys

from libHX711 import *
from libPumpPwm import *


sys.path.append(os.path.join(os.path.dirname(__file__), '..', ''))
from myLib.utl import *


class App:
    def __init__(self,
                 pinPwmPump,
                 pinClkHx711,
                 pinSerialHx711,
                 gain,
                 subtract,
                 divide):

        # Get interface to gpiod
        self.pig = pigpio.pi()

        # Create pressure sensor
        self.sensor = HX711(pinClkHx711, pinSerialHx711)
        self.sensor.SetGain(gain)
        self.sensor.SetCalibration(subtract, divide)

        # Create pump control
        self.pump = PumpPwm(pinPwmPump)

        # Store runtime information
        class RunState:
            pass

        self.runState = RunState()

        self.runState.high = 35
        self.runState.high = 25
        self.runState.low  = 15
        self.runState.pwmPct = 100
        self.runState.timeLimitVal  = 90
        self.runState.timeLimitUnit = "m"
        self.runState.reportSecs    = 5
        self.runState.state = "GOING_UP"

        # keep timer handles
        self.timerHandleTimeLimit = None
        self.timerHandleMonitor = None


    def Run(self):
        def OnStdIn(inputStr):
            inputStr = inputStr.strip()

            if inputStr != "":
                self.OnKeyboardReadable(inputStr)
            
        WatchStdinEndLoopOnEOF(OnStdIn, binary=True)

        self.PrintHelp()
        self.PrintCurrentState()

        evm_MainLoop()

        # Stop once you hit CTL+C
        print("")
        print("Exiting")
        self.pump.End()

    def PrintHelp(self):
        print("Commands")
        print("--------")
        print("high <val> - set pressure to climb to before turning off pump")
        print("low  <val> - set pressure below which the pump turns back on")
        print("pwmPct <val> - set the pct the PWM on when pressurizing")
        print("timeLimit <val> <unit> - shut off pump after this time")
        print("    <unit> can be s - seconds, m - minutes, h - hours")
        print("reportSecs <val> - how frequenly pressure checked/reported")
        print("start - begin inflation")
        print("stop - stop doing this and shut off the pump")
        print("help - show this message")
        print("")

    def PrintCurrentState(self):
        print("Current Values")
        print("--------------")
        print("high %s" % (self.runState.high))
        print("low  %s" % (self.runState.low))
        print("pwmPct %s" % (self.runState.pwmPct))
        print("timeLimit %s %s" % (self.runState.timeLimitVal,
                                   self.runState.timeLimitUnit))
        print("reportSecs %s" % (self.runState.reportSecs))
        print("")
        

    def OnKeyboardReadable(self, inputStr):
        print("")

        inputStrList = inputStr.split()

        cmd = inputStrList[0]

        understood = True
        printVals  = True

        if len(inputStrList) == 1:
            if cmd == "start":
                self.Start()

                printVals = False
            elif cmd == "stop":
                self.Stop()

                printVals = False
            elif cmd == "help":
                self.PrintHelp()
            else:
                understood = False
        elif len(inputStrList) == 2:
            val1 = int(inputStrList[1])

            if cmd == "high":
                self.runState.high = val1
            elif cmd == "low":
                self.runState.low = val1
            elif cmd == "reportSecs":
                self.runState.reportSecs = val1
            elif cmd == "pwmPct":
                self.runState.pwmPct = val1
            else:
                understood = False
        elif len(inputStrList) == 3:
            val1 = int(inputStrList[1])
            val2 = inputStrList[2]

            if cmd == "timeLimit":
                self.runState.timeLimitVal  = val1
                self.runState.timeLimitUnit = val2
            else:
                understood = False

        if understood:
            print("ok")

            if printVals:
                self.PrintCurrentState()
        else:
            print("Err, not understood: \"%s\"" % (cmd))
            self.PrintHelp()
            self.PrintCurrentState()

        print("")



    def GetTimeLimitMs(self):
        retVal = self.runState.timeLimitVal

        if self.runState.timeLimitUnit == "s":
            retVal = retVal * 1000
        elif self.runState.timeLimitUnit == "m":
            retVal = retVal * 1000 * 60
        elif self.runState.timeLimitUnit == "h":
            retVal = retVal * 1000 * 60 * 60
        else:
            retVal = 0

        return retVal
        

    def OnTimeoutTimeLimit(self):
        print("Time limit reached, stopping")

        self.Stop()

    def OnTimeoutMonitor(self):
        dateStr = time.strftime("%Y-%m-%d")
        timeStr = time.strftime("%H:%M:%S")
        val     = int(self.sensor.GetMeasurement())

        print("%s,%s,%s" % (dateStr, timeStr, val))

        if self.runState.state == "GOING_UP":
            if val < self.runState.high:
                # make sure motor running
                self.pump.SetPwmPct(self.runState.pwmPct)
            else:
                # shut off motor, switch state
                print("Upper pressure threshold (%s) hit, cutting pump" % \
                      (self.runState.high))
                print("Resuming again once pressure below lower threshold (%s)"\
                      % (self.runState.low))

                self.pump.SetPwmPct(0)

                self.runState.state = "GOING_DOWN"
        elif self.runState.state == "GOING_DOWN":
            if val <= self.runState.low:
                # turn on motor, switch state
                print("Lower pressure threshold (%s) hit, enabling pump" % \
                      (self.runState.low))
                print("Disabling once pressure above upper threshold (%s)" % \
                      (self.runState.high))

                self.pump.SetPwmPct(self.runState.pwmPct)

                self.runState.state = "GOING_UP"
            else:
                # nothing to do, just letting pressure decrease here
                pass


        self.timerHandleMonitor = \
            evm_SetTimeout(self.OnTimeoutMonitor, \
                           self.runState.reportSecs * 1000)


    def Start(self):
        self.Stop(0)

        print "Starting" 

        # Set up time limit timer
        ms = self.GetTimeLimitMs()
        self.timerHandleTimeLimit = \
            evm_SetTimeout(self.OnTimeoutTimeLimit, ms)

        # Set up monitoring timer, but go off immediately
        self.timerHandleMonitor = evm_SetTimeout(self.OnTimeoutMonitor, 0)

        # put limit on the pressure sensor readings
        self.sensor.SetDiscardAbove(self.runState.high * 4)


    def Stop(self, verbose = 1):
        if verbose:
            print "Stopping"

        # Cancel timers
        if (self.timerHandleTimeLimit):
            evm_CancelTimeout(self.timerHandleTimeLimit)

            self.timerHandleTimeLimit = None

        if (self.timerHandleMonitor):
            evm_CancelTimeout(self.timerHandleMonitor)

            self.timerHandleMonitor = None

        # Reset state
        self.runState.state = "GOING_UP"



def Main():
    if len(sys.argv) != 7:
        print(("Usage: %s <pinPwmPump> " +
                         "<pinClkHx711> <pinSerialHx711> " +
                         "<hx711Gain> " +
                         "<hx711Subtract> <hx711Divide>") % (sys.argv[0]))
        print("Probably: %s 21 23 24 32 490916 18670" % (sys.argv[0]))
        sys.exit(-1)

    # pull out arguments
    pinPwmPump     = int(sys.argv[1])
    pinClkHx711    = int(sys.argv[2])
    pinSerialHx711 = int(sys.argv[3])
    gain           = int(sys.argv[4])
    subtract       = float(sys.argv[5])
    divide         = float(sys.argv[6])

    # create and run app
    app = App(pinPwmPump,
              pinClkHx711,
              pinSerialHx711,
              gain,
              subtract,
              divide)

    app.Run()



Main()

















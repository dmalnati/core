#!/usr/bin/python

import random
import time

import pigpio


def Main():
    bcPin = 4

    pigd = pigpio.pi()



    for pct in range(0, 100):
        #pct = random.randint(0, 100)
        msPulse = int(500 + ((float(pct) / 100.0) * 2000))
        print(msPulse)
        pigd.set_servo_pulsewidth(bcPin, msPulse)
        time.sleep(0.1)

    pigd.stop()

Main()

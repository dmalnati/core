#!/usr/bin/env python

import RPi.GPIO as GPIO
import time


HERTZ   = 50
PIN_OUT = 7

print("Hertz: " + str(HERTZ))
print("Pin  : " + str(PIN_OUT))

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_OUT, GPIO.OUT)

p = GPIO.PWM(PIN_OUT, HERTZ)

print("start: 7.5")
p.start(7.5)

print("change: 7.5")
p.ChangeDutyCycle(7.5)
time.sleep(1)
print("change: 12.5")
p.ChangeDutyCycle(12.5)
time.sleep(1)
print("change: 2.5")
p.ChangeDutyCycle(2.5)
time.sleep(1)

print("stop")
p.stop()

print("cleanup")
GPIO.cleanup()


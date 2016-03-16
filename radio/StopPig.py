#!/usr/bin/python

import sys

import pigpio


def Main():
    if len(sys.argv) != 2:
        print("Usage: " + sys.argv[0] + " <bcPin>")
        sys.exit(-1)

    bcPin = int(sys.argv[1])

    pigd = pigpio.pi()

    pigd.bb_serial_read_close(bcPin)

    pigd.stop()


Main()



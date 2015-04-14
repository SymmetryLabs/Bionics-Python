#!/usr/bin/env python

import liblo
from liblo import *
import sys
from time import sleep


try:
    targetA = liblo.Address("172.16.0.78", 9000)
    targetSelf = liblo.Address(9000)
except liblo.AddressError, err:
    print str(err)
    sys.exit()

# Converts magnitude to power level
def mag2level(mag):
    NUM_LEDS = 15
    level = int(mag * NUM_LEDS)
    return level

# Converts level to RGB stream
def level2rgb(level):
    NUM_LEDS = 15
    pixelOn = [0, 0, 255]
    pixelOff = [0, 0, 0]
    rgbBlob = []
    for led in range(NUM_LEDS):
        if led < level:
            rgbBlob.extend(pixelOn)
        else:
            rgbBlob.extend(pixelOff)
    return rgbBlob


class MyServer(ServerThread):
    def __init__(self):
        ServerThread.__init__(self, 8500)

    @make_method('/A/acc/mag', 'd')
    def mag_callback(self, path, args):
        [d] = args
        print "received message '%s' with argument: %f" % (path, d)

        # Parse into iLevel
        level = level2rgb(d)
        rgbBlob = level2rgb(level)
        print "rgbBlob: ", rgbBlob

        # Forward to the unit
        msg = liblo.Message("/outputs/rgb/1")
        msg.add(rgbBlob)
        # liblo.send(targetA, msg)
        liblo.send(targetSelf, msg)

    @make_method('/foo', 'ifs')
    def foo_callback(self, path, args):
        i, f, s = args
        print "received message '%s' with arguments: %d, %f, %s" % (path, i, f, s)

    @make_method(None, None)
    def fallback(self, path, args):
        print "received unknown message '%s'" % path
        print args

try:
    server = MyServer()
except ServerError, err:
    print str(err)
    sys.exit()

server.start()

while True:
    print "loop!"
    sleep(5)

raw_input("press enter to quit...\n")
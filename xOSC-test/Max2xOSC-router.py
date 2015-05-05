#!/usr/bin/env python

import liblo
from liblo import *
import sys
from time import sleep
from colorsys import hsv_to_rgb
from itertools import chain

def chunks(li, n):
    for i in xrange(0, len(li), n):
        yield li[i:i+n]

try:
    # targetA = liblo.Address("172.16.0.78", 9000)
    targetA = liblo.Address("169.254.1.1", 9000)
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
        level = mag2level(d)
        print "level = ", level
        rgbBlob = level2rgb(level)
        print "rgbBlob: ", rgbBlob

        # Forward to the unit
        msg = liblo.Message("/A/outputs/rgb/1")
        msg.add(rgbBlob)
        liblo.send(targetA, msg)
        # liblo.send(targetSelf, msg)

    @make_method('/A/leds', 'iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
    def mag_callback(self, path, args):


        hsvs = [hsv for hsv in chunks(args, 3)]
        rgbs = [hsv_to_rgb(h[0]/255., h[1]/255., h[2]/255.) for h in hsvs]
        rgbs = list(chain.from_iterable(rgbs))
        rgbs = [int(v*255) for v in rgbs]
        print rgbs
        # print "received message '%s' with argument: %f" % (path, d)
        print "received /A/leds"
        msg = liblo.Message("/A/outputs/rgb/1")
        msg.add(rgbs)
        liblo.send(targetA, msg)
        # liblo.send(targetSelf, msg)

    @make_method('/B/leds', 'iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
    def mag_callbackB(self, path, args):


        hsvs = [hsv for hsv in chunks(args, 3)]
        rgbs = [hsv_to_rgb(h[0]/255., h[1]/255., h[2]/255.) for h in hsvs]
        rgbs = list(chain.from_iterable(rgbs))
        rgbs = [int(v*255) for v in rgbs]
        print rgbs
        # print "received message '%s' with argument: %f" % (path, d)
        print "received /B/leds"
        msg = liblo.Message("/B/outputs/rgb/1")
        msg.add(rgbs)
        liblo.send(targetA, msg)
        # liblo.send(targetSelf, msg)

    @make_method('/B/leds', 'iiiiiiiiiiiiiii')
    def mag_callbackB5(self, path, args):


        hsvs = [hsv for hsv in chunks(args, 3)]
        rgbs = [hsv_to_rgb(h[0]/255., h[1]/255., h[2]/255.) for h in hsvs]
        rgbs = list(chain.from_iterable(rgbs))
        rgbs = [int(v*255) for v in rgbs]
        print rgbs
        # print "received message '%s' with argument: %f" % (path, d)
        print "received /B/leds"
        msg = liblo.Message("/B/outputs/rgb/1")
        msg.add(rgbs)
        liblo.send(targetA, msg)
        # liblo.send(targetSelf, msg)

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
#!/usr/bin/env python

from liblo import *
import sys
from time import sleep

class MyServer(ServerThread):
    def __init__(self):
        ServerThread.__init__(self, 9049)

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
#!/usr/bin/env python

import liblo, sys

from OSC import *


# we can also build a message object first...
msg = liblo.Message("/foo/blah")
# ... append arguments later...
msg.add(123, "foo")

serialised_bytes = msg.serialise()
print "SERIALIZED: ", serialised_bytes

print "DECODED: ", decodeOSC(serialised_bytes)
# Program to play motion data from data files
# Sends to port 9050 (normally the Processing port)

import json
from datetime import datetime, timedelta

from DataIOClasses import DataWriter, DataReader

directory = 'tests/data/'
filename = '20150303-183941.txt'
datareader = DataReader( directory + filename )
messageHistory = datareader.getEntries()
# print messageHistory

OSCport = 9050

print ""
print ""
print ""
print "--------------------"
print "--------------------"
print "OSC Data Player RUNNING"
print "--------------------"
print "--------------------"
print ""

print "Playing file: " + directory + filename
print "Sending to OSC port: ", OSCport
print messageHistory[-1]['time'].total_seconds(), " seconds of recorded data"
print ""

# From "client.py" in pyliblo examples

import liblo, sys

try:
    target = liblo.Address(OSCport)
except liblo.AddressError, err:
    print str(err)
    sys.exit()


# Loop through all messages and send to Processing
while True:
    try:
        startTime = datetime.now()
        print "BEGIN SENDING recorded data"
        for message in messageHistory:
            msg = liblo.Message(message['path'])
            for data in message['data']:
                msg.add(data)
            while ( (datetime.now()-startTime) < message['time'] ):
                pass
            liblo.send(target, msg)
        print "END SENDING recorded data"
        print ""
    except KeyboardInterrupt:
        break


print "--------------------"
print "--------------------"
print "OSC Data Player CLOSED"
print "--------------------"
print "--------------------"
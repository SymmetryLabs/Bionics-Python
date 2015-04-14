# Program to play motion data from data files
# Sends to port 9050 (normally the Processing port)

import json
from datetime import datetime, timedelta
from time import sleep

# from DataIOClasses import DataWriter, DataReader

# directory = 'tests/data/'
# filename = '20150303-183941.txt'
# datareader = DataReader( directory + filename )
# messageHistory = datareader.getEntries()
# print messageHistory

OSCport = 9000

print ""
print ""
print ""
print "--------------------"
print "--------------------"
print "OSC Data Player RUNNING"
print "--------------------"
print "--------------------"
print ""

# print "Playing file: " + directory + filename
print "Sending to OSC port: ", OSCport
# print messageHistory[-1]['time'].total_seconds(), " seconds of recorded data"
print ""

# From "client.py" in pyliblo examples

import liblo, sys

try:
    targetA = liblo.Address("172.16.0.78", OSCport)
    targetSelf = liblo.Address(OSCport)
except liblo.AddressError, err:
    print str(err)
    sys.exit()

NUM_LEDS = 15
# messages_animationChange = [ "anim/power", "anim/sparkle", "anim/eq" ]

print "--------------------"
print "OSC message options..."
print "Enter a number between 0 and ", NUM_LEDS
# for message in messages_animationChange:
#     print "[ ", messages_animationChange.index(message), " ] ", message
print "--------------------"
print



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



# Loop through all messages and send to Processing
while True:
    try:
        user_input = raw_input("Enter option ... ")
        rgbBlob = level2rgb( int(user_input) )

        # Send the commands
        msg = liblo.Message("/A/outputs/rgb/1")
        msg.add(rgbBlob)
        liblo.send(targetA,msg)
        print "Sending: ", rgbBlob
        print ""


    except KeyboardInterrupt:
        break


print "--------------------"
print "--------------------"
print "OSC Data Player CLOSED"
print "--------------------"
print "--------------------"
# --------------------------------------------
# --------------------------------------------
# x- IMPORT NECESSARY STUFF

import logging
import sys

import time
import rtmidi
from rtmidi.midiconstants import *
import random

# From test_midiin_callback.py in rtmidi examples
from rtmidi.midiutil import open_midiport
log = logging.getLogger('test_midiin_callback')


# Initialize xbee
from xbee import XBee
import serial


# Initialize tinypacks
import tinypacks
import struct
import time
from datetime import datetime
from datetime import timedelta


print ""
print ""
print ""
print "--------------------"
print "--------------------"
print "Bionic-Python INITIALIZING..."
print "--------------------"
print "--------------------"
print ""








# --------------------------------------------
# --------------------------------------------
# x- INITIALIZE MIDI OUT
# x- WRITE ALL MIDI FUNCTIONS
# TRY SORTING MIDI FUNCTIONS...

midiout = rtmidi.MidiOut()
try:
    midiout.open_virtual_port("Bionic Output")
    print "\"Bionic Output\" MIDI Channel Created"
except:
	print "Couldn't create Bionic Output"



def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


def noteOn(address, value):
    midiout.send_message([0x92, address, value])

def noteOff(address, value):
    midiout.send_message([0x82, address, value])

def noteFor(address, value, _time):
    noteOn(address, value)
    time.sleep(_time)
    noteOff(address, value)


# Use this for the 10/28 Bionic Test
def noteOnQuickly(address, value):
    noteFor(address, value, 0.02)

# Call noteOn/noteOff
# Pitch: Left/Right - Use roll
# Velocity: Magnitude - Use aaReal
def triggerMidiMusic(pitch, velocity):
    noteOnQuickly(pitch, velocity)

def effectOn():
    noteOn(93, 0)

def effectOff():
    noteOff(93, 0)

def effectOnFor(_time):
    effectOn()
    time.sleep(_time)
    effectOff()


# parameter ranges 0-3
def effectParameterChange(parameter, value):
    parameterAddress = 20 + parameter
    mitiout.send_message([0xB0, parameterAddress, value])



def boomMag(magnitude):
    effectParameterChange(0, magnitude)

def boomHue(magnitude):
    effectParameterChange(3, magnitude)

def boomX(magnitude):
    effectParameterChange(1, magnitude)

def boomY(magnitude):
    effectParameterChange(2, magnitude)



def boomXY(magX, magY):
    boomX(magX)
    boomY(magY)

def boomParam(magnitude, x, y, hue):
    boomMag(magnitude)
    boomHue(hue)
    boomXY(x, y)



def boom(magnitude, x, y, hue):
    boomParam(magnitude, x, y, hue)
    note(93, 0)


def boomRandom():
    boom(random.randint(60, 100), random.randint(0, 127), random.randint(0, 127), random.randint(0, 127))

def boomRandom(magnitude, hue):
    boom(magnitude, random.randint(0, 127), random.randint(0, 127), hue)



def previousEffect():
    shiftOn()
    note(97, 0)
    shiftOff()

def nextEffect():
    shiftOn()
    note(96, 0)
    shiftOff()


def shiftOn():
    noteOn(98, 0)

def shiftOff():
    noteOff(98, 0)












# --------------------------------------------
# --------------------------------------------
# x- INITIALIZE INTERNAL STUFF

# Main data structure for communications tracking
masterList = {}
numberStoredEntries = 20

global hueNow, magnitudeCutoff
hueNow = 0
magnitudeCutoff = 0.5

huePercent = 0






# --------------------------------------------
# --------------------------------------------
# x- INITIALIZE XBEE
# x- SET XBEE CALLBACK TO MIDI OUT
# SET XBEE CALLBACK TO INTERNAL STUFF


# MIDI OUT and notes must be enabled prior to this...
def message_received(response):
    try:
        global magnitudeCutoff

        print "--------------------"
        print "XBEE Message RECEIVED"        

        packed_data = response['rf_data']
        # print "Size of packed_data ", len(packed_data)

        # Initialize unpacked_data so the while loop will execute at least once
        unpacked_data = 0
        reports = []

        while unpacked_data is not None:
            try:
                unpacked_data, packed_data = tinypacks.unpack(packed_data)
            except:
                print "Exit unpacking loop"
                break
            else:
                if unpacked_data is not None:
                    # print unpacked_data
                    reports.append(unpacked_data)

        print "Num of Reports = ", len(reports)
        for report in reports:
            print "-Start Report-"
            for message in report['msg']:
                print "message ", message
            print "-End Report-"
        print "Unpacked all data"
        print ""

        # # tinypacks data structure, date added
        # unpacked_data['time'] = datetime.now()
        # unitID = response['source_addr'] # need to convert to string?

        # ## Add to master list, with unitID as key
        # # if masterList does not contain unitID, do something different
        # if not unitID in masterList.keys():
        #     masterList[unitID] = []

        # # check to see if queue is too big
        # if len(masterList[unitID]) >= numberStoredEntries:
        #     masterList[unitID].pop() # remove last entry

        # # insert most recent entry
        # masterList[unitID].insert(0, unpacked_data)

        try:
            # Only select the first message for now
            message = messages[0]
            if "msg" in message.keys():
                print "msg found..."
                valueList = message["msg"]
                aaRealPercent = valueList["val"]
                try:
                    timeMIDIsend
                except:
                    print "issue with timeMIDIsend"
                if ( datetime.now() - timeMIDIsend ) > timedelta(milliseconds=30):
                    if aaRealPercent > magnitudeCutoff:
                        SC.triggerMidiMusic( 63, translate(aaRealPercent, 0, 1, 60, 127) )
                        # SC.triggerMidiMusic( 63, 127 )
                        print "TRIGGER!"
                        message_received.timeMIDIsend = datetime.now()

            print ""
        except:
            print "(IGNORABLE) ERROR! Triggering interaction engine from XBEE message received"

    except:
        print "ERROR! Parsing error in message_received" 
    print "--------------------"
    print ""

message_received.timeMIDIsend = datetime.now()




PORTS = ['/dev/tty.usbserial-AM01VFA7', '/dev/tty.usbserial-A90FNX5T']
BAUD_RATE = 115200
# Iterate through possible Serial Port Names looking for connected xBee Explorer
for port in PORTS:
    try:
        ser = serial.Serial(port, BAUD_RATE)
    except OSError:
        print "ERROR! Unsuccessfully tried PORT = ", port
    else:
        print "Connected to PORT = ", port
        break
# Check to see if Serial successfully connected
try:
    ser
    print "Serial Port CREATED"
except:
    print "ERROR! Serial Port couldn't connect"
    raise OSError

# Initialize xbee object if Serial connetion successful
xbee = XBee(ser, escaped = True, callback=message_received)
print "XBEE Object CREATED"



# Defined to take in an xbee object
# Make sure not to send strings longer than 4 letters
def sendBroadcast(xbee, _data):
    print "XBEE Sending Broadcast"
    packed_data = tinypacks.pack(_data)
    xbee.tx(
        dest_addr = '\xFF\xFF',
        data = (packed_data) )






def triggerUnit_changeAnim( pitch ):
    animNumber = int(translate( pitch, 0, 127, 0, 3))
    # broadcastData = { "pNam" : "hue", "per" : huePercent }
    broadcastData = [ 1, animNumber ]
    sendBroadcast(xbee, broadcastData)

def triggerUnit_changeHue( pitch ):
    huePercent = translate( pitch, 0., 127., 0., 1.)
    # broadcastData = { "pNam" : "hue", "per" : huePercent }
    broadcastData = [ 1, huePercent ]
    sendBroadcast(xbee, broadcastData)

def triggerUnit_changeDecay( pitch ):
    decayPercent = translate( pitch, 0., 127., 0., 1.)
    # broadcastData = { "pNam" : "hue", "per" : huePercent }
    broadcastData = [ 2, decayPercent ]
    sendBroadcast(xbee, broadcastData)

def triggerPython_magnitudeCutoff( pitch ):
    global magnitudeCutoff
    magnitudeCutoff = translate( pitch, 0, 127., 0., 1.)



# --------------------------------------------
# --------------------------------------------
# x- INITIALIZE MIDI IN
# x- SET CALLBACK TO MIDI OUT
# SET CALLBACK TO INTERNAL STUFF


# DEFINE MIDI IN CALLBACK HERE -> PROBABLY ONLY REFERENCES INTERNAL VARIABLES AND XBEE
class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        print "MIDI Message Received [", message, "]"
        ("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
        
        # put handling data here...
        eventType = message[0] & 0xF0
        channel = message[0] & 0x0F
        address = message[1]
        pitch = message[2]





        # SET INTERNAL PARAMETER CHANGES HERE

        # SET XBEE OUT MESSAGES HERE
        if eventType is NOTE_ON and channel is 0x00:
                    print "Anim change triggered!"
                    triggerUnit_changeAnim( pitch )

        if eventType is NOTE_ON and channel is 0x01:
            print "Hue change triggered!"
            triggerUnit_changeHue( pitch )

        if eventType is NOTE_ON and channel is 0x02:
            print "Decay change triggered!"
            triggerUnit_changeDecay( pitch )

        if eventType is NOTE_ON and channel is 0x03:
            print "Tweak internal parameter"
            triggerPython_magnitudeCutoff( pitch )
            











# CREATE MIDI INPUT, ASSIGN CALLBACK FUNCTION
midiin = rtmidi.MidiIn()

# port = sys.argv[1] if len(sys.argv) > 1 else None
try:
    # midiin, port_name = open_midiport(port)
    midiin.open_virtual_port("Bionic Input")
    print "\"Bionic Input\" MIDI Channel Created"
except (EOFError, KeyboardInterrupt):
    sys.exit()

print("Attaching MIDI input callback handler")
midiin.set_callback(MidiInputHandler("Bionic Input"))














# --------------------------------------------
# --------------------------------------------


# MAIN LOOP
# Continuously read and print packets
print ""
print ""
print "--------------------"
print "--------------------"
print "Bionic-Python STARTED"
print "--------------------"
print "--------------------"
print "** Console Reports will trigger as events are received **"

while True:
    try:
        # if masterList['']
        # hueNow += 5
        # if hueNow > 255:
        #     hueNow -= 255
        # print hueNow

        # NEED TO BUILD INTO PROPER MODEL LOGIC STRUCTURE
        # Put broadcast data into structure and send out to units
        # 
        time.sleep(0.05)

        # print "magnitudeCutoff", magnitudeCutoff
        # print "----------"
        # print

    except KeyboardInterrupt:
        print "KeyboardInterrupt EXCEPT"
        break
    except:
        print "Generic EXCEPT"
        break




try:
    print "--------------------"
    print "--------------------"
    print "Bionic-Python Exiting..."
    xbee.halt()
    ser.close()
    midiin.close_port()
    del midiin
    midiout.close_port()
    del midiout
    print "Bionic-Python CLOSED"
    print "--------------------"
    print "--------------------"
except:
    print "Couldn't close!"
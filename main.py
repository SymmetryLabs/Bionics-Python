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
# x- INITIALIZE INTERNAL STUFF

# Main data structure for communications tracking
global allReports, numberStoredEntries
allReports = []
numberStoredEntries = 5000

global hueNow, magnitudeCutoff, timeMIDIsend
hueNow = 0
magnitudeCutoff = 0.3

huePercent = 0


timeMIDIsend = {}





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


def noteOn(channel, pitch, velocity):
    midiout.send_message([0x90 | channel, pitch, velocity])

def noteOff(channel, pitch, velocity):
    midiout.send_message([0x80 | channel, pitch, velocity])

def noteFor(channel, pitch, velocity, _time):
    noteOn(channel, pitch, velocity)
    time.sleep(_time)
    noteOff(channel, pitch, velocity)


# Use this for the 10/28 Bionic Test
def noteOnQuickly(channel, pitch, velocity):
    noteFor(channel, pitch, velocity, 0.02)

def effectOn():
    noteOn(93, 0)

def effectOff():
    noteOff(93, 0)

def effectOnFor(_time):
    effectOn()
    time.sleep(_time)
    effectOff()


# parameter ranges 0-3
# def effectParameterChange(parameter, value):
#     parameterAddress = 20 + parameter
#     mitiout.send_message([0xB0, parameterAddress, value])



# def boomMag(magnitude):
#     effectParameterChange(0, magnitude)

# def boomHue(magnitude):
#     effectParameterChange(3, magnitude)

# def boomX(magnitude):
#     effectParameterChange(1, magnitude)

# def boomY(magnitude):
#     effectParameterChange(2, magnitude)



# def boomXY(magX, magY):
#     boomX(magX)
#     boomY(magY)

# def boomParam(magnitude, x, y, hue):
#     boomMag(magnitude)
#     boomHue(hue)
#     boomXY(x, y)



# def boom(magnitude, x, y, hue):
#     boomParam(magnitude, x, y, hue)
#     note(93, 0)


# def boomRandom():
#     boom(random.randint(60, 100), random.randint(0, 127), random.randint(0, 127), random.randint(0, 127))

# def boomRandom(magnitude, hue):
#     boom(magnitude, random.randint(0, 127), random.randint(0, 127), hue)



# def previousEffect():
#     shiftOn()
#     note(97, 0)
#     shiftOff()

# def nextEffect():
#     shiftOn()
#     note(96, 0)
#     shiftOff()


# def shiftOn():
#     noteOn(98, 0)

# def shiftOff():
#     noteOff(98, 0)





# --------------------------------------------
# --------------------------------------------
# x- INITIALIZE XBEE
# x- SET XBEE CALLBACK TO MIDI OUT
# SET XBEE CALLBACK TO INTERNAL STUFF

def printReports(reports):
    for report in reports:
        print "-Start Report-"
        for message in report['msg']:
            print "message ", message
        print "-End Report-"


def getReportsFromXbeeMessage(response):
    global magnitudeCutoff, timeMIDIsend, allReports, numberStoredEntries
    print "response = ", response
    packed_data = response['rf_data']
    print "Size of packed_data ", len(packed_data)

    # Initialize unpacked_data so the while loop will execute at least once
    unpacked_data = {}
    reports = []
    messages = []
    unitID = response['source_addr'] # need to convert to string?
    # print "reponse keys = ", response.keys()
    # print "unitID = ", repr(unitID)
    timeStamp = datetime.now()

    while unpacked_data is not True and unpacked_data is not None:
        try:
            (unpacked_data, packed_data) = tinypacks.unpack(packed_data)
        except:
            e = sys.exc_info()[0]
            print e
            print ""
            print "ERROR DIAGNOSTICS"
            print "unpacked_data ", unpacked_data
            print "packed_data", packed_data
            print ""
            break
        # print "Unpacked Data: ", unpacked_data
        if unpacked_data is not True and unpacked_data is not None:
            reportToStore = {}
            reportToStore = unpacked_data
            reportToStore["time"] = datetime.now()
            reportToStore["unitID"] = unitID
            reports.insert( 0, reportToStore )
    #         print "Report stored!"
    # print "Unpacked all data into reports / messages"
    # print "# Reports = ", len(reports)
    # print "# Messages = ", len(messages)
    # print reports
    # print ""

    return reports




# ***************************************
# ***************************************
# *************   FILTERS   *************
# ***************************************
# ***************************************


global filter_midiMusic_timesSent
filter_midiMusic_timesSent = {}

def filter_midiMusicTrigger(unitID, messages):
    global filter_midiMusic_timesSent

    # If this is the first time receiving something from this xBee, add it to the timeMIDIsend dictionary
    if unitID not in filter_midiMusic_timesSent:
        filter_midiMusic_timesSent[unitID] = datetime.now()

    timeSinceLastTrigger = datetime.now() - filter_midiMusic_timesSent[unitID]

    aaRealPercent = 0
    anglePercent = 0

    # print messages
    for message in messages:
        if (unicode("lvl") == message["pNam"]):
            aaRealPercent = message["val"]
        elif (unicode("hue") == message["pNam"]):
            anglePercent = message["val"]

    if ( timeSinceLastTrigger ) > timedelta(milliseconds=30) and aaRealPercent > magnitudeCutoff:
        unitIDtoChannel = {'\x00\x00' : 3, '\x00\r' : 4, '\x00\n' : 1, '\x00\x0B' : 2}
        channel = unitIDtoChannel[unitID]
        noteOnQuickly( channel, 0, translate(aaRealPercent, 0, 1, 50, 127) )
        noteOnQuickly( channel, 1, translate(anglePercent, 0, 1, 50, 127) )
        filter_midiMusic_timesSent[unitID] = datetime.now()
        print "MIDI TRIGGER! Channel = ", channel 


def filter_rollParameter(unitID, message):
    if (unicode("hue") == message["pNam"]):
        roll = message["hue"]
        # WIP - WRITE PROPER MIDI MESSAGE HERE!!!







def determineMidiFromReports(reports):
    for report in reports:
        # for messages in report["msg"]:
        unitID = report["unitID"]
        messages = report["msg"]

        # LIST OF FILTER HERE!!!
        # print repr(unitID), " - Messages into filter: ", messages

        filter_midiMusicTrigger( unitID, messages )
                        
    # print ""








# MIDI OUT and notes must be enabled prior to this...
def message_received(response):
    global magnitudeCutoff, timeMIDIsend, allReports, numberStoredEntries

    # print "--------------------"
    # print "XBEE Message RECEIVED"        

    # Get the reports (all messages in a single transmission) from the xBee packet
    reports = getReportsFromXbeeMessage(response)
    # printReports(reports)

    # Process the report and trigger actions
    determineMidiFromReports(reports)

    # Store it when done
    # check to see if queue is too big
    for report in reports:
        while len(allReports) >= numberStoredEntries:
            allReports.pop() # remove last entry
        allReports.insert( 0, report )

    # print "--------------------"
    # print ""

# Attempt to make this variable static to the function
# message_received.timeMIDIsend = datetime.now()




PORTS = ['/dev/tty.usbserial-AM01VFA7', '/dev/tty.usbserial-A90FNX5T', '/dev/tty.usbserial-A94RVX9H']
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
        # print "filterTimes", filter_midiMusic_timesSent

        # print "magnitudeCutoff", magnitudeCutoff
        # print "----------"
        # print

    except KeyboardInterrupt:
        print "KeyboardInterrupt EXCEPT"
        break
    except IOError:
        print "IOError EXCEPT"
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

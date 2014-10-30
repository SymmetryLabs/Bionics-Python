# 2AM   10/28/2014 First Midi Test with New Framework

#! /usr/bin/python

"""
bionic_prototype_async.py

Based on bionic_prototype.py, but updated with new MIDI and packet processing

10/27/2014 - Used for first Bionic test!  Super ghetto.  Would love to add error catching...
"""

# Initialize xbee
from xbee import XBee
import serial


import SC


# Initialize tinypacks
import tinypacks
import struct
import time
from datetime import datetime
from datetime import timedelta


# 
# 
# From SC.py originally
import logging
import sys

import time
import rtmidi
import random

# From test_midiin_callback.py in rtmidi examples
from rtmidi.midiutil import open_midiport
log = logging.getLogger('test_midiin_callback')

# 
# 
# 


# Main data structure for communications tracking
masterList = {}
numberStoredEntries = 20

global hueNow
hueNow = 0

global timeMIDIsend
timeMIDIsend = datetime(2014, 9, 12, 11, 19, 54)




def message_received(response):
    global timeMIDIsend

    try:
        print "----------"
        print "Message received!"        

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
                    if aaRealPercent > 0.25:
                        SC.triggerMidiMusic( 63, translate(aaRealPercent, 0, 1, 60, 127) )
                        # SC.triggerMidiMusic( 63, 127 )
                        print "TRIGGER!"
                        timeMIDIsend = datetime.now()

            print ""
        except:
            print "Error in interaction engine"

    except:
        print "Parsing error in message_received" 


    # if "m_e" in unpacked_data.keys():
    #     if unpacked_data["m_e"] == 1 and unpacked_data["m"] > 100:
    #         mag = translate(unpacked_data["m"], 0, 1023, 95, 65)
    #         print "mag ", mag
    #         # if unitID == '\x00\x0C':
    #         #     SC.boomRandom(mag, 0)
    #         #     # print "C!"
    #         # elif unitID == '\x00\x0B':
    #         #     SC.boomRandom(mag, hueNow/255*127)
    #         # else:
    #         hueSC = 127 - (hueNow * 127/255)
    #         # print hueSC
    #         SC.boomRandom(mag,hueSC)
    print "----------"
    print ""



def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)



def sendBroadcast(xbee, _data):
    print "Sending broadcast"
    packed_data = tinypacks.pack(_data)
    # numberBytes = struct.pack('B', len(packed_data)) # evidently don't need this anymore
    xbee.tx(
        dest_addr = '\xFF\xFF',
        # data = (numberBytes + packed_data))
        data = (packed_data))












# 
# 
# From SC.py originally


def SCexit():
    print("Exit.")
    midiin.close_port()
    del midiin
    midiout.close_port()
    del midiout


def noteOn(address, value):
    midiout.send_message([0x92, address, value])

def noteOff(address, value):
    midiout.send_message([0x82, address, value])

def noteFor(address, value, _time):
    noteOn(address, value)
    time.sleep(_time)
    noteOff(address, value)

# Use this for the 10/28 Bionic Test
def note(address, value):
    noteFor(address, value, 0.02)

# Call noteOn/noteOff
# Pitch: Left/Right - Use roll
# Velocity: Magnitude - Use aaReal
def triggerMidiMusic(pitch, velocity):
    note(pitch, velocity)
    # noteOn(pitch, velocity)





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
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


# Main data structure for communications tracking
masterList = {}
numberStoredEntries = 20

global hueNow
hueNow = 0

global timeMIDIsend
timeMIDIsend = datetime(2014, 9, 12, 11, 19, 54)




def message_received(response):
    try:
        print "Message received!"        

        packed_data = response['rf_data']
        # Initialize unpacked_data so the while loop will execute at least once
        unpacked_data = 0

        while unpacked_data is not None:
            try:
                unpacked_data, packed_data = tinypacks.unpack(packed_data)
            except:
                print "Exit unpacking loop"
                break
            else:
                if unpacked_data is not None:
                    print unpacked_data


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

        # # print unpacked_data
        # if "msg" in unpacked_data.keys():
        #     valueList = unpacked_data["msg"]
        #     aaRealPercent = valueList["val"]
        #     if ( datetime.now() - timeMIDIsend ) > timedelta(milliseconds=30):
        #         if aaRealPercent > 0.25:
        #             SC.triggerMidiMusic( 63, translate(aaRealPercent, 0, 1, 60, 127) )
        #             # SC.triggerMidiMusic( 63, 127 )
        #             print "TRIGGER!"
        #             timeMIDIsend = datetime.now()

        print ""

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



def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)



def sendBroadcast(_data):
    packed_data = tinypacks.pack(_data)
    numberBytes = struct.pack('B', len(packed_data))
    xbee.tx(
        dest_addr = '\xFF\xFF',
        data = (numberBytes + packed_data))
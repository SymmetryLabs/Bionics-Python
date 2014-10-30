#! /usr/bin/python

"""
bionic_prototype.py

This is an older version, before I migrated to asynchronous xBee calls.

10/28/2014 - Not sure if it still works...
"""

import SC

# Initialize xbee
from xbee import XBee
import serial

# Initialize tinypacks
import tinypacks
import struct
import time
from datetime import datetime

PORT = '/dev/tty.usbserial-AM01VFA7'
BAUD_RATE = 57600
ser = serial.Serial(PORT, BAUD_RATE)
xbee = XBee(ser, escaped = True)

# Main data structure for communications tracking
masterList = {}
numberStoredEntries = 20

hueNow = 0

timeMIDIsend = datetime.now()

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


# tutu pumps in hue "h"
# arms pump in MagEvent "m_e"
def getCommunications():
    response = xbee.wait_read_frame()
    # print response
    (unpacked_data, remaining_data) = tinypacks.unpack(response['rf_data'])

    # tinypacks data structure, date added
    unpacked_data['time'] = datetime.now()
    unitID = response['source_addr'] # need to convert to string?

    ## Add to master list, with unitID as key
    # if masterList does not contain unitID, do something different
    if not unitID in masterList.keys():
        masterList[unitID] = []

    # check to see if queue is too big
    if len(masterList[unitID]) >= numberStoredEntries:
        masterList[unitID].pop() # remove last entry

    # insert most recent entry
    masterList[unitID].insert(0, unpacked_data)

    # print unpacked_data

    if "h" in unpacked_data.keys():
        hueNow = unpacked_data["h"]
        print "hue ", hueNow

    if "m_e" in unpacked_data.keys():
        if unpacked_data["m_e"] == 1 and unpacked_data["m"] > 200:
            mag = translate(unpacked_data["m"], 0, 1023, 100, 60)
            if unitID == '\x00\x0C':
                SC.boomRandom(mag, 0)
                # print "C!"
            elif unitID == '\x00\x0B':
                SC.boomRandom(mag, 120)
            else:
                SC.boomRandom(mag,127)




def sendBroadcast(_data):
    packed_data = tinypacks.pack(_data)
    numberBytes = struct.pack('B', len(packed_data))
    xbee.tx(
        dest_addr = '\x00\x0B',
        data = (numberBytes + packed_data))




# Continuously read and print packets
while True:
    try:
        # NEED TO BUILD IN PROPER LOGIC HERE
        getCommunications()

        # if masterList['']
        # hueNow += 1
        # if hueNow > 255:
        #     hueNow -= 255
        # print hueNow
        
        # NEED TO BUILD INTO PROPER MODEL LOGIC STRUCTURE
        # Put broadcast data into structure and send out to units
        # 
        broadcastData = {
            "h" : hueNow,
            "e1" : 0,
            "e2" : 0
            }
        # sendBroadcast( broadcastData )
        # print broadcastData
        # time.sleep(1)

    except KeyboardInterrupt:
        break
        
ser.close()
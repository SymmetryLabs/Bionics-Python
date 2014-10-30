#! /usr/bin/python

"""
receive_samples_tinypacks.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

This example continuously reads the serial port and processes IO data
received from a remote XBee.

Modified slightly by Trip to use TinyPacks with the old AiR Bionic Framework.
"""

from xbee import XBee
import serial

PORT = '/dev/tty.usbserial-AH01D5K8'
BAUD_RATE = 115200
ser = serial.Serial(PORT, BAUD_RATE)
xbee = XBee(ser, escaped = True )


import tinypacks
from datetime import datetime

# master collection of all data, accessed as masterList['ID_#'][entryNumber]['key']
masterList = {}
numberStoredEntries = 20



# Continuously read and print packets
while True:
    try:
        response = xbee.wait_read_frame()
        (unpacked_data, remaining_data) = tinypacks.unpack(response['rf_data'])
        print response
        # print "Unpacked: ", unpacked_data
        # Store data in some structure

        # tinypacks data structure, date added
        unpacked_data['time'] = datetime.now()
        unitID = response['source_addr'] # need to convert to string?

        # add to master list, with unitID as key

        # if masterList does not contain unitID, do something different
        if not unitID in masterList.keys():
        	masterList[unitID] = []

        # check to see if queue is too big
        if len(masterList[unitID]) >= numberStoredEntries:
        	masterList[unitID].pop() # remove last entry

        # insert most recent entry
        masterList[unitID].insert(0, unpacked_data)

        # print len(masterList[unitID])
        print

    except KeyboardInterrupt:
        break
        
ser.close()

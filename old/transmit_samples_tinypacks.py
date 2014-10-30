#! /usr/bin/python

"""
receive_samples.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

This example continuously reads the serial port and processes IO data
received from a remote XBee.
"""

from xbee import XBee
import serial

import struct
import time

PORT = '/dev/tty.usbserial-AH01D5K8'
BAUD_RATE = 57600
ser = serial.Serial(PORT, BAUD_RATE)
xbee = XBee(ser, escaped = True)

import tinypacks

sendData = 0

time.sleep(1);

# Continuously read and print packets
while True:
    try:
    	sendData+=5
    	if sendData > 255: sendData = 0

        data = {"bool": True, "int": sendData, "int": 10}
        print("Data: " +  repr(data))
        packed_data = tinypacks.pack(data)
        print("Packed data: " + repr(packed_data))

        # sendDataPacked = packed_data.encode('hex')
        numberBytes = struct.pack('B', len(packed_data))

        xbee.tx(dest_addr = '\xFF\xFF', data = (numberBytes + packed_data))

        # print xbee.wait_read_frame()
        time.sleep(1)

    except KeyboardInterrupt:
        break
        
ser.close()

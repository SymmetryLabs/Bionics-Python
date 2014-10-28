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

PORT = '/dev/tty.usbserial-AH01D5K8'
BAUD_RATE = 115200

# Open serial port
ser = serial.Serial(PORT, BAUD_RATE)

# Create API object
xbee = XBee(ser, escaped = True)

# Continuously read and print packets
while True:
    try:
        response = xbee.wait_read_frame()
        print response
        # print 'source: ', response['source_addr'].encode('hex'), '  ', int(response['rf_data'].encode('hex'), 16)
    except KeyboardInterrupt:
        break
        
ser.close()

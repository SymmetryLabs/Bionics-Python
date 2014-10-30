# --------------------------------------------
# --------------------------------------------
# IMPORT NECESSARY STUFF

import logging
import sys

import time
import rtmidi
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




# --------------------------------------------
# --------------------------------------------
# INITIALIZE MIDI OUT

midiout = rtmidi.MidiOut()
try:
    midiout.open_virtual_port("Bionic Output")
except:
	print "Couldn't create Bionic Output"




# --------------------------------------------
# --------------------------------------------
# INITIALIZE INTERNAL STUFF

# Main data structure for communications tracking
masterList = {}
numberStoredEntries = 20

global hueNow
hueNow = 0

huePercent = 0


# --------------------------------------------
# --------------------------------------------
# x- INITIALIZE XBEE
# x- SET XBEE CALLBACK TO MIDI OUT
# SET XBEE CALLBACK TO INTERNAL STUFF

# MIDI OUT and notes must be enabled prior to this...
def message_received(response):
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
                        message_received.timeMIDIsend = datetime.now()

            print ""
        except:
            print "Error in interaction engine"

    except:
        print "Parsing error in message_received" 
    print "----------"
    print ""

message_received.timeMIDIsend = datetime.now()




PORTS = ['/dev/tty.usbserial-AM01VFA7', '/dev/tty.usbserial-A90FNX5T']
BAUD_RATE = 115200
# Iterate through possible Serial Port Names looking for connected xBee Explorer
for port in PORTS:
    try:
        ser = serial.Serial(port, BAUD_RATE)
    except OSError:
        print "Unsuccessfully tried PORT = ", port
    else:
        print "Connected to PORT = ", port
        break
# Check to see if Serial successfully connected
try:
    ser
except:
    print "Serial didn't connect"
    raise OSError

# Initialize xbee object if Serial connetion successful
xbee = XBee(ser, escaped = True, callback=message_received)
print "Waiting for incoming messages..."



# Defined to take in an xbee object
def sendBroadcast(xbee, _data):
    print "Sending xBee broadcast"
    packed_data = tinypacks.pack(_data)
    xbee.tx(
        dest_addr = '\xFF\xFF',
        data = (packed_data))





# --------------------------------------------
# --------------------------------------------
# x- INITIALIZE MIDI IN
# SET CALLBACK TO MIDI OUT
# SET CALLBACK TO INTERNAL STUFF


# DEFINE MIDI IN CALLBACK HERE -> PROBABLY ONLY REFERENCES INTERNAL VARIABLES AND XBEE
class MidiInputHandler(object):
    def __init__(self, port, portOut):
        self.port = port
        self.portOut = portOut
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        print("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
        
        # put handling data here...
        # push to self.portOut




# CREATE MIDI INPUT, ASSIGN CALLBACK FUNCTION
midiin = rtmidi.MidiIn()

# port = sys.argv[1] if len(sys.argv) > 1 else None
try:
    # midiin, port_name = open_midiport(port)
    midiin.open_virtual_port("Bionic Input")
except (EOFError, KeyboardInterrupt):
    sys.exit()

print("Attaching MIDI input callback handler.")
midiin.set_callback(MidiInputHandler("Bionic Input", "Bionic Output"))




# --------------------------------------------
# --------------------------------------------


# MAIN LOOP
# Continuously read and print packets
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
        # print "hue ", hueNow
        time.sleep(0.1)

        huePercent+=0.05
        if huePercent > 1:
            huePercent = 0
        broadcastData = { "pName" : "hue", "per" : huePercent }
        sendBroadcast( xbee, broadcastData )
        print "Broadcasted: ", broadcastData
        print "----------"
        print

    except KeyboardInterrupt:
        print "KeyboardInterrupt EXCEPT"
        break
    except:
        print "Generic EXCEPT"
        break




try:
	print "Exiting..."
	xbee.halt()
	ser.close()
	midiin.close_port()
	del midiin
	midiout.close_port()
	del midiout
	print "Successfully closed!"
except:
	print "Couldn't close!"
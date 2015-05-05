# What's my current problem?
# unit -> xbee -> python xbee -> OSC -> Processing


# Processing -> OSC -> python osc -> python xbee -> unit -> deserialize at unit
# NEED:
# -serialize message in Python and pack into xbee : can I do this with liblo.send?...no, think I need message.serialise()

# --------------------------------------------
# --------------------------------------------
# x- IMPORT NECESSARY STUFF

import logging
import sys

from time import sleep
from datetime import datetime, timedelta


# Import OSC stuff
from liblo import *
import liblo


# Initialize xbee
from xbee import XBee
import serial





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
# -------------- OSC IN and OUT --------------
# --------------------------------------------
# --------------------------------------------

def OSCtoXbeeBroadcast(xbee, OSCmsg):
    # Convert from OSC message to byte stream of packed_data
    xbeeSendBroadcast( xbee, OSCmsg.serialise() )


def OSCtoXbeeMessage(xbee, address, OSCmsg):
    # Convert from OSC message to byte stream of packed_data
    xbeeSendMessage( xbee, address, OSCmsg.serialise() )


# OSC Server for receiving messages
class OSCServer(ServerThread):
    def __init__(self):
        ServerThread.__init__(self, 9049)

    @make_method(None, None)
    def fallback(self, path, args):
        print "--------------------"
        print "OSC CALLBACK FUNCTION"  
        print datetime.now(), "received message '%s', '%s'" % (path, args)

        # Is this what I want?  I should have something about the message address pick which xBee this goes to
        OSCtoXbeeBroadcast(xbee, msg)


try:
    server = OSCServer()
except ServerError, err:
    print str(err)
    sys.exit()

server.start()


# Send all messages to port 9050 on the local machine
try:
    targetOSC = liblo.Address(9050)
except liblo.AddressError, err:
    print str(err)
    sys.exit()


# Sends OSC messages to Processing port
def xBeeToOSCMessage(reports):
    # print "Report[0]: ", reports[0]
    msg = reports[0]["msg"]
    # print "Forwarding OSC Message: ", reports[0]["msg"]
    liblo.send(targetOSC, msg)




# --------------------------------------------
# --------------------------------------------
# ------------ XBEE IN and OUT ---------------
# --------------------------------------------
# --------------------------------------------


# Take in xBee response, return report {timestamp, address, OSCMessage}
def getOSCFromXbeeMessage(response):

    packed_data = response['rf_data']
    # print "xBee payload = ", packed_data
    # print "Size of xBee payload ", len(packed_data)

    # Take the bit data from xBee and extract the OSC Message (address, types, data)
    deserializedMessage = decodeOSC(packed_data)
    addr = deserializedMessage.pop(0)
    typeString = deserializedMessage.pop(0)
    data = []
    for type in typeString:
        if type is not ",":
            thisData = (type, deserializedMessage.pop(0))
            data.append( thisData )

    # print "Parsed OSC byte stream: ", addr, ", ", data

    # Add unit number to the address string
    # for byte in addr:
        # addr = 


    # Extract the message source
    unitID = response['source_addr'] # need to convert to string?
    # print "unitID: ", repr(unitID)
    # REALLY need to replace this with something even remotely slick... ;)
    if unitID == '\x00\x0A':
        unitID = 'A'
    elif unitID == '\x00\x0B':
        unitID = 'B'
    elif unitID == '\x00\x0C':
        unitID = 'C'
    elif unitID == '\x00\x0D':
        unitID = 'D'
    else:
        print "Address of unit not detected"

    addr = 'unit/' + unitID + addr


    # Add the OSC data to the OSCMessage object
    OSCmsg = liblo.Message(addr)
    for entry in data:
        OSCmsg.add(entry)


    # Record the message timestamp
    timeStamp = datetime.now()


    # Place the time, message, and source address into a report
    report = {}
    report["OSCmsg"] = OSCmsg
    report["time"] = datetime.now()
    report["unitID"] = unitID


    return report




# Called upon incoming xBee message
def message_received(response):
    # if response['id'] is not 'rx': 
    #     print "RESPONSE: ", response['id']
    # print "--------------------"
    # print "XBEE Message RECEIVED"

    # print "Response: ", response

    # If statement is to exclude poorly formatted xbee messages
    # Usually there is only one sent, when units start (all empty \x00)
    # Should eliminate this from xBee end...
    if ',' in response['rf_data']:
        report = getOSCFromXbeeMessage(response)
        # print "In message_received: ", reports

        # Pass OSC message through to Processing
        xBeeToOSCMessage(report)

    else:
        print "Received bad xBee message"

    # print "--------------------"
    # print ""





PORTS = ['/dev/tty.usbserial-AM01VFA7', '/dev/tty.usbserial-A90FNX5T', '/dev/tty.usbserial-A94RVX9H', '/dev/tty.usbserial-A40360V8']
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
def xbeeSendBroadcast(xbee, packed_data):
    print "--------------------"
    print "XBEE Sending Broadcast"
    # Have loads of options available here as arguments
    # frame_id - determines whether or not the target radio returns ACK
    # options = b'\x01 - disables ACK - determines whether or not local radio retries transmissions
    xbee.tx(
        dest_addr = '\xFF\xFF',
        # dest_addr = b'\x00\x0A',
        # frame_id = b'\x01',
        data = packed_data )

    print "--------------------"
    print ""


def xbeeSendMessage(xbee, address, packed_data):
    print "--------------------"
    print "XBEE Sending Message to ", address
    print "Packed_data: ", packed_data
    xbee.tx(
        dest_addr = address,
        # dest_addr = b'\x00\x0A',
        # frame_id = b'\x01',
        data = packed_data )

    print "--------------------"
    print ""



# --------------------------------------------
# --------------------------------------------
# x- OSC helpers.  MOVE TO PYLIBLO!


from pyOSCfunctions import *






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

try:
    while True:
        # NEED TO BUILD INTO PROPER MODEL LOGIC STRUCTURE
        # Put broadcast data into structure and send out to units
        # 
        # sleep(1)

        # Send test OSC messages to units
        # xbeeSendBroadcast(xbee, OSC_Tx_Test)
        # print "filterTimes", filter_midiMusic_timesSent

        # print "magnitudeCutoff", magnitudeCutoff
        # print "----------"
        # print
        pass

except KeyboardInterrupt:
    print "KeyboardInterrupt EXCEPT"
except IOError:
    print "IOError EXCEPT"
    # except:
    #     print "Generic EXCEPT"
    #     break




try:
    print "--------------------"
    print "--------------------"
    print "Bionic-Python Exiting..."
    xbee.halt()
    ser.close()
    server.stop()
    print "Bionic-Python CLOSED"
    print "--------------------"
    print "--------------------"
except:
    print "Couldn't close!"

# --------------------------------------------
# --------------------------------------------
# x- IMPORT NECESSARY STUFF

import logging
import sys

import time


# Import OSC stuff
from liblo import *
import liblo


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





# --------------------------------------------
# --------------------------------------------
# x- INITIALIZE OSC SERVER and CLIENT
# x- WRITE ALL MIDI FUNCTIONS

class MyServer(ServerThread):
    def __init__(self):
        ServerThread.__init__(self, 1234)

    @make_method('/foo', 'ifs')
    def foo_callback(self, path, args):
        i, f, s = args
        print "received message '%s' with arguments: %d, %f, %s" % (path, i, f, s)

    @make_method(None, None)
    def fallback(self, path, args):
        print "received unknown message '%s', '%s'" % (path, args)
        print path
        print args

try:
    server = MyServer()
except ServerError, err:
    print str(err)
    sys.exit()

server.start()


# send all messages to port 1234 on the local machine
try:
    targetOSC = liblo.Address(1234)
except liblo.AddressError, err:
    print str(err)
    sys.exit()


def forwardOSCMessage(reports):
    # print "Report[0]: ", reports[0]
    msg = reports[0]["msg"]
    print "Forwarding OSC Message: ", reports[0]["msg"]
    liblo.send(targetOSC, msg)



# WRITE FUNCTIONS FOR SENDING AND PACKING STUFF
# WHAT DO THE MESSAGES I SEND FORTH LOOK LIKE?



# --------------------------------------------
# --------------------------------------------
# x- INITIALIZE XBEE
# SET XBEE CALLBACK TO INTERNAL STUFF

def printReports(reports):
    for report in reports:
        print "-Start Report-"
        for message in report['msg']:
            print "message ", message
        print "-End Report-"


def getOSCFromXbeeMessage(response):
    reports = []

    packed_data = response['rf_data']
    print "xBee payload = ", packed_data
    print "Size of xBee payload ", len(packed_data)

    deserializedMessage = decodeOSC(packed_data)
    addr = deserializedMessage.pop(0)
    typeString = deserializedMessage.pop(0)
    data = []
    for type in typeString:
        if type is not ",":
            thisData = (type, deserializedMessage.pop(0))
            data.append( thisData )

    print "Parsed OSC byte stream: ", addr, ", ", data

    # Add unit number to the address string
    # for byte in addr:
        # addr = 

    unitID = response['source_addr'] # need to convert to string?
    print "unitID: ", repr(unitID)
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

    msg = liblo.Message(addr)
    for entry in data:
        msg.add(entry)

    timeStamp = datetime.now()

    reportToStore = {}
    reportToStore["msg"] = msg
    reportToStore["time"] = datetime.now()
    reportToStore["unitID"] = unitID

    reports.insert( 0, reportToStore )

    return reports





def message_received(response):
    global magnitudeCutoff, timeMIDIsend, allReports, numberStoredEntries

    print "--------------------"
    print "XBEE Message RECEIVED"        

    reports = getOSCFromXbeeMessage(response)
    # print "In message_received: ", reports

    # Pass OSC message through to Processing
    forwardOSCMessage(reports)

    # Process the report and trigger actions

    # Store it when done
    # check to see if queue is too big
    for report in reports:
        while len(allReports) >= numberStoredEntries:
            allReports.pop() # remove last entry
        allReports.insert( 0, report )

    print "--------------------"
    print ""





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




# --------------------------------------------
# --------------------------------------------
# x- OSC helpers.  MOVE TO PYLIBLO!


import math, string, struct


######
#
# OSCMessage decoding functions
#
######

def _readString(data):
    """Reads the next (null-terminated) block of data
    """
    length   = string.find(data,"\0")
    nextData = int(math.ceil((length+1) / 4.0) * 4)
    return (data[0:length], data[nextData:])

def _readBlob(data):
    """Reads the next (numbered) block of data
    """
    
    length   = struct.unpack(">i", data[0:4])[0]
    nextData = int(math.ceil((length) / 4.0) * 4) + 4
    return (data[4:length+4], data[nextData:])

def _readInt(data):
    """Tries to interpret the next 4 bytes of the data
    as a 32-bit integer. """
    
    if(len(data)<4):
        print "Error: too few bytes for int", data, len(data)
        rest = data
        integer = 0
    else:
        integer = struct.unpack(">i", data[0:4])[0]
        rest    = data[4:]

    return (integer, rest)

def _readLong(data):
    """Tries to interpret the next 8 bytes of the data
    as a 64-bit signed integer.
     """

    high, low = struct.unpack(">ll", data[0:8])
    big = (long(high) << 32) + low
    rest = data[8:]
    return (big, rest)

def _readTimeTag(data):
    """Tries to interpret the next 8 bytes of the data
    as a TimeTag.
     """
    high, low = struct.unpack(">ll", data[0:8])
    if (high == 0) and (low <= 1):
        time = 0.0
    else:
        time = int(high) + float(low / 1e9)
    rest = data[8:]
    return (time, rest)

def _readFloat(data):
    """Tries to interpret the next 4 bytes of the data
    as a 32-bit float. 
    """
    
    if(len(data)<4):
        print "Error: too few bytes for float", data, len(data)
        rest = data
        float = 0
    else:
        float = struct.unpack(">f", data[0:4])[0]
        rest  = data[4:]

    return (float, rest)

def decodeOSC(data):
    """Converts a binary OSC message to a Python list. 
    """
    table = {"i":_readInt, "f":_readFloat, "s":_readString, "b":_readBlob}
    decoded = []
    address,  rest = _readString(data)
    if address.startswith(","):
        typetags = address
        address = ""
    else:
        typetags = ""

    if address == "#bundle":
        time, rest = _readTimeTag(rest)
        decoded.append(address)
        decoded.append(time)
        while len(rest)>0:
            length, rest = _readInt(rest)
            decoded.append(decodeOSC(rest[:length]))
            rest = rest[length:]

    elif len(rest)>0:
        if not len(typetags):
            typetags, rest = _readString(rest)
        decoded.append(address)
        decoded.append(typetags)
        if typetags.startswith(","):
            for tag in typetags[1:]:
                value, rest = table[tag](rest)
                decoded.append(value)
        else:
            raise OSCError("OSCMessage's typetag-string lacks the magic ','")

    return decoded




######
#
# OSCError classes
#
######

class OSCError(Exception):
    """Base Class for all OSC-related errors
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class OSCClientError(OSCError):
    """Class for all OSCClient errors
    """
    pass

class OSCServerError(OSCError):
    """Class for all OSCServer errors
    """
    pass

class NoCallbackError(OSCServerError):
    """This error is raised (by an OSCServer) when an OSCMessage with an 'unmatched' address-pattern
    is received, and no 'default' handler is registered.
    """
    def __init__(self, pattern):
        """The specified 'pattern' should be the OSC-address of the 'unmatched' message causing the error to be raised.
        """
        self.message = "No callback registered to handle OSC-address '%s'" % pattern

class NotSubscribedError(OSCClientError):
    """This error is raised (by an OSCMultiClient) when an attempt is made to unsubscribe a host
    that isn't subscribed.
    """
    def __init__(self, addr, prefix=None):
        if prefix:
            url = getUrlStr(addr, prefix)
        else:
            url = getUrlStr(addr, '')

        self.message = "Target osc://%s is not subscribed" % url            








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
    server.stop()
    print "Bionic-Python CLOSED"
    print "--------------------"
    print "--------------------"
except:
    print "Couldn't close!"

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
        ServerThread.__init__(self, 9049)

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


# send all messages to port 9050 on the local machine
try:
    targetOSC = liblo.Address(9050)
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

while True:
    try:
        # NEED TO BUILD INTO PROPER MODEL LOGIC STRUCTURE
        # Put broadcast data into structure and send out to units
        # 
        sleep(1)

        # Send test OSC messages to units
        # sendBroadcast(xbee, OSC_Tx_Test)
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

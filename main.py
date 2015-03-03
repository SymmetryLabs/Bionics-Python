# --------------------------------------------
# --------------------------------------------
# x- IMPORT NECESSARY STUFF

import logging
import sys

import time


# Import OSC stuff
from OSC import *
from simpleOSC import *



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

    msg = OSCMessage(addr)
    for entry in data:
        msg.append(entry)

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
    # sys.exit(0)
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
# x- INITIALIZE OSC SERVER and CLIENT
# x- WRITE ALL MIDI FUNCTIONS


# Code taken directly from "app_example.py" in simpleOSC module

# CALLBACK FUNCTIONS
def checkcheckcheck(addr, tags, data, source):
    print "CHECK CHECK CHECK..."
    print "received new osc msg from %s" % getUrlStr(source)
    print "with addr : %s" % addr
    print "typetags :%s" % tags
    print "the actual data is : %s" % data



# Initialize client and server
initOSCClient('127.0.0.1', 9050) # takes args : ip, port
initOSCServer('127.0.0.1', 9049, 1) # takes args : ip, port, mode --> 0 for basic server, 1 for threading server, 2 for forking server


setOSCHandler('/check', checkcheckcheck)

startOSCServer() # and now set it into action

print 'ready to receive and send osc messages ...'




def forwardOSCMessage(reports):
    # print "Report[0]: ", reports[0]
    msg = reports[0]["msg"]
    print "Forwarding OSC Message: ", reports[0]["msg"]
    # liblo.send(targetOSC, msg)
    addr = msg[0]
    data = msg[1::]
    sendOSCMsg(addr, data)



# WRITE FUNCTIONS FOR SENDING AND PACKING STUFF
# WHAT DO THE MESSAGES I SEND FORTH LOOK LIKE?












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
        # time.sleep(1)

        # Send test OSC messages to units
        OSC_Tx_Test = OSCMessage("/foo/blah")
        # ... append arguments later...
        OSC_Tx_Test.append(123)
        OSC_Tx_Test.append("moo")
        # print "Sending OSC Test Message: ", OSC_Tx_Test

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
    except:
        print "Generic EXCEPT"
        break




try:
    print "--------------------"
    print "--------------------"
    print "Bionic-Python Exiting..."
    closeOSC()
    xbee.halt()
    ser.close()
    closeOSC()
    print "Bionic-Python CLOSED"
    print "--------------------"
    print "--------------------"
except:
    print "Couldn't close!"

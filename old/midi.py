import rtmidi
from rtmidi.midiconstants import *
import random

# From test_midiin_callback.py in rtmidi examples
from rtmidi.midiutil import open_midiport
log = logging.getLogger('test_midiin_callback')





timeMIDIsend = {}





# --------------------------------------------
# --------------------------------------------
# x- INITIALIZE MIDI OUT
# x- WRITE ALL MIDI FUNCTIONS
# TRY SORTING MIDI FUNCTIONS...

midiout = rtmidi.MidiOut()
try:
    midiout.open_virtual_port("Bionic Output")
    print "\"Bionic Output\" MIDI Channel Created"
except:
	print "Couldn't create Bionic Output"



def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


def noteOn(channel, pitch, velocity):
    midiout.send_message([0x90 | channel, pitch, velocity])

def noteOff(channel, pitch, velocity):
    midiout.send_message([0x80 | channel, pitch, velocity])

def noteFor(channel, pitch, velocity, _time):
    noteOn(channel, pitch, velocity)
    time.sleep(_time)
    noteOff(channel, pitch, velocity)


# Use this for the 10/28 Bionic Test
def noteOnQuickly(channel, pitch, velocity):
    noteFor(channel, pitch, velocity, 0.02)

def effectOn():
    noteOn(93, 0)

def effectOff():
    noteOff(93, 0)

def effectOnFor(_time):
    effectOn()
    time.sleep(_time)
    effectOff()


# parameter ranges 0-3
# def effectParameterChange(parameter, value):
#     parameterAddress = 20 + parameter
#     mitiout.send_message([0xB0, parameterAddress, value])



# def boomMag(magnitude):
#     effectParameterChange(0, magnitude)

# def boomHue(magnitude):
#     effectParameterChange(3, magnitude)

# def boomX(magnitude):
#     effectParameterChange(1, magnitude)

# def boomY(magnitude):
#     effectParameterChange(2, magnitude)



# def boomXY(magX, magY):
#     boomX(magX)
#     boomY(magY)

# def boomParam(magnitude, x, y, hue):
#     boomMag(magnitude)
#     boomHue(hue)
#     boomXY(x, y)



# def boom(magnitude, x, y, hue):
#     boomParam(magnitude, x, y, hue)
#     note(93, 0)


# def boomRandom():
#     boom(random.randint(60, 100), random.randint(0, 127), random.randint(0, 127), random.randint(0, 127))

# def boomRandom(magnitude, hue):
#     boom(magnitude, random.randint(0, 127), random.randint(0, 127), hue)



# def previousEffect():
#     shiftOn()
#     note(97, 0)
#     shiftOff()

# def nextEffect():
#     shiftOn()
#     note(96, 0)
#     shiftOff()


# def shiftOn():
#     noteOn(98, 0)

# def shiftOff():
#     noteOff(98, 0)





# ***************************************
# ***************************************
# *************   FILTERS   *************
# ***************************************
# ***************************************


global filter_midiMusic_timesSent
filter_midiMusic_timesSent = {}

def filter_midiMusicTrigger(unitID, messages):
    global filter_midiMusic_timesSent

    # If this is the first time receiving something from this xBee, add it to the timeMIDIsend dictionary
    if unitID not in filter_midiMusic_timesSent:
        filter_midiMusic_timesSent[unitID] = datetime.now()

    timeSinceLastTrigger = datetime.now() - filter_midiMusic_timesSent[unitID]

    aaRealPercent = 0
    anglePercent = 0

    # print messages
    for message in messages:
        if (unicode("lvl") == message["pNam"]):
            aaRealPercent = message["val"]
        elif (unicode("hue") == message["pNam"]):
            anglePercent = message["val"]

    if ( timeSinceLastTrigger ) > timedelta(milliseconds=30) and aaRealPercent > magnitudeCutoff:
        unitIDtoChannel = {'\x00\x00' : 3, '\x00\r' : 4, '\x00\n' : 1, '\x00\x0B' : 2}
        channel = unitIDtoChannel[unitID]
        noteOnQuickly( channel, 0, translate(aaRealPercent, 0, 1, 50, 127) )
        noteOnQuickly( channel, 1, translate(anglePercent, 0, 1, 50, 127) )
        filter_midiMusic_timesSent[unitID] = datetime.now()
        print "MIDI TRIGGER! Channel = ", channel 


def filter_rollParameter(unitID, message):
    if (unicode("hue") == message["pNam"]):
        roll = message["hue"]
        # WIP - WRITE PROPER MIDI MESSAGE HERE!!!







def determineMidiFromReports(reports):
    for report in reports:
        # for messages in report["msg"]:
        unitID = report["unitID"]
        messages = report["msg"]

        # LIST OF FILTER HERE!!!
        # print repr(unitID), " - Messages into filter: ", messages

        filter_midiMusicTrigger( unitID, messages )
                        
    # print ""






    def triggerUnit_changeAnim( pitch ):
    animNumber = int(translate( pitch, 0, 127, 0, 3))
    # broadcastData = { "pNam" : "hue", "per" : huePercent }
    broadcastData = [ 1, animNumber ]
    sendBroadcast(xbee, broadcastData)

def triggerUnit_changeHue( pitch ):
    huePercent = translate( pitch, 0., 127., 0., 1.)
    # broadcastData = { "pNam" : "hue", "per" : huePercent }
    broadcastData = [ 1, huePercent ]
    sendBroadcast(xbee, broadcastData)

def triggerUnit_changeDecay( pitch ):
    decayPercent = translate( pitch, 0., 127., 0., 1.)
    # broadcastData = { "pNam" : "hue", "per" : huePercent }
    broadcastData = [ 2, decayPercent ]
    sendBroadcast(xbee, broadcastData)

def triggerPython_magnitudeCutoff( pitch ):
    global magnitudeCutoff
    magnitudeCutoff = translate( pitch, 0, 127., 0., 1.)



# --------------------------------------------
# --------------------------------------------
# x- INITIALIZE MIDI IN
# x- SET CALLBACK TO MIDI OUT
# SET CALLBACK TO INTERNAL STUFF


# DEFINE MIDI IN CALLBACK HERE -> PROBABLY ONLY REFERENCES INTERNAL VARIABLES AND XBEE
class MidiInputHandler(object):
    def __init__(self, port):
        self.port = port
        self._wallclock = time.time()

    def __call__(self, event, data=None):
        message, deltatime = event
        self._wallclock += deltatime
        print "MIDI Message Received [", message, "]"
        ("[%s] @%0.6f %r" % (self.port, self._wallclock, message))
        
        # put handling data here...
        eventType = message[0] & 0xF0
        channel = message[0] & 0x0F
        address = message[1]
        pitch = message[2]



        # SET INTERNAL PARAMETER CHANGES HERE

        # SET XBEE OUT MESSAGES HERE
        if eventType is NOTE_ON and channel is 0x00:
                    print "Anim change triggered!"
                    triggerUnit_changeAnim( pitch )

        if eventType is NOTE_ON and channel is 0x01:
            print "Hue change triggered!"
            triggerUnit_changeHue( pitch )

        if eventType is NOTE_ON and channel is 0x02:
            print "Decay change triggered!"
            triggerUnit_changeDecay( pitch )

        if eventType is NOTE_ON and channel is 0x03:
            print "Tweak internal parameter"
            triggerPython_magnitudeCutoff( pitch )
            






# CREATE MIDI INPUT, ASSIGN CALLBACK FUNCTION
midiin = rtmidi.MidiIn()

# port = sys.argv[1] if len(sys.argv) > 1 else None
try:
    # midiin, port_name = open_midiport(port)
    midiin.open_virtual_port("Bionic Input")
    print "\"Bionic Input\" MIDI Channel Created"
except (EOFError, KeyboardInterrupt):
    sys.exit()

print("Attaching MIDI input callback handler")
midiin.set_callback(MidiInputHandler("Bionic Input"))


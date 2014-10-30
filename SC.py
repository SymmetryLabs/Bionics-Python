"""
SC.py

Contains all functions that create the virtual MIDI port and map to MIDI controls (channel, pitch, velocity, etc)

10/28/2014 - Works!
10/29/2014 - Adding ability to print incoming MIDI messages
"""


# --------------------------------------------
# --------------------------------------------

# Needs to come after the parsing functions
# Needs to come after MIDI out
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

# --------------------------------------------
# --------------------------------------------

#  CREATE MIDI OUTPUT
midiout = rtmidi.MidiOut()
try:
    midiout.open_virtual_port("Bionic Output")
except:
	print "Couldn't create Bionic Output"

# --------------------------------------------
# --------------------------------------------

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








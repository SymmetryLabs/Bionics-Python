"""
SC.py

Contains all functions that create the virtual MIDI port and map to MIDI controls (channel, pitch, velocity, etc)

10/28/2014 - Works!
"""

import time
import rtmidi
import random

midi = rtmidi.MidiOut()
available_ports = midi.get_ports()

if available_ports:
    midi.open_port(0)
else:
    midi.open_virtual_port("Bionic Arm")


def noteOn(address, value):
	midi.send_message([0x92, address, value])

def noteOff(address, value):
	midi.send_message([0x82, address, value])

def noteFor(address, value, _time):
	noteOn(address, value)
	time.sleep(_time)
	noteOff(address, value)

# Use this for the 10/28 Bionic Test
def note(address, value):
	noteFor(address, value, 0.02)

# Call noteOn/noteOff
# Pitch: Left/Right - Use roll
# Velocity: Magnitude - Use aaReal
def triggerMidiMusic(pitch, velocity):
	note(pitch, velocity)
	# noteOn(pitch, velocity)








def effectOn():
	noteOn(93, 0)

def effectOff():
	noteOff(93, 0)

def effectOnFor(_time):
	effectOn()
	time.sleep(_time)
	effectOff()


# parameter ranges 0-3
def effectParameterChange(parameter, value):
	parameterAddress = 20 + parameter
	midi.send_message([0xB0, parameterAddress, value])



def boomMag(magnitude):
	effectParameterChange(0, magnitude)

def boomHue(magnitude):
	effectParameterChange(3, magnitude)

def boomX(magnitude):
	effectParameterChange(1, magnitude)

def boomY(magnitude):
	effectParameterChange(2, magnitude)



def boomXY(magX, magY):
	boomX(magX)
	boomY(magY)

def boomParam(magnitude, x, y, hue):
	boomMag(magnitude)
	boomHue(hue)
	boomXY(x, y)



def boom(magnitude, x, y, hue):
	boomParam(magnitude, x, y, hue)
	note(93, 0)


def boomRandom():
	boom(random.randint(60, 100), random.randint(0, 127), random.randint(0, 127), random.randint(0, 127))

def boomRandom(magnitude, hue):
	boom(magnitude, random.randint(0, 127), random.randint(0, 127), hue)



def previousEffect():
	shiftOn()
	note(97, 0)
	shiftOff()

def nextEffect():
	shiftOn()
	note(96, 0)
	shiftOff()


def shiftOn():
	noteOn(98, 0)

def shiftOff():
	noteOff(98, 0)





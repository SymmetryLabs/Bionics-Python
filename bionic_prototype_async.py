# 2AM   10/28/2014 First Midi Test with New Framework

#! /usr/bin/python

"""
bionic_prototype_async.py

Based on bionic_prototype.py, but updated with new MIDI and packet processing

10/27/2014 - Used for first Bionic test!  Super ghetto.  Would love to add error catching...
"""




def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)



def sendBroadcast(xbee, _data):
    print "Sending xBee broadcast"
    packed_data = tinypacks.pack(_data)
    xbee.tx(
        dest_addr = '\xFF\xFF',
        data = (packed_data))




# --------------------------------------------
# --------------------------------------------

# 
# 
# From SC.py originally


def SCexit():
    


def noteOn(address, value):
    midiout.send_message([0x92, address, value])

def noteOff(address, value):
    midiout.send_message([0x82, address, value])

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
    mitiout.send_message([0xB0, parameterAddress, value])



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
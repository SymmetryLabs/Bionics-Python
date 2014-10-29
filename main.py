# main.py

from bionic_prototype_async import *


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
        time.sleep(.2)

        # broadcastData = {
        #     "h" : hueNow
        #     # "e1" : 0,
        #     # "e2" : 0
        #     }
        # sendBroadcast( broadcastData )
        # print broadcastData
        # time.sleep(1)

    except KeyboardInterrupt:
        print "KeyboardInterrupt EXCEPT"
        break
    except:
        print "Generic EXCEPT"
        break

try:
	xbee.halt()
	ser.close()
	print "Successfully closed!"
except:
	print "Couldn't close!"
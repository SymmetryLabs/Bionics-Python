# main.py

from bionic_prototype_async import *


# PORT = '/dev/tty.usbserial-AM01VFA7'
PORT = '/dev/tty.usbserial-A90FNX5T'
BAUD_RATE = 115200
ser = serial.Serial(PORT, BAUD_RATE)
xbee = XBee(ser, escaped = True, callback=message_received)



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
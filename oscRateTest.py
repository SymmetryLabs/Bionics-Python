# Script to run to test the effects of various OSC message rates on the Processing code

import liblo, sys
from time import sleep, strftime

# Rate in Hz
rate = 200.
rateDelay = 1./rate

print ""
print ""
print ""
print "--------------------"
print "--------------------"
print "OSC Rate Test INITIALIZING..."
print "--------------------"
print "--------------------"
print ""

print "Running with RATE = ", rate, " Hz"
print ""
print "Sending messages in 5 seconds..."
print ""
sleep(5)

# send all messages to port 1234 on the local machine
try:
    target = liblo.Address(9050)
except liblo.AddressError, err:
    print str(err)
    sys.exit()


while True:
	try:
		# Send test message with 3 floats to simulate the accelerometer data
		liblo.send(target, "/unit/A/m/a/r", 0.001, 0.987, 0.456)

		print "Message sent @ ", strftime('%X %x %Z')

		# Delay to achieve the set rate
		sleep(rateDelay)

	except KeyboardInterrupt:
		break

print "	"
print "OSC Rate Test END"
print "--------------------"
print "--------------------"
print ""
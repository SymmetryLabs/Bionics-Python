import json
from datetime import datetime, timedelta

from DataIOClasses import DataWriter, DataReader


print ""
print "RUNNING DATAWRITER CODE"

datawriter = DataWriter('testData.txt')
startTime = datetime.now()

msgJ = {'path': '/foo/message2', 'data': [3.1415, 4398046511104, 'x']}

for i in range(0,200*10):
	currentMsg = msgJ
	currentTime = datetime.now()
	elapsedTime = currentTime - startTime
	currentMsg['time'] = elapsedTime

	# Call whenever you need to add an entry
	# Entry JSON: {'path', 'data', 'time':timedelta}
	datawriter.addEntry(currentMsg)

datawriter.close()


print ""
print "RUNNING DATAREADER CODE"

datareader = DataReader('testData.txt')
messageHistory = datareader.getEntries()
print messageHistory
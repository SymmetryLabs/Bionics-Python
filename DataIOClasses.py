import json
from datetime import datetime, timedelta


class DataWriter:
	def __init__(self, filename):
		self._filename = filename
		self._outputfile = open(filename, 'w')

	def close(self):
		self._outputfile.close()

	def _stringifyEntry(self, JSONentry):
		JSONentry['time'] = str( JSONentry['time'].total_seconds() )
		return JSONentry

	def addEntry(self, JSONentry):
		# Convert time stamp to a string
		# Receives JSON {'path', 'data', 'time' : timedelta}
		formattedEntry = self._stringifyEntry(JSONentry)

		json.dump(formattedEntry, self._outputfile)
		self._outputfile.write('\n')


class DataReader:
	def __init__(self, filename):
		self._filename = filename
		self._inputfile = open(filename, 'r')
		self._lines = self._inputfile.readlines()
		self._inputfile.close()

	def getEntries(self):
		messages = []
		for line in self._lines:
			messages.append( self._processLine(line) )

		return messages

	def _processLine(self, line):
		message = json.loads(line)
		message['time'] = timedelta( seconds = float(message['time']) )
		return message
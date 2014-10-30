#!/usr/bin/python
#
# TinyPacks pack/unpack example
#

import tinypacks
import binascii

data = {"status": True, "count": 123, "boolean": True}
print("Data: " +  repr(data))

packed_data = tinypacks.pack(data)
# print("Packed: " + binascii.hexlify(packed_data))

for c in packed_data:
	print c.encode('hex')

# (unpacked_data, remaining_data) = tinypacks.unpack(packed_data)
# print("Unpacked: " + repr(unpacked_data))

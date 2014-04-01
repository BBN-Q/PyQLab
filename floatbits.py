import struct

def floatToBits(f):
	s = struct.pack('>f', f)
	return struct.unpack('>l', s)[0]

def bitsToFloat(b):
	s = struct.pack('>l', b)
	return struct.unpack('>f', s)[0]

def prevfloat(f):
	return bitsToFloat(floatToBits(f)-1)

def nextfloat(f):
	return bitsToFloat(floatToBits(f)+1)

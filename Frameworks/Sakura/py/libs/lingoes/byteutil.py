# coding: utf8
# byteutil.py
# 1/15/2013 jichi

INT8SIZE = 1
INT16SIZE = 2
INT32SIZE = 3
INT64SIZE = 4

def toint8(data, offset=0): # str, int -> int
  return ord(data[offset])

def toint16(data, offset=0): # str, int -> int
  return (ord(data[offset])
      + (ord(data[offset+1]) << 8))

def toint32(data, offset=0): # str, int -> int
  return (ord(data[offset])
      + (ord(data[offset+1]) << 8)
      + (ord(data[offset+2]) << 8*2)
      + (ord(data[offset+3]) << 8*3))

def toint64(data, offset=0): # str, int -> int
  return (ord(data[offset])
      + (ord(data[offset+1]) << 8)
      + (ord(data[offset+2]) << 8*2)
      + (ord(data[offset+3]) << 8*3)
      + (ord(data[offset+4]) << 8*4)
      + (ord(data[offset+5]) << 8*5)
      + (ord(data[offset+6]) << 8*6)
      + (ord(data[offset+7]) << 8*7))

def iterint32(data, start, stop):
  for i in xrange(start, stop, INT32SIZE): # sizeof() is 4
    yield toint32(data, i)

tobyte = toint8
toshort = toint16
toint = toint32
tolong = toint64

iterint = iterint32

# EOF

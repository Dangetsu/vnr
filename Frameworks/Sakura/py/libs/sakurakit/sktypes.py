# coding: utf8
# sktypes.py
# 10/22/2012 jichi

## C Types ##

from ctypes import c_long, c_ulong, c_longlong, c_ulonglong

def long_(i):   return c_long(i).value
def ulong(i):   return c_ulong(i).value

def llong(i):   return c_longlong(i).value
def ullong(i):  return c_ulonglong(i).value

def int64(i):   return llong(i)

# See: http://docs.scipy.org/doc/numpy/user/basics.types.html
def uint8(s):   return u & 255
def uint16(s):  return u & 65535
def uint32(s):  return u & 4294967295
def uint64(u):  return u & 18446744073709551615

## Type-checking ##

def is_float(v):
  """
  @param  v  any
  @return  bool
  """
  # http://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-in-python
  # This method is not slow
  try: float(v); return True
  except (TypeError, ValueError): return False

#def is_int(v):
#  """
#  @param  v  any
#  @return  bool
#  """
#  if isinstance(v, basestring):
#    return v.isdigit() # or isnumeric for unicode
#  else:
#    try: int(v); return True
#    except (TypeError, ValueError): return False

## Conversions ##

def to_int(v):
  """@nothrow"""
  try: return int(v)
  except (TypeError, ValueError): return 0

def to_long(v):
  """@nothrow"""
  try: return long(v)
  except (TypeError, ValueError): return 0L

def to_str(v):
  """@nothrow"""
  """Note: In Python, str(None) == 'None'"""
  return "%s" % (v or "")

def to_unicode(v):
  """@nothrow"""
  try: return unicode(v) if v else u""
  except (ValueError, TypeError, UnicodeDecodeError): return u""

# EOF

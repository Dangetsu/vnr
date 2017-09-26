# coding: utf8
# skhash.py
# 10/22/2012 jichi
#
# For string hash, see: http://www.cse.yorku.ca/~oz/hash.html
#
# TODO: use numpy.add.accumulate instead of reduce

## String hashing algorithms ##

import hashlib
from skstr import signed_ord
from sktypes import long_, ulong, llong, ullong

import numpy
#numpy.seterr(all='ignore')  # ignore overflow warning

DJB2_HASH = 5381

def djb2(L, rehash=None):
  """
  C:
    ulong
    hash(const uchar *str, ulong hash=5381)
    {
      int c;
      while (c = *str++)
        hash = ((hash << 5) + hash) + c; /* hash * 33 + c */
      return hash;
    }

  Python:
     h = 5381
     for c in L:
       h = ((h << 5) + h) + ord(c) # h * 33 + c
     return h
  """
  return reduce(lambda h,c: ord(c) + ((h << 5) + h), L,
      DJB2_HASH if rehash is None else rehash)

def djb2_l(L, rehash=None):
  return reduce(lambda h,c: long_(ord(c) + ((h << 5) + h)), L,
      DJB2_HASH if rehash is None else rehash)

def djb2_ul(L, rehash=None):
  return reduce(lambda h,c: ulong(ord(c) + ((h << 5) + h)), L,
      DJB2_HASH if rehash is None else rehash)

def djb2_ll(L, rehash=None):
  return reduce(lambda h,c: llong(ord(c) + ((h << 5) + h)), L,
      DJB2_HASH if rehash is None else rehash)

def djb2_ull(L, rehash=None):
  return reduce(lambda h,c: ullong(ord(c) + ((h << 5) + h)), L,
      DJB2_HASH if rehash is None else rehash)

def djb2_64(L, rehash=None):
  """
  @param  L  bytearray or str or unicode not None
  @param  rehash  long or None
  @return  long

  _64: overflow with type of int64
  """
  h = numpy.int64(DJB2_HASH if rehash is None else rehash)
  # Lambda not used to improve performance
  #return long(reduce(lambda h,c: ord(c) + ((h << 5) + h), L, h))
  for c in L:
    h += (h << 5) + ord(c)
  return long(h)

def djb2_64_s(L, rehash=None):
  """
  @param  L  bytearray or str or unicode not None
  @param  rehash  long or None
  @return  long

  _64: overflow with type of int64
  _s: signed char instead of uchar.

  Unsigned char is better in performance and clash rate.
  Using signed char is only for backward compatibility with existing subtitles.
  """
  h = numpy.int64(DJB2_HASH if rehash is None else rehash)
  # Lambda not used to improve performance
  #return long(reduce(lambda h,c: signed_ord(c) + ((h << 5) + h), L, h))
  for c in L:
    h += (h << 5) + signed_ord(c)
  return long(h)

def djb2_64_s_nz(L, rehash=None):
  """
  @param  L  bytearray or str or unicode not None
  @param  rehash  long or None
  @return  long

  _64: overflow with type of int64
  _s: signed char instead of uchar.
  _nz: skip zero. Only for backward compatibility of subs from Zky
  """
  h = numpy.int64(DJB2_HASH if rehash is None else rehash)
  for c in L:
    if not ord(c):
      break
    h += (h << 5) + signed_ord(c) # h * 33 + c
  return long(h)

def sdbm(L, rehash=0):
  """
  C:
    ulong
    sdbm(const uchar *str, ulong hash=0)
    {
      int c;
      while (c = *str++)
        hash = c + (hash << 6) + (hash << 16) - hash;
      return hash;
    }

  Python:
    h = 0
    for c in L:
      h = ord(c) + (h << 6) + (h << 16) - h
    return h
  """
  return reduce(lambda h,c: ord(c) + (h << 6) + (h << 16) - h, L, rehash or 0)

def sdbm_l(L, rehash=0):
  return reduce(lambda h,c: long_(ord(c) + (h << 6) + (h << 16) - h), L, rehash or 0)

def sdbm_ul(L, rehash=0):
  return reduce(lambda h,c: ulong(ord(c) + (h << 6) + (h << 16) - h), L, rehash or 0)

def sdbm_ll(L, rehash=0):
  return reduce(lambda h,c: llong(ord(c) + (h << 6) + (h << 16) - h), L, rehash or 0)

def sdbm_ull(L, rehash=0):
  return reduce(lambda h,c: ullong(ord(c) + (h << 6) + (h << 16) - h), L, rehash or 0)

def sdbm_64(L, rehash=0):
  rehash = numpy.int64(rehash or 0)
  return reduce(lambda h,c: ord(c) + (h << 6) + (h << 16) - h, L, rehash)

def loselose(L, rehash=0):
  """
  C:
    uint
    hash(const uchar *str, uint hash=0)
    {
      int c;
      while (c = *str++)
        hash += c;
      return hash;
    }

  Python:
    h = 0
    for c in L:
      h += ord(c);
    return h
  """
  return sum(ord(c) for c in L) + (rehash or 0)
  #return sum(imap(L,ord)) + (rehash or 0)

def loselose_l(L, rehash=0):
  return reduce(lambda h,c: long_(ord(c) + h), L, rehash or 0)

def loselose_ul(L, rehash=0):
  return reduce(lambda h,c: ulong(ord(c) + h), L, rehash or 0)

def loselose_ll(L, rehash=0):
  return reduce(lambda h,c: llong(ord(c) + h), L, rehash or 0)

def loselose_ull(L, rehash=0):
  return reduce(lambda h,c: ullong(ord(c) + h), L, rehash or 0)

def loselose_64(L, rehash=0):
  rehash = numpy.int64(rehash or 0)
  return reduce(lambda h,c: ord(c) + h, L, rehash or 0)

## File hashing algorithms ##

# See: http://stackoverflow.com/questions/1131220/get-md5-hash-of-a-files-without-open-it-in-python
def md5sumpath(path):
  """Return the MD5 digest of the file
  @param  path  str  input file path
  @return  str  md5 in lowercase hex string
  """
  try:
    # Change to UNC path: http://stackoverflow.com/questions/7169845/using-python-how-can-i-access-a-shared-folder-on-windows-network
    if path.startswith('/') and not path.startswith('//'):
      path = '/' + path
    md5 = hashlib.md5()
    with open(path,'rb') as f:
      chunk_size =128 * md5.block_size
      for chunk in iter(lambda: f.read(chunk_size), b''):
        md5.update(chunk)
    return md5.hexdigest()
  #except IOError: return ""
  except: return ""

def md5sumdata(data):
  """Return the MD5 digest of the data
  @param  data  str
  @return  str  md5 in lowercase hex string
  """
  return hashlib.md5(data).hexdigest()

if __name__ == '__main__':
  print md5sumfile("s:/hg/service/main/web-app/images/avatars/default.png")

# EOF

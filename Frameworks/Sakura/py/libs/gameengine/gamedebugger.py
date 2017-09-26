# coding: utf8
# gamedebugger.py
# 10/3/2013 jichi
# Windows only
# See: http://code.google.com/p/paimei/source/browse/trunk/MacOSX/PaiMei-1.1-REV122/build/lib/pydbg/pydbg.py?r=234

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import math
from itertools import imap
from sakurakit.skdebug import dprint, dwarn

# Default values in CheatEngine
#SEARCH_START = 0x0
#SEARCH_STOP = 0x7fffffff
#SEARCH_START =  0x400000    # base address for most games
#SEARCH_LENGTH = 0x300000    # range to search

class debug(object):
  def __init__(self, pid):
    """
    @param  pid  long
    """
    self.pid = pid

  def __enter__(self):
    self.debugger = GameDebugger(pid)
    if self.debugger.active:
      return self.debugger

  def __exit__(self, *err): pass

def _empty_func(self, *args, **kwargs): pass

#def _isregex(pattern):
#  """
#  @param  pattern  str
#  @return  bool
#  """
#  for ch in '.?*[]()':
#    if ch in pattern:
#      return True
#  return False

class GameDebugger(object):
  def __init__(self, pid):
    """
    @param  pid  long
    """
    self.pid = pid # long

    from pysafedbg import pysafedbg
    self.debugger = pysafedbg() # pydbg

    if self.pid:
      try: self.debugger.attach(self.pid)
      except Exception, e:
        dwarn(e)
        self.pid = 0
    dprint("pass")

  def __del__(self):
    dprint("pass")
    if self.pid:
      try: self.debugger.detach()
      except Exception, e: dwarn(e)

  def active(self):
    """
    Wreturn  bool
    """
    return bool(self.pid)

  # Debug

  def dump_module_names(self): # debug only
    dprint("enter")
    for it in self.iterate_modules():
      dprint(it.szModule)
    dprint("leave")

  # Modules

  def iterate_modules(self):
    """
    @yield  module  MODULEENTRY32
    """
    if self.debugger and self.pid:
      for it in self.debugger.iterate_modules():
        yield it

  def get_module(self, moduleName=None):
    """
    @param  moduleName  str or None
    @return   module or None
    """
    if moduleName:
      moduleName = moduleName.lower()
      for module in self.iterate_modules():
        if module.szModule.lower() == moduleName:
          return module
    else:
      for module in self.iterate_modules():
        return module

  def get_module_range(self, moduleName=None):
    """
    @param  moduleName  str or None
    @return  (int lowerBound, int upperBound) or None
    """
    module = self.get_module(moduleName)
    if module:
      return module.modBaseAddr, module.modBaseAddr + module.modBaseSize

  def hit_module(self, addr):
    """Memory address hit test
    @param  addr  long
    @return  module  where the address falls in
    """
    for module in self.iterate_modules():
      if addr >= module.modBaseAddr and addr < module.modBaseAddr + module.modBaseSize:
        return module

  # Search

  def search_module_memory(self, pattern, moduleName=None):
    """Search memory
    @param  pattern  int or str or [int]
    @param  moduleName  str
    @return  long  addr
    """
    r = self.get_module_range(moduleName)
    return self.search_memory(pattern, start=r[0], stop=r[1]) if r else -1

  def search_memory(self, pattern, *args, **kwargs):
    """Search memory
    @param  pattern  int or [int] or str
    @return  long  addr
    """
    if isinstance(pattern, (int, long)):
      return self.search_memory_long(pattern, *args, **kwargs)
    elif isinstance(pattern, (list, tuple)):
      return self.search_memory_list(pattern, *args, **kwargs)
    #elif isinstance(pattern, basestring): #, re._pattern_type)):
    #  return self.search_memory_string(pattern, *args, **kwargs)
    else:
      return self.search_memory_string(pattern, *args, **kwargs)
    #else:
    #  dwarn("invalid pattern type: %s" % type(pattern))
    #  return -1

  def search_memory_long(self, pattern, *args, **kwargs):
    """Search memory
    @param  pattern  int
    @return  long  addr
    """
    # http://stackoverflow.com/questions/6187699/how-to-convert-integer-value-to-array-of-four-bytes-in-python
    r = xrange(int(math.log(pattern, 2)/8) * 8, -1, -8)
    s = (pattern >> i & 0xff for i in r)
    return self.search_memory_list(s, *args, **kwargs)

  def search_memory_list(self, pattern, *args, **kwargs):
    """Search memory
    @param  pattern  [int]
    @return  long  addr
    """
    pattern = ''.join(imap(chr, pattern))
    return self.search_memory_string(pattern, *args, **kwargs)

  #def search_memory_string(self, pattern, *args, **kwargs):
  #  """Search memory with printable string pattern
  #  @param  pattern  str
  #  @return  long  addr
  #  """
  #  pattern = ''.join(imap(_hex2chr, pattern))
  #  return self.search_memory_binary(pattern, *args, **kwargs)

  def search_memory_string(self, pattern, start, stop):
    """Search memory with unprintable raw string pattern
    @param  pattern  str or regular expression
    @param  start  int  search memory lower bound
    @param  stop  int  search memory upper bound
    @return  long  addr
    See:  http://paimei.googlecode.com/svn-history/r234/trunk/MacOSX/PaiMei-1.1-REV122/build/lib/pydbg/pydbg.py
    """
    if stop <= start:
      return 0

    #if start > stop:
    #  return -1
    #import re
    #rx = re.compile(pattern)

    if isinstance(pattern, basestring):
      find = lambda s, t: s.find(t) # str, str -> int
    else:
      #assert isinstance(pattern, re._pattern_type)
      def find(s, t): # str, str -> int
        m = t.search(s)
        return m.start() if m else -1

    from pydbg import defines
    skipped_perms = defines.PAGE_GUARD|defines.PAGE_NOACCESS|defines.PAGE_READONLY

    pydbg = self.debugger
    cursor  = start
    # scan through the entire memory range and save a copy of suitable memory blocks.
    while cursor < stop:
      try: mbi = pydbg.virtual_query(cursor)
      except: break # out of region
      #if(mbi.BaseAddress):
      #  print ("%08x, size %x " % (mbi.BaseAddress, mbi.RegionSize))

      if not mbi.Protect & skipped_perms:
        # read the raw bytes from the memory block.
        try:
          data = pydbg.read_process_memory(mbi.BaseAddress, mbi.RegionSize)
          offset = find(data, pattern)
          if offset >= 0:
            return mbi.BaseAddress + offset
        except: pass # ignore accessed denied
      cursor += mbi.RegionSize
    return -1

          #m = rx.search(data[loc:])
          #if m:
          #  return mbi.BaseAddress + m.start()
          # Find all matched string
          #loc = 0
          #m = rx.search(data[loc:])
          #while m:
          #  #loc += m.span()[0] + 1
          #  loc += m.start() + 1
          #  addy = mbi.BaseAddress + loc - 1
          #  rounded_addy = addy & 0xfffffff0
          #  # convert addy from int to long
          #  addy = rounded_addy + (addy & 0x0000000f)
          #  rounded_size = ((32 + len(pattern) - (16 - (addy - rounded_addy)) ) / 16) * 16
          #  data = pydbg.read_process_memory(rounded_addy, rounded_size)
          #  #print pydbg.hex_dump(data, rounded_addy)
          #  return rounded_addy
          #  m = rx.search(data[loc:]) # continue searching

if __name__ == '__main__':
  # BALDRSKY ZERO
  # See: http://9gal.com/read.php?tid=411756
  #pattern = 0x90ff503c83c4208b45ec
  pattern = 0x90, 0xff, 0x50, 0x3c, 0x83, 0xc4, 0x20, 0x8b, 0x45, 0xec

  pid = 8096
  d = GameDebugger(pid=pid)
  if d.active():
    addr = 0x0120f9b0
    m = d.hit_module(addr)
    if m:
      print m.szModule

    #addr = d.searchbytes(pattern)
    #print hex(addr)

# EOF

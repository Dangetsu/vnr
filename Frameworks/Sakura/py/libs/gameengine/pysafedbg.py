# coding: utf8
# pysafedbg
# 4/19/2014 jichi

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

from pydbg import pydbg

# This class requires the original pydbg to have object type
# Disable debug privilege which could break AlphaROM
class pysafedbg(pydbg):

  def __init__(self, *args, **kwargs):
    super(pysafedbg, self).__init__(*args, **kwargs)

  def get_debug_privileges(self): pass # override
  def debug_active_process(self, pid): pass # override

if __name__ == '__main__':
  dbg = pynodbg()
  pid = 123
  dbg.attach(pid)

# EOF

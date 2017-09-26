# coding: utf8
# regsvr32.py
# 8/18/2014 jichi
import os

def run(dllpath, *args):
  """
  @param  dllpath  unicode
  @param* args  [unicode]
  @return  bool
  """
  cmd = 'regsvr32.exe "%s"' % dllpath
  if args:
    cmd += ' '.join(args)
  return os.system(cmd) == 0 # 0 when succeed

# EOF

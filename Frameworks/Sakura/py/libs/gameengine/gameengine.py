# coding: utf8
# gameengine.py
# 10/3/2013 jichi
# Windows only

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

from sakurakit.skdebug import dwarn

def inject(pid):
  """
  @param  pid  long
  @return  bool
  """
  from engines import engines
  try:
    for eng in engines():
      if eng.match(pid):
        return eng.inject(pid)
  except Exception, e:
    dwarn(e)
  return False

# EOF

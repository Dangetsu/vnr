# coding: utf8
# applocale.py
# 11/19/2012

from sakurakit.skdebug import dprint
from sakurakit import skpaths, skwin
import os

def create_environ(lcid):
  """
  @param  lcid  int  ms lcid
  @return  tuple
  """
  return (
    ('__COMPAT_LAYER', '#APPLICATIONLOCALE'),
    ('AppLocaleID', '%.4x' % lcid),
  )

def create_process(path, lcid, params=None):
  """
  @param  path  str  path to executable
  @param  lcid  int  ms lcid
  @param  params  [unicode] or None
  @return  long  pid
  """
  dprint("enter: lcid = 0x%.4x, path = %s" % (lcid, path))
  env = create_environ(lcid)
  pid = skwin.create_process(path, environ=env, params=params)
  dprint("leave: pid = %i" % pid)
  return pid

def exists():
  """
  @return  bool
  """
  ret = os.path.exists(skpaths.WINDIR + "/AppPatch/AlLayer.dll")
  dprint("ret = %s" % ret)
  return ret

# EOF

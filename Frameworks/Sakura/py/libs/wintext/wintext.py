# coding: utf8
# wintext.py
# 6/22/2013 jichi
# http://bytes.com/topic/python/answers/570252-reading-text-labels-win32-window
# Windows only

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

from sakurakit import skos
from sakurakit.skdebug import derror, dwarn

SUPPORTED = False # bool
if skos.WIN:
  try:
    # http://sakuradite.com/topic/639
    # This might not work on Windows 10
    from comtypes.gen.Accessibility import IAccessible
    SUPPORTED = True
  #except ImportError, e:
  except Exception, e:
    derror(e)

if not SUPPORTED:
  def textat(x, y): pass # not supported

else:

  import ctypes
  from ctypes import oledll, byref, POINTER
  from ctypes.wintypes import POINT
  #from comtypes import COMError
  from comtypes.automation import VARIANT
  from comtypes.gen.Accessibility import IAccessible
  #import win32api, win32con, win32gui

  # create wrapper for the oleacc.dll type library
  #from comtypes.client import GetModule
  #GetModule("oleacc.dll")

  def AccessibleObjectFromPoint(x, y):
    """Return an accessible object and an index. See MSDN for details.
    @param  x  int  global pos
    @param  y  int  global pos
    @return  dict, int
    """
    pacc = POINTER(IAccessible)()
    var = VARIANT()
    oledll.oleacc.AccessibleObjectFromPoint(POINT(x, y), byref(pacc), byref(var))
    return pacc, var

  def textat(x, y):
    """
    @param  x  int
    @param  y  int
    @return  unicode or None not str
    """
    try:
      pacc, index = AccessibleObjectFromPoint(x, y)
      return pacc.accName[index]
    #except (WindowsError, comtypes.COMError), e:
    except Exception, e: dwarn(e)

if __name__ == "__main__":
  import sys, time
  import win32api
  while True:
    time.sleep(1)
    x, y = win32api.GetCursorPos()
    name = textat(x,y)
    if name is not None:
      print "===", (x, y), "==="
      print type(name), name.encode(sys.stdout.encoding, "backslashreplace")
    #hwnd = windowat(x, y)
    #if hwnd:
    #  t = windowtext(hwnd)
    #  if t:
    #    t = t.decode('sjis')
    #    try: print type(t), t.encode(sys.stdout.encoding, "backslashreplace")
    #    except Exception, e: print e

# EOF

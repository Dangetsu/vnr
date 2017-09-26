# coding: utf8
# winutil.py
# 10/15/2012 jichi
# Windows only

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

import os
from sakurakit import skos, skwin
from sakurakit.skdebug import dwarn
if skos.WIN:
  import win32gui
  from pywinutil import WinUtil

## Path ##

def to_long_path(path):
  """
  @param  path  unicode
  @return  unicode not None
  """
  return WinUtil.toLongPath(path)

def to_short_path(path):
  """
  @param  path  unicode
  @return  unicode not None
  """
  return WinUtil.toShortPath(path)

## Window ##

def raise_window(hwnd):
  if skos.WIN:
    skwin.set_top_window(hwnd)

def raise_widget(w):
  if skos.WIN:
    hwnd = skwin.hwnd_from_wid(w.winId())
    skwin.set_top_window(hwnd)
    #skwin.set_foreground_window(hwnd) # This will cause game to lose focus!

def set_foreground_window(hwnd):
  if skos.WIN:
    skwin.set_foreground_window(hwnd)

def set_foreground_widget(w):
  if skos.WIN:
    hwnd = skwin.hwnd_from_wid(w.winId())
    skwin.set_foreground_window(hwnd)

def resolve_link(path):
  """
  @param  path  unicode
  @return  unicode not None
  """
  ret = WinUtil.resolveLink(path)
  if not ret or not os.path.exists(ret):
    import growl
    from mytr import my
    msg = my.tr("Shortcut target does not exist")
    if path:
      msg += ":<br/>" + ret
    growl.error(msg)
  return ret

def is_good_window(wid):
  #if not skwin.window_has_title(wid)
  #  return False
  if skwin.is_window_minimized(wid):
    return True
  if not skwin.is_window_visible(wid):
    return False
  w, h = skwin.get_window_size(wid)
  return w >= 300 and h >= 200 # minimum windows size

def get_process_good_window(pid):
  """
  @param  pid long
  @return  long
  """
  def proc(wid, lp):
    if (not lp[1] and
        lp[0] == skwin.get_window_process_id(wid) and
        is_good_window(wid)):
      lp[1] = wid
      #return False
  try:
    lp = [pid, 0]
    win32gui.EnumWindows(proc, lp)
    wid = lp[1]
    return wid
  except Exception, e:
    dwarn(e)
    return 0

# EOF

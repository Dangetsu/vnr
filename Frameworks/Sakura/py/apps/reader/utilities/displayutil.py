# coding: utf8
# displayutil.py
# 10/15/2012 jichi
# Windows only

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

import sys
from sakurakit import skos, skwin
from sakurakit.skdebug import dwarn, dprint
if skos.WIN:
  import win32con, win32gui

# Stretch window

__aspects = None
def __get_aspects():
  global __aspects
  if not __aspects:
    W = xrange(2, 20, 2)
    H = 3, 5, 7, 9
    __aspects = [w/float(h) for w in W for h in H if w >= h]
  return __aspects

def __find_content_aspect(aspect):
  """
  @param  float aspect
  @return  aspect
  """
  return min(__get_aspects(),
      key=lambda it: abs(it-aspect))

def _find_content_size(w, h):
  """
  @param  w
  @param  h
  @return  int w, int h
  """
  # http://msdn.microsoft.com/en-us/library/windows/desktop/ms632600%28v=vs.85%29.aspx
  #w -= _BORDER_WIDTH + _BORDER_WIDTH
  #h -= _BORDER_WIDTH + _TITLEBAR_HEIGHT
  aspect = w / float(h)
  aspect1 = __find_content_aspect(aspect)
  if aspect > aspect1:
    return int(h*aspect1), h
  elif aspect < aspect1:
    return w, int(w/aspect1)
  else: # This seldom happens
    return w, h

_TITLEBAR_HEIGHT = 25

def _set_border_visible(hwnd, v):
  """
  @param  hwnd
  """
  STYLE_REMOVE = win32con.WS_OVERLAPPEDWINDOW
  EXSTYLE_REMOVE = win32con.WS_EX_OVERLAPPEDWINDOW
  try:
    if not v: # always remove thick border
      style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
      if style & EXSTYLE_REMOVE:
        style &= ~EXSTYLE_REMOVE
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, style)

    # http://www.asmcommunity.net/forums/topic/gdi-and-window-resize/
    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style = style|STYLE_REMOVE if v else style&~STYLE_REMOVE
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

    win32gui.SetWindowPos(hwnd, 0, 0, 0, 0, 0, win32con.SWP_FRAMECHANGED|win32con.SWP_NOSIZE|win32con.SWP_NOMOVE|win32con.SWP_NOZORDER|win32con.SWP_NOACTIVATE)
  except Exception, e: dwarn(e)

def stretch_window(hwnd, t=True, size=None, menu=None):
  """
  @param  hwnd  long
  @param  t  bool
  @param  size  (int w, int h) or None
  @param  menu  HMENU or None
  @return  bool
  """
  try:
    _set_border_visible(hwnd, not t)

    w0, h0 = skwin.get_screen_size()
    if not t: # restore
      w1, h1 = size or skwin.get_window_size(hwnd)
      x = (w0 - w1) / 2
      y = (h0 - h1) / 2
      win32gui.SetWindowPos(hwnd, 0, x, y, w1, h1, win32con.SWP_FRAMECHANGED)
      if menu:
        skwin.set_window_menu(hwnd, menu) # Restore menu bar
    else: # stretch
      w1, h1 = skwin.get_content_size(hwnd) or size
      h1 -= _TITLEBAR_HEIGHT # guessed menubar height
      w1, h1 = _find_content_size(w1, h1)
      w, h = w0, h0
      overwidth = w0 * h1
      overheight = w1 * h0
      if overwidth > overheight:
        w = h0 * w1 / h1
      elif overwidth < overheight:
        h = w0 * h1 / w1
      x = (w0 - w) / 2
      y = (h0 - h) / 2

      if skwin.get_window_menu(hwnd):
        skwin.set_window_menu(hwnd, None) # Remove menu bar

      win32gui.SetWindowPos(hwnd, 0,
          x, y, #x - _LEFT_MARGIN, y - _TOP_MARGIN,
          w, h, #w + _LEFT_MARGIN + _RIGHT_MARGIN, h + _TOP_MARGIN + _BOTOM_MARGIN,
          win32con.SWP_FRAMECHANGED)
    return True

  except Exception, e:
    dwarn(e)
  return False

__resolutions = None # cached, [(w, h)]
def __get_resolutions():
  global __resolutions
  if not __resolutions:
    __resolutions = skwin.get_display_resolutions()
    dprint("supported resolutions =", __resolutions)
  return __resolutions

__aspect_resolutions = None # cached, [(w, h)]
def __get_aspect_resolutions():
  global __aspect_resolutions
  if not __aspect_resolutions:
    import sysinfo
    w0, h0 = sysinfo.DISPLAY_RESOLUTION
    dprint("original resolution =", (w0, h0))
    __aspect_resolutions = [(w,h) for w,h in __get_resolutions() if w*h0 == w0*h]
    dprint("aspect resolutions =", __aspect_resolutions)
  return __aspect_resolutions

def __resolution_distance(display, window):
  """
  @param  window  (int w, int h)
  @param  display  (int w, int h)
  @return  int
  """
  w0, h0 = display
  w1, h1 = window
  dw = w1 - w0
  dh = h1 - h0
  return sys.maxint if dw > 25 or dh > 25 else dw * dw + dh * dh

def _find_resolution(size, aspect=False):
  """
  @param  size  (int w, int h)
  @param* aspect  bool
  @return  (int w, int h) not None
  """
  dprint("window size =", size)
  l = __get_aspect_resolutions() if aspect else __get_resolutions()
  ret  = min(l, key=lambda it: __resolution_distance(it, size))
  dprint("ret =", ret)
  return ret

def stretch_display(hwnd, t=True, size=None, resolution=None, aspect=False):
  """
  @param  hwnd  long
  @param  t  bool
  @param  aspect  bool  whether keep aspect ratio
  @param  resolution  (int w, int h) or None
  @param  size  (int w, int h) or None
  @return  bool
  """
  try:
    _set_border_visible(hwnd, not t)

    w0, h0 = skwin.get_window_size(hwnd)

    #if t: # stretch
    #  if skwin.get_window_menu(hwnd):
    #    skwin.set_window_menu(hwnd, None) # Remove menu bar
    #else:
    #  if menu:
    #    skwin.set_window_menu(hwnd, menu) # Restore menu bar
    #    #h0 -= _TITLEBAR_HEIGHT

    if t: # stretch
      w, h = skwin.get_content_size(hwnd) or (w0, h0)
      resolution = _find_resolution((w, h - _TITLEBAR_HEIGHT), aspect=aspect) # Always reduce title bar
    else:
      w, h = w0, h0
    if resolution:
      #if resolution != skwin.get_display_resolution():
      skwin.set_display_resolution(resolution)
    else:
      resolution = skwin.get_display_resolution()
    w1, h1 = resolution
    x = max(0, (w1 - w0)/2)
    y = max(-30, (h1 - h0)/2) # can be negative (usually -21)
    if not t and size: # restore
      w, h = size
    win32gui.SetWindowPos(hwnd, 0, x, y, w, h, win32con.SWP_FRAMECHANGED)
    return True

  except Exception, e:
    dwarn(e)
  return False

if __name__ == '__main__':
  # http://www.news2news.com/vfp/?example=374&ver=vcpp
  # http://sourceforge.net/p/pywin32/bugs/480/
  import sys
  for w,h in skwin.get_display_resolutions():
    if w/float(h) == 1.6:
      print w,h
  print skwin.test_display_resolution((1440, 900))
  print skwin.test_display_resolution((1280, 800))
  #print skwin.set_display_resolution((1280, 800))
  #print skwin.set_display_resolution((1440, 900))
  sys.exit(0)

# EOF

# coding: utf8
# skclip.py
# 11/9/2013 jichi
#
# Not thread-safe!
# May raise on type error
#
# See: http://coffeeghost.net/2010/10/09/pyperclip-a-cross-platform-clipboard-module-for-python/
# See: http://coffeeghost.net/src/pyperclip.py

if __name__ == '__main__':
  import sys
  sys.path.append('..')

from Qt5.QtWidgets import QApplication
from skdebug import dwarn

def getpixmap(v):
  """
  @return  QPixmap
  """
  return QApplication.clipboard().pixmap()

def setpixmap(v):
  """
  @param  v  QPixmap
  """
  QApplication.clipboard().setPixmap(v)

def getimage(v):
  """
  @return  QImage
  """
  return QApplication.clipboard().image()

def setimage(v):
  """
  @param  v  QImage
  """
  QApplication.clipboard().setImage(v)

def gettext():
  """Not reliable when the clipboard is busy
  @return  unicode
  """
  return QApplication.clipboard().text()

import skos
if skos.WIN:
  import win32clipboard

  #def settext(v):
  #  """Not reliable when the clipboard is busy
  #  @param  v  unicode
  #  """
  #  try:
  #    win32clipboard.OpenClipboard()
  #    try:
  #      win32clipboard.EmptyClipboard()
  #      win32clipboard.SetClipboardText(v)
  #    except Exception, e: dwarn(e)
  #    win32clipboard.CloseClipboard()
  #  except Exception, e: dwarn(e)

  import ctypes
  import win32con
  import skwinapi
  from sakurakit import msvcrt # so that it does not conflicts with msvcrt

  # See: http://coffeeghost.net/2010/10/09/pyperclip-a-cross-platform-clipboard-module-for-python/
  def settext(text):
    """
    @param  text  unicode or str
    @return  bool
    """
    # FIXME: Need to set clipboard format to UTF8
    #text = text.encode('sjis', errors='ignore')
    u16 = isinstance(text, unicode)
    ret = True
    if skwinapi.OpenClipboard(0): # hwnd = 0
      if skwinapi.EmptyClipboard(): # clipboard must be emptied first
        size = len(text)
        size1 = size + 1
        if u16:
          size *= 2
          size1 *= 2
        data = text if u16 else text
        hCd = skwinapi.GlobalAlloc(win32con.GMEM_DDESHARE|win32con.GMEM_ZEROINIT, size1)
        pchData = skwinapi.GlobalLock(hCd)
        if pchData:
          #msvcrt.strcpy(ctypes.c_char_p(pchData), bytes(data))
          msvcrt.memcpy(pchData, data, size)
          # http://www.codeexperts.com/showthread.php?1420-crash-while-writing-unicode-data-to-clipboard-using-SetClipboardData
          skwinapi.GlobalUnlock(hCd)
          fmt = win32con.CF_UNICODETEXT if u16 else win32con.CF_TEXT
          ret = bool(skwinapi.SetClipboardData(fmt, hCd))
      skwinapi.CloseClipboard()
    if not ret:
      dwarn("clipboard busy")
    return ret

else: # unix
  def settext(v):
    """Not reliable when the clipboard is busy
    @param  v  unicode
    """
    QApplication.clipboard().setText(v)

if __name__ == '__main__':
  #settext("hello")
  #settext(u"hello")
  settext(u"なにこれ")
  settext(u"简体中文")

# EOF

# See: http://coffeeghost.net/2010/10/09/pyperclip-a-cross-platform-clipboard-module-for-python/
#def gettext():
#  """
#  @return  str not unicode
#  """
#  try:
#    ctypes.windll.user32.OpenClipboard(0)
#    pcontents = ctypes.windll.user32.GetClipboardData(1) # 1 is CF_TEXT
#    data = ctypes.c_char_p(pcontents).value
#    #ctypes.windll.kernel32.GlobalUnlock(pcontents)
#    ctypes.windll.user32.CloseClipboard()
#    return data
#  except Exception, e:
#    dwarn(e)
#    return ''


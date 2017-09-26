# coding: utf8
# apps.py
# 11/10/2013 jichi
#
# See:
# http://white-azalea.hatenablog.jp/entry/20130116/1358348450
# https://github.com/Sunao-Yoshii/VoiceroidAccessor
# http://www.white-azalea.net/VoiceroidRunner.zip

if __name__ == '__main__':
  import sys
  sys.path.append('..')

from sakurakit import skclip, skevents, skos
from sakurakit.skdebug import dprint, dwarn
from bottle import Voiceroid
if skos.WIN:
  from sakurakit import skwin

## .NET ##

class MonoVoiceroid(Voiceroid):
  key = 'mono' # override
  name = u"MonoVoiceroid" # override

# See: https://github.com/Sunao-Yoshii/VoiceroidAccessor/blob/master/Zunko/Zunko.cs
class Zunko(MonoVoiceroid):
  key = 'zunko' # override
  name = u"東北ずん子" # override
  version = '1.6' # override

  MSG_CLICK = 245 # override, win32con.BM_CLICK
  MIN_WINDOW_COUNT = 8 # normal window count is 8

  def getWindow(self):
    """@reimp"""
    wids = skwin.get_process_windows(self.pid)
    if wids and len(wids) >= self.MIN_WINDOW_COUNT:
      for wid in wids:
        c = skwin.get_window_class(wid)
        if c and c.startswith('WindowsForms10.Window'): # WindowsForms10.Window.8.app.0.17ad52b
          return wid
    return 0

  def getTextEdit(self):
    """@reimp"""
    parent = self.wid
    if parent:
      wids = skwin.get_window_children(parent)
      if wids:
        for wid in wids:
          c = skwin.get_window_class(wid)
          if c and c.startswith('WindowsForms10.RichEdit'):
            return wid
    return 0

  def _findButton(self, text):
    """
    @param  text  unicode
    @param* reverse  bool
    @return  long
    """
    parent = self.wid
    if parent:
      wids = skwin.get_window_children(parent)
      if wids:
        for wid in wids:
          c = skwin.get_window_class(wid)
          if c and c.startswith('WindowsForms10.BUTTON'):
            t = skwin.get_window_text(wid)
            if t == text:
              return wid
    return 0

  def getPlayButton(self):
    """@reimp"""
    return self._findButton(u" 再生")

  def getStopButton(self):
    """@reimp"""
    return self._findButton(u" 停止")

  def stop(self, sleep=True):
    """@reimp"""
    ret = super(Zunko, self).stop()
    if ret and sleep:
      skevents.sleep(100) # reduce the chance that it might crash
      #import time
      #time.sleep(1)
    return ret

  #def isBusy(self):
  #  """@reimp"""
  #  return bool(self._findButton(u" 一時停止"))

## TCL/TK ##

# See: https://github.com/Sunao-Yoshii/VoiceroidAccessor/blob/master/Yukari/Yukari.cs
# See: http://d.hatena.ne.jp/kougaku-navi/20111202/p1
class TkVoiceroid(Voiceroid):
  key = 'tk' # override
  name = u"TkVoiceroid" # override

  MSG_CLICK = 0 # override

  # 民安ともえ
  CMD_TCL_MENU = 1 # show TCL menu
  CMD_TCL_SOURCE = 4 # select TCL source code
  CMD_TCL_KILL = 7 # close the application
  CMD_TCL_ABOUT = 13 # show TCL version

  CMD_SAVE = 35
  CMD_QUIT = 41

  CMD_DELLINE = 45
  CMD_UNDO = 46
  CMD_CUT = 52
  CMD_PASTE = 56
  CMD_SELECTALL = 60

  def setText(self, v): # blocked
    """@reimp"""
    hwnd = self.wid
    if hwnd:
      if skwin.send_window_command(hwnd, self.CMD_SELECTALL):
        if skwin.send_window_command(hwnd, self.CMD_CUT):
          skclip.settext(v)
          #if sleep:
          #  skevents.sleep(200) # wait until the clipboard is ready
          if skwin.send_window_command(hwnd, self.CMD_PASTE):
            return True
    return False

  TEXTEDIT = 1 # class=TkChild
  BUTTON_PLAY = 9 # class=BUTTON, 再生
  BUTTON_STOP = 8 # class=BUTTON, 停止
  BUTTON_SAVE = 7 # class=BUTTON, 保存
  BUTTON_CHOUSEI = 6 # class=BUTTON, フレーズ調整
  BUTTON_TOUROKU = 5 # class=BUTTON, 単語登録
  SCROLLBAR = 11 # class=ScrollBar
  def _findWindow(self, index):
    """
    @param  text  unicode
    @return  long
    """
    parent = self.wid
    if parent:
      wids = skwin.get_window_children(parent)
      if len(wids) > index:
        return wids[index]
    return 0

  MIN_WINDOW_COUNT = 20 # startup: 6, normal: 23
  def getWindow(self):
    """@reimp"""
    wids = skwin.get_process_windows(self.pid)
    if wids and len(wids) >= self.MIN_WINDOW_COUNT:
      for wid in wids:
        c = skwin.get_window_class(wid)
        if c == 'TkTopLevel': # WindowsForms10.Window.8.app.0.17ad52b
          t = skwin.get_window_text(wid)
          if t.startswith('VOICEROID'):
            return wid
    return 0

  def getTextEdit(self):
    """@reimp  unused"""
    return self._findWindow(self.TEXTEDIT)

  def getPlayButton(self):
    """@reimp"""
    return self._findWindow(self.BUTTON_PLAY)

  def getStopButton(self):
    """@reimp"""
    return self._findWindow(self.BUTTON_STOP)

class Yukari(TkVoiceroid):
  key = 'yukari' # override
  name = u"結月ゆかり" # override
  version = '1.5' # override

  CMD_PREFS_PITCH = 63
  CMD_PREFS_DELAY = 65
  CMD_HELP = 70
  CMD_ABOUT = 73

# FIXME: Broken
# Missing TCL command to paste/undo
class Tamiyasu(TkVoiceroid):
  key = 'tamiyasu' # override
  name = u"民安ともえ" # override
  version = '1.5' # override

  CMD_VOLUMN = 59
  CMD_PITCH = 61
  CMD_HELP = 74
  CMD_ABOUT = 77
  CMD_PLINFO_MENU = 79
  CMD_PLINFO_OPEN = 83
  CMD_PLAY = 95
  CMD_WAV_OPEN = 99

  def play(self): # async
    """@reimp"""
    hwnd = self.wid
    return bool(hwnd) and skwin.post_window_command(hwnd, self.CMD_PLAY)

# 放流されません
#class Ai(TkVoiceroid):
#  key = 'ai' # override
#  name = u"月読アイ" # override

if __name__ == '__main__':
  import sys
  from PySide.QtGui import QApplication
  a = QApplication(sys.argv)

  from bottle import VoiceroidController

  #path = r'S:\Applications\AHS\VOICEROID+\zunko\VOICEROID.exe'
  #path = r'C:\Program Files\AHS\VOICEROID+\zunko\VOICEROID.exe'
  #v = VoiceroidController(Zunko(), path=path)

  path = r'S:\Applications\AHS\VOICEROID+\yukari\VOICEROID.exe'
  v = VoiceroidController(Yukari(), path=path)

  #path = r'S:\Applications\AHS\VOICEROID+\tamiyasu\VOICEROID.exe'
  #path = r'C:\Program Files\AHS\VOICEROID+\yukari\VOICEROID.exe'
  #v = VoiceroidController(Tamiyasu(), path=path)

  v.run()
  #if v.isActive():
  print "active"
  #print v.voiceroid.play()
  print v.stop()
  print v.speak(u"なにかあった")

# EOF

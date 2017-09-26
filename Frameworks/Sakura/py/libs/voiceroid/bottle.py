# coding: utf8
# bottle.py
# 11/10/2013 jichi
#
# See:
# http://white-azalea.hatenablog.jp/entry/20130116/1358348450
# https://github.com/Sunao-Yoshii/VoiceroidAccessor
# http://www.white-azalea.net/VoiceroidRunner.zip

if __name__ == '__main__':
  import sys
  sys.path.append('..')

import os
from sakurakit import skevents, skos
from sakurakit.skdebug import dwarn
from winbottle.procbottle import ProcessBottle
if skos.WIN:
  from sakurakit import skwin

class VoiceroidController(ProcessBottle):
  LCID = 0x0411 # long

  def __init__(self, voiceroid=None, parent=None, pid=0, path=""):
    """
    @param  parent  QObject
    @param  pid  long
    @param  path  unicode
    @param  voiceroid  Voiceroid
    """
    if not path and voiceroid:
      path = voiceroid.getPath()
    super(VoiceroidController, self).__init__(parent=parent, pid=pid, path=path)
    self.voiceroid = voiceroid
    self.pidChanged.connect(voiceroid.setPid)

  def run(self):
    """@reimp"""
    super(VoiceroidController, self).run()
    if self.isActive():
      self.minimize()
      if not self.isMimimized():
        skevents.runlater(self.minimize, 1000)

  def createProcess(self):
    """@reimp"""
    if skos.WIN:
      from apploc import applocale
      if applocale.exists():
        return applocale.create_process(self.path, lcid=self.LCID)
    return super(VoiceroidController, self).createProcess()

  @property
  def wid(self):
    try: return self.voiceroid.wid
    except Exception, e:
      dwarn(e)
      return 0

  def minimize(self):
    hwnd = self.wid
    if hwnd:
      skwin.minimize_window(hwnd)

  def isMimimized(self):
    """
    @return  bool
    """
    hwnd = self.wid
    return bool(hwnd) and skwin.is_window_minimized(hwnd)

  def speak(self, text):
    """
    @param  text  unicode
    """
    try:
      v = self.voiceroid
      #if v.isBusy():
      #  dwarn("busy")
      #  ok = True
      #else:
      ok = v.setText(text)
      if ok:
        if text:
          ok = v.play()
        else:
          ok = v.stop()
    except Exception, e:
      dwarn(e)
      ok = False
    if not ok:
      self.restart()
    return ok

  def stop(self):
    try: ok = self.voiceroid.stop()
    except Exception, e:
      dwarn(e)
      ok = False
    if not ok:
      self.restart()
    return ok

class Voiceroid(object):
  key = 'voiceroid'
  name = u'VOICEROID+' # unicode
  version = '1.0' # str

  MSG_CLICK = 245 # win32con.BM_CLICK

  def __init__(self):
    self.pid = 0 # long
    self.clearCache()

  def clearCache(self):
    """Reset cached windows"""
    self._window = 0 # hwnd
    self._playButton = 0 # hwnd
    self._stopButton = 0 # hwnd
    self._textEdit = 0 # hwnd

  # Registry

  def _getRegistryPath(self):
    """
    @return  unicode or None
    """
    regpath = r"SOFTWARE\AHS\VOICEROID\%s\%s" % (self.version, self.key)
    regkey = 'InstallDir'
    import _winreg
    hk = _winreg.HKEY_LOCAL_MACHINE
    try:
      with _winreg.ConnectRegistry(None, hk) as reg: # computer_name = None
        with _winreg.OpenKey(reg, regpath) as key:
          path = _winreg.QueryValueEx(key, regkey)[0]
          if path:
            return path
    except (WindowsError, TypeError, AttributeError): pass

  def _getEnvironmentPath(self):
    """
    @return  unicode
    """
    from sakurakit import skpaths
    pf = skpaths.PROGRAMFILES
    path = r'AHS\VOICEROID+\%s' % self.name
    return os.path.join(pf, path)

  def getPath(self):
    """
    @return  unicode not None
    """
    for path in self._getRegistryPath(), self._getEnvironmentPath():
      if path:
        path = os.path.join(path, 'VOICEROID.exe')
        if os.path.exists(path):
          return path
    return ''

  # Interface

  #def isBusy(self):
  #  """Whether is reading
  #  @return  bool
  #  """
  #  return False

  #def debug(self, *args, **kwargs): pass

  def getWindow(self):
    """
    @return  HWND
    @raise
    """
    return 0

  def getPlayButton(self):
    """
    @return  HWND
    @raise
    """
    return 0

  def getStopButton(self):
    """
    @return  HWND
    @raise
    """
    return 0

  def getTextEdit(self):
    """
    @return  HWND
    @raise
    """
    return 0

  # Properties

  def setPid(self, v):
    """
    @param  v  ulong
    """
    if self.pid != v:
      self.pid = v
      self.clearCache()

  @property
  def window(self):
    """
    @return  HWND
    @raise
    """
    if not self._window:
      self._window = self.getWindow()
    return self._window

  wid = window # aliased

  @property
  def playButton(self):
    """
    @return  HWND
    @raise
    """
    if not self._playButton:
      self._playButton = self.getPlayButton()
    return self._playButton

  @property
  def stopButton(self):
    """
    @return  HWND
    @raise
    """
    if not self._stopButton:
      self._stopButton = self.getStopButton()
    return self._stopButton

  @property
  def textEdit(self):
    """
    @return  HWND
    @raise
    """
    if not self._textEdit:
      self._textEdit = self.getTextEdit()
    return self._textEdit

  # Actions

  def play(self):
    """Non-blocked (post). Read the current text.
    @raise
    """
    hwnd = self.playButton
    return bool(hwnd) and skwin.post_window_message(hwnd, self.MSG_CLICK)

  def stop(self): # blocked
    """Blocked (send). Play the current text
    @raise
    """
    hwnd = self.stopButton
    return bool(hwnd) and 0 == skwin.send_window_message(hwnd, self.MSG_CLICK)

  #def text(self):
  #  """Get the current text to read
  #  @param  v  unicode
  #  @raise
  #  """
  #  hwnd = self.textEdit
  #  return skwin.get_window_text(hwnd) if hwnd else ''

  def setText(self, v):
    """Blocked (send). Play the current text
    @param  v  unicode
    @raise
    """
    hwnd = self.textEdit
    return bool(hwnd) and skwin.set_window_text(hwnd, v)

# EOF

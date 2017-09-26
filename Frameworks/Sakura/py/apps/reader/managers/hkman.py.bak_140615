# coding: utf8
# hkman.py
# 1/29/2014 jichi

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

from functools import partial
from PySide.QtCore import Qt, Signal, Property, QObject, QThread
from sakurakit import skos
from sakurakit.skdebug import dprint
from sakurakit.skclass import Q_Q, memoized, memoizedproperty
#from sakurakit.skqml import QmlObject
import settings

if not skos.WIN:
  class dummy_pyhk:
    def addHotkey(self, *args, **kwargs): pass
    def removeHotkey(self, *args, **kwargs): pass

HOTKEY_DELIM = '\n'
def packhotkey(l): # list -> str
  return HOTKEY_DELIM.join(l)
def unpackhotkey(s): # str -> list
  if isinstance(s, unicode):
    s = s.encode('utf8', errors='ignore')
  return s.split(HOTKEY_DELIM)
  #l = s.split(HOTKEY_DELIM)
  #return [it.encode('utf8', errors='ignore') for it in l]

@memoized
def manager(): return HotkeyManager()

class HotkeyManager(QObject):

  def __init__(self, parent=None):
    super(HotkeyManager, self).__init__(parent)
    self.__d = _HotkeyManager()

  enabledChanged = Signal(bool)
  def isEnabled(self): return self.__d.enabled
  def setEnabled(self, t):
    d = self.__d
    if d.enabled != t:
      dprint("t = %s" % t)
      d.enabled = t
      if t:
        d.start()
      else:
        d.stop()
      self.enabledChanged.emit(t)

  #def setTtsEnabled(self, t):
  #  self.__d.setMappingEnabled('tts', t)
  #  settings.global_().setTtsHotkeyEnabled(t)

  #def setTtsHotkey(self, k):
  #  self.__d.setMappingKey('tts', k)
  #  settings.global_().setTtsHotkey(k)

class _HotkeyManager(object):
  def __init__(self):
    self.enabled = False # bool
    self._pyhk = None # pyhk instance

    ss = settings.global_()

    # key mapping
    self._mapping = {
      'tts': { # string task name
        'do': self._onTts, # function
        'on': ss.isTtsHotkeyEnabled(), # bool
        'key': ss.ttsHotkey(), # string
      }
    }

    ss.ttsHotkeyEnabledChanged.connect(partial(self.setMappingEnabled, 'tts'))
    ss.ttsHotkeyChanged.connect(partial(self.setMappingKey, 'tts'))

    #from PySide import QtCore
    #qApp = QtCore.QCoreApplication.instance()
    #qApp.aboutToQuit.connect(self.stop)

  @memoizedproperty
  def thread(self):
    ret = HotkeyThread()
    ret.hotkeyReceived.connect(self._onHotkey, Qt.QueuedConnection) # delay processing hotkeys to the next event loop
    #ret.start()
    #ret.start(QThread.LowPriority)
    ret.start(QThread.TimeCriticalPriority) # schedule more often to prevent blocking mouse
    return ret

  def start(self):
    for hk in self._mapping.itervalues():
      if hk['on'] and hk['key']:
        self._addHotkey(hk['key'])

  def stop(self):
    for hk in self._mapping.itervalues():
      if hk['on'] and hk['key']:
        self._removeHotkey(hk['key'])

  def setMappingEnabled(self, name, t):
    m = self._mapping[name]
    if m['on'] != t:
      m['on'] = t
      k = m['key']
      if k:
        self._toggleHotkey(k, t)

  def setMappingKey(self, name, k):
    m = self._mapping[name]
    oldk = m['key']
    if oldk != k:
      m['key'] = k
      if oldk:
        self._removeHotkey(oldk)
      if k:
        self._addHotkey(k)

  def _addHotkey(self, k):
    self.thread.addHotkey(k)
    #l = unpackhotkey(k)
    #self.pyhk.addHotkey(l, partial(self._emitHotkey, k))

  def _removeHotkey(self, k): # str
    self.thread.removeHotkey(k)
    #l = unpackhotkey(k)
    #self.pyhk.removeHotkey(l)

  def _toggleHotkey(self, k, t):
    if t:
      self._addHotkey(k)
    else:
      self._removeHotkey(k)

  #@memoizedproperty
  #def pyhk(self): # pyhk instance
  #  if skos.WIN:
  #    from pyhk import pyhk
  #    return pyhk()
  #  else:
  #    return dummy_pyhk()

  def _onHotkey(self, key): # callback
    for name, hk in self._mapping.iteritems():
      if hk['key'] == key and hk['on']:
        apply(hk['do'])

  @staticmethod
  def _onTts():
    import textman
    textman.manager().speakCurrentText()
    dprint("pass")

#@QmlObject
class HotkeyManagerProxy(QObject):
  def __init__(self, parent=None):
    super(HotkeyManagerProxy, self).__init__(parent)
    manager().enabledChanged.connect(self.enabledChanged)

  enabledChanged = Signal(bool)
  enabled = Property(bool,
      lambda self: manager().isEnabled(),
      lambda self, v: manager().setEnabled(v),
      notify=enabledChanged)

# Threading

class HotkeyThread(QThread):
  def __init__(self, parent=None):
    super(HotkeyThread, self).__init__(parent)
    d = self.__d = _HotkeyThread(self)

    self.hotkeyAdded.connect(d.addHotkey, Qt.QueuedConnection)
    self.hotkeyRemoved.connect(d.removeHotkey, Qt.QueuedConnection)

  def addHotkey(self, k): # str ->
    self.hotkeyAdded.emit(k)

  def removeHotkey(self, k): # str ->
    self.hotkeyRemoved.emit(k)

  #def stop(self):
  #  self.quit()
  #  #self.__d.stop()

  hotkeyReceived = Signal(str)

  # Private signals
  hotkeyAdded = Signal(str)
  hotkeyRemoved = Signal(str)

@Q_Q
class _HotkeyThread(object):

  def addHotkey(self, k): # str ->
    l = unpackhotkey(k)
    self.pyhk.addHotkey(l, partial(self._emitHotkey, k))

  def removeHotkey(self, k): # str ->
    l = unpackhotkey(k)
    self.pyhk.removeHotkey(l)

  def _emitHotkey(self, k):
    self.q.hotkeyReceived.emit(k)

  @memoizedproperty
  def pyhk(self): # pyhk instance
    if skos.WIN:
      from pyhk import pyhk
      return pyhk()
    else:
      return dummy_pyhk()

# Debug entry
if __name__ == '__main__': #and os.name == 'nt':
  # http://schurpf.com/python/python-hotkey-module/
  import pyhk
  def fun_k():
    print "key"
  def fun_m():
    print "mouse"

  #create pyhk class instance
  hot = pyhk.pyhk()
  #add hotkey
  hot.addHotkey(['Ctrl', 'A'],fun_k)
  hot.removeHotkey(['Ctrl', 'A'])

  hot.addHotkey(['mouse right'],fun_m)

  # Start event loop and block the main thread
  #import pythoncom
  #pythoncom.PumpMessages() # wait forever
  a = debug.app()
  a.exec_()

# EOF

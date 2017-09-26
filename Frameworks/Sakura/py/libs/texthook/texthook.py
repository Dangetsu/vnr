# coding: utf8
# texthook.py
# 10/6/2012 jichi
# Windows only
# See: http://stackoverflow.com/questions/5253854/python-import-dll

__all__ = 'TextHook',

#from ctypes import c_longlong
from PySide.QtCore import Signal, QObject, Qt
from sakurakit import skos
from sakurakit.skclass import Q_Q, memoized
from sakurakit.skdebug import dprint, dwarn

ENABLE_GAMEENGINE = True

if skos.WIN:
  import pytexthook
  #from numpy import * # for int types

  _REPEAT_CAPACITY_FACTOR = 2 # increase capacity when repeat is enabled

  @Q_Q
  class _TextHook(pytexthook.TextHook):
    def __init__(self, q):
      super(_TextHook, self).__init__(q)
      # Default is 200. This value is CRITICAL!
      self.setInterval(300)

      # Queued connection is critical!
      # Although the text thread share the same threadID,
      # it is on a different eventloop hacked by wintimer

      self.pid = 0
      self.hijacked = False # bool
      self.hcode = ''     # str hook code
      self.hooks = {}     # {str name:str code}
      self.encoding = 'shift-jis'
      #self.signature = 0   # thread signature for user-defined hook

      self.dataReceived.connect(self._emitdataReceived, Qt.QueuedConnection)

    def _emitdataReceived(self, rawData, renderedData, signature, source):
      raw = rawData.data()
      rendered = raw if renderedData.isEmpty() else renderedData.data()
      self.q.dataReceived.emit(raw, rendered, signature, source)

    @staticmethod
    def pruneHookCode(hcode):
      """
      @param  hcode  str
      @return  str or None  Extract the first parameter as the hook code
      """
      try:
        h = filter(bool, hcode.split())
        if len(h) == 1:
          return h[0]
        if '.' not in h[0] and '.' in h[1] and h[1][0] != '/':
          return ' '.join(h[:2])
        return h[0]
      except: pass

  # Should be singleton
  class TextHook(QObject):
    """Text hook proxy
    This is a thin wrapper to reduce influence from future changes of pytexthook
    """
    def __init__(self, parent=None):
      super(TextHook, self).__init__(parent)
      self.__d = _TextHook(self)
      dprint("pass")

    ## Signals ##

    dataReceived = Signal(bytearray, bytearray, long, unicode) # (raw text, rendered text, signature, source)
    hookCodeChanged = Signal(unicode)
    processAttached = Signal(long) # pid
    processDetached = Signal(long) # pid

    ## Properties ##

    #def interval(self): return self.__d.interval()
    #def setInterval(self, value): self.__d.setInterval(value)

    realDataCapacityChanged = Signal(int)
    def realDataCapacity(self): return self.__d.dataCapacity()
    def setRealDataCapacity(self, v):
      d = self.__d
      if v != d.dataCapacity():
        dprint(v)
        d.setDataCapacity(v)
        self.realDataCapacityChanged.emit(v)

    suggestedDataCapacityChanged = Signal(int)
    def suggestedDataCapacity(self):
      ret = self.realDataCapacity()
      if self.removesRepeat():
        ret /= _REPEAT_CAPACITY_FACTOR
      return ret
    def setSuggestedDataCapacity(self, v):
      if v != self.suggestedDataCapacity():
        dprint(v)
        d = self.__d
        self.setRealDataCapacity(v * _REPEAT_CAPACITY_FACTOR if d.removesRepeat() else v)
        self.suggestedDataCapacityChanged.emit(v)

    removesRepeatChanged = Signal(bool)
    def removesRepeat(self):
      return self.__d.removesRepeat()
    def setRemovesRepeat(self, t):
      d = self.__d
      if t != d.removesRepeat():
        dprint(t)
        d.setRemovesRepeat(t)

        c = self.realDataCapacity()
        self.setRealDataCapacity(c * _REPEAT_CAPACITY_FACTOR if t else c / _REPEAT_CAPACITY_FACTOR)

        self.removesRepeatChanged.emit(t)

    keepsSpaceChanged = Signal(bool)
    def keepsSpace(self):
      return self.__d.keepsSpace()
    def setKeepsSpace(self, t):
      d = self.__d
      if t != d.keepsSpace():
        dprint(t)
        d.setKeepsSpace(t)
        self.keepsSpaceChanged.emit(t)

    encodingChanged = Signal(str)
    def encoding(self):
      return self.__d.encoding
    def setEncoding(self, v):
      d = self.__d
      if v != d.encoding:
        dprint(v)
        d.encoding = v
        d.setWideCharacter(v.lower() == 'utf-16') # consistent with share.yaml
        self.encodingChanged.emit(v)

    def setParentWinId(self, hwnd):
      dprint(hwnd)
      self.__d.setParentWinId(hwnd)
    def parentWinId(self, hwnd): return self.__d.parentWinId(hwnd)

    def isEnabled(self): return self.__d.isEnabled()
    def setEnabled(self, t):
      dprint(t)
      self.__d.setEnabled(t)

    def isWhitelistEnabled(self): return self.__d.isThreadWhitelistEnabled()
    def setWhitelistEnabled(self, t):
      dprint(t)
      self.__d.setThreadWhitelistEnabled(t)

    def keptThreadName(self): return self.__d.keptThreadName()
    def setKeptThreadName(self, v):
      """
      @param  v  str
      len(v) must be smaller than 0x200!
      """
      dprint(v)
      #assert len(v) < 0x200
      self.__d.setKeptThreadName(v)

    def setWhitelist(self, val):
      """
      @param  [int signature]
      """
      self.__d.setThreadWhitelist(val)

    def whitelist(self):
      """
      @return  [int signature]
      """
      return self.__d.threadWhitelist()

    def clearWhitelist(self): self.__d.clearThreadWhitelist();

    ## Status ##

    def isActive(self): return self.__d.isActive()

    def isAttached(self): return bool(self.__d.pid) # -> bool
    def isHijacked(self): return self.hijacked # -> bool

    def currentPid(self):
      """
      @return  long
      """
      return self.__d.pid

    def currentHookCode(self):
      """
      @return  str
      """
      return self.__d.hcode

    def currentHooks(self):
      """
      @return  {str name:str code}
      """
      return self.__d.hooks

    ## Actions ##

    def start(self):
      dprint("pass")
      self.__d.start()
    def stop(self):
      dprint("pass")
      self.__d.stop()

    def attachProcess(self, pid, hijack=True):
      """Return if succeed
      @param  pid  long
      @param* hijack  bool
      @return  bool
      """
      dprint("enter")
      if not pid:
        return False

      d = self.__d
      #d.signature = 0
      if d.pid and d.pid != pid:
        if d.hcode:
          d.hcode = ''
          d.removeHookCode(d.pid)
          d.hooks = {}
        d.detachProcess(d.pid)
        d.hijacked = False
        self.processDetached.emit(d.pid)
        d.pid = 0
      ok = d.attachProcess(pid)
      if ok:
        d.pid = pid
        if hijack:
          self.hijackProcess()
          #import time
          #MAX_RETRIES = 3
          #for i in xrange(MAX_RETRIES):
          #  time.sleep(1.0/MAX_RETRIES) # retry for totally 1 second
          #  if self.hijackProcess():
          #    break
          #  else:
          #    dwarn("hijack failed, retry: %s/%s" % (i + 1, MAX_RETRIES))
        self.processAttached.emit(d.pid)

        if ENABLE_GAMEENGINE:
          dprint("try game engine")
          from gameengine import gameengine
          gameengine.inject(pid)
          #skevents.runlater(partial(
          #    gameengine.inject, g.pid),
          #    3000) # wait for 3 seconds so that the gameengine will not crash the game on the start up (such as BALDR)
      dprint("leave: ret = %s" % ok)
      return ok

    def hijackProcess(self):
      """Return if succeed
      @return  bool
      """
      d = self.__d
      if d.pid and not d.hijacked:
        dprint("enter")
        d.hijacked = d.hijackProcess(d.pid)
        if d.hijacked:
          dprint("leave: ret = true")
        else:
          dwarn("leave: ret = false")
      return bool(d.pid) and d.hijacked

    def detachProcess(self):
      """Return if succeed
      @return  bool
      """
      dprint("enter")
      ret = False
      d = self.__d
      #d.signature = 0
      d.hijacked = False
      if d.pid:
        if d.hcode or d.hooks:
          d.hcode = ''
          d.removeHookCode(d.pid)
          d.hooks = {}
        ret = self.__d.detachProcess(d.pid)
        self.processDetached.emit(d.pid)
        d.pid = 0
      dprint("leave: ret = %s" % ret)
      return ret

    def addHook(self, code, name="", verbose=True):
      """
      @param  code  str
      @param* name  str
      @param* verbose  bool
      @return  bool
      """
      if verbose:
        dprint("enter: name = %s, code = %s" % (name, code))
      else:
        dprint("enter: name = %s" % name)
      d = self.__d
      ok = bool(d.pid) and d.addHookCode(d.pid, code, name, verbose)
      if ok:
        d.hooks[name] = code
      dprint("leave: ret = %s" % ok)
      return ok

    def setHookCode(self, hcode):
      """Return if failed
      @oaram  hcode  ''
      @return  bool
      """
      dprint("enter: hcode = %s" % hcode)
      d = self.__d
      ret = d.hcode == hcode
      if d.pid and d.hcode != hcode:
        if d.hcode:
          #dwarn("ignore previous hook code, as it might hang VNR")
          d.removeHookCode(d.pid)
          d.hcode = ''
          if d.hooks:
            for name, code in d.hooks.iteritems():
              d.addHookCode(d.pid, code, name)
        realcode = _TextHook.pruneHookCode(hcode)
        if realcode:
          realcode = realcode.upper()
          ret = d.addHookCode(d.pid, realcode)
          if ret:
            d.hcode = hcode
            self.hookCodeChanged.emit(hcode)
      dprint("leave: ret = %s" % ret)
      return ret

    @staticmethod
    def verifyHookCode(hcode):
      """
      @param  hcode  unicode
      @return  bool
      """
      return _TextHook.verifyHookCode(hcode.upper())

    def clearHookCode(self):
      d = self.__d
      if d.hcode:
        d.removeHookCode(d.pid)
        d.hcode = ''
        if d.pid and d.hooks:
          for name, code in d.hooks.iteritems():
            d.addHookCode(d.pid, code, name)

else:
  class TextHook(QObject): # dummy
    def __init__(self, parent=None):
      super(TextHook, self).__init__(parent)

    ## Signals ##

    dataReceived = Signal(bytearray, bytearray, long, unicode)
    hookCodeChanged = Signal(unicode)
    processAttached = Signal(long) # pid
    processDetached = Signal(long) # pid

    ## Properties ##

    sugggestedDataCapacityChanged = Signal(int)
    def suggestedDataCapacity(self): return 512
    def setSuggestedDataCapacity(self, value): pass

    realDataCapacityChanged = Signal(int)
    def realDataCapacity(self): return 512
    def setRealDataCapacity(self, value): pass

    removesRepeatChanged = Signal(bool)
    def removesRepeat(self): return False
    def setRemovesRepeat(self, value): pass

    keepsSpaceChanged = Signal(bool)
    def keepsSpace(self): return False
    def setKeepsSpace(self, value): pass

    encodingChanged = Signal(str)
    def encoding(self): return 'shift-jis'
    def setEncoding(self, value): pass

    def setParentWinId(self, hwnd): pass
    def parentWinId(self, hwnd): return 0
    def setEnabled(self, enabled): pass
    def isEnabled(self): return False

    def setWhitelistEnabled(self, enabled): pass
    def isWhitelistEnabled(self): return False

    def setWhitelist(self, enabled): pass
    def whitelist(self): return []
    def clearWhitelist(self): pass

    def setKeptThreadName(self, v): pass
    def keptThreadName(self): return ''

    ## Status ##

    def isActive(self): return False
    def isAttached(self): return False
    def isHijacked(self): return False

    def currentPid(self): return 0
    def currentHookCode(self): return ""
    def currentHooks(self): return {}

    ## Actions ##

    def start(self): pass
    def stop(self): pass

    def attachProcess(self, pid, hijack=True): return False
    def detachProcess(self): return False
    def hijackProcess(self): return False

    def addHook(self, code, name="", verbose=True): return False

    def setHookCode(self, hcode): return False

    @staticmethod
    def verifyHookCode(hcode): return False

    def clearHookCode(self): pass

@memoized
def global_(): return TextHook()

# EOF

# coding: utf8
# atle.py
# 11/19/2012 jichi
# See: chiitrans2/atlas.cs

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import ctypes
#from sakurakit import msvcrt
from sakurakit.skdebug import dprint, dwarn

ATLE_DLL = 'AtleCont'   # $PROGRAMFILES/ATLAS V14/AtleCond.dll
ATLE_ENCODING = 'sjis'

BUFFER_SIZE = 30000

class _Loader(object):

  def __init__(self):
    self.initialized = False
    self._dll = None
    self._buffer1 = None
    self._buffer2 = None

  @property
  def buffer1(self):
    """
    @return  ctypes.c_void_p
    """
    if not self._buffer1:
      dprint("alloc buffer1")
      #self._buffer1 = msvcrt.malloc(BUFFER_SIZE)
      self._buffer1 = ctypes.create_string_buffer(BUFFER_SIZE)
    return self._buffer1

  @property
  def buffer2(self):
    """
    @return  ctypes.c_void_p
    """
    if not self._buffer2:
      dprint("alloc buffer2")
      #self._buffer2 = msvcrt.malloc(BUFFER_SIZE)
      self._buffer2 = ctypes.create_string_buffer(BUFFER_SIZE)
    return self._buffer2

  #def freeBuffers(self):
  #  if self._buffer1:
  #    dprint("free buffer1")
  #    msvcrt.free(self._buffer1)
  #    self._buffer1 = None
  #  if self._buffer2:
  #    dprint("free buffer2")
  #    msvcrt.free(self._buffer2)
  #    self._buffer2 = None

  @property
  def dll(self):
    if not self._dll:
      try:
        #self._dll = ctypes.WinDLL(ATLE_DLL)
        #self._dll = ctypes.CDLL(ATLE_DLL)
        #self._dll = ctypes.OleDLL(ATLE_DLL)
        #self._dll = ctypes.cdll.LoadLibrary(ATLE_DLL)
        self._dll = ctypes.CDLL(ATLE_DLL)
        dprint("atle dll is loaded")
      except Exception, e:
        dwarn("failed to load atle", e)
    return self._dll

  def hasDll(self): return bool(self._dll)

  def AtlInitEngineData(self):
    """
    @return  bool
    @raise  WindowsError, AttributeError

    IDA disassembled info:
    int __cdecl AtlInitEngineData(HWND hWnd, int, LPCSTR lpString2, int, int)

    Guessed:
    int __cdecl AtlInitEngineData(
      HWND hWnd,
      int unknown,
      LPCSTR lpBuffer1,
      int unknown,
      LBSTR lpBuffer2)
    """
    ok = 0 == self.dll.AtlInitEngineData(0, 2, self.buffer1, 0, self.buffer2)
    dprint("ok = %s" % ok)
    return ok

  def CreateEngine(self):
    """
    @return  bool
    @raise  WindowsError, AttributeError
    """
    ok = 1 == self.dll.CreateEngine(1, 1, 0, 'General')
    dprint("ok = %s" % ok)
    return ok

  def DestroyEngine(self):
    """
    @return  bool
    @raise  WindowsError, AttributeError
    """
    ok = 32768 == self.dll.DestroyEngine()
    dprint("ok = %s" % ok)
    return ok

  def TranslatePair(self, text):
    """
    @param  text  str
    @return  str not None
    @raise  WindowsError, AttributeError
    """
    out = ctypes.c_char_p()
    buf = None
    dwSize = 0
    ok = 0 == self.dll.TranslatePair(text, ctypes.byref(out), None, dwSize)
    ret = out.value
    return ret or ""

class Loader(object):
  def __init__(self):
    self.__d = _Loader()

  def __del__(self):
    self.destroy()

  def init(self):
    d = self.__d
    if d.initialized:
      return
    try:
      d.AtlInitEngineData()
      d.CreateEngine()
      d.initialized = True
    except (WindowsError, AttributeError): pass

  def isInitialized(self): return self.__d.initialized

  def destroy(self):
    d = self.__d
    if d.hasDll():
      try: d.DestroyEngine()
      except Exception, e: dwarn("warning: exception", e)
      d._dll = None
      d.initialized = False
    #d.freeBuffers()

  def translate(self, text):
    """
    @param  text  unicode or str
    @return   unicode not None
    @throw  RuntimeError
    """
    try: return self.__d.TranslatePair(text
        .encode(ATLE_ENCODING, errors='ignore')).decode(ATLE_ENCODING, errors='ignore')
    #except UnicodeError:
    #  dwarn("failed to encode/decode string")
    except (WindowsError, AttributeError), e:
      dwarn("failed to load atle dll", e)
      raise RuntimeError("failed to access atle dll")

if __name__ == '__main__': # DEBUG
  import os
  #os.environ['PATH'] += os.pathsep + r"C:\Program Files\ATLAS V14"
  os.environ['PATH'] += os.pathsep + r"C:\Applications\ATLAS V14"

  l = Loader()
  l.init()
  t = u"お花の匂い"
  ret = l.translate(t)
  print ret
  t = u"そこで私とお父さん、お母さんの一家全員で牧場を切り盛りしてたんですけど"
  ret = l.translate(t)
  print ret
  l.destroy()

# EOF

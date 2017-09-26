# coding: utf8
# nova.py
# 1/19/2012 jichi
# See: LEC Japanese to English Translation Engine.exe

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import ctypes, os
#from sakurakit import msvcrt
from sakurakit.skdebug import dprint, dwarn
import lecdef

BUFFER_SIZE = lecdef.DLL_BUFFER_SIZE

ENGINE_DLL = 'EngineDll_je'   # Nova/JaEn/EngineDll_je.dll
ENGINE_ENCODING = 'sjis'

class _Loader(object):

  # Crash even the safe buffering is enabled
  BUFFER_THREAD_SAFE = False # whether the translation buffers should be thread-safe

  def __init__(self):
    self.initialized = False
    self._dll = None
    self._buffer = None

  @property
  def buffer(self):
    """
    @return  ctypes.c_char_p
    """
    if not self._buffer:
      dprint("alloc buffer")
      #ret = msvcrt.malloc(BUFFER_SIZE)
      #ret = ctypes.cast(ret, ctypes.c_char_p)
      #self._buffer = ret
      self._buffer = ctypes.create_string_buffer(BUFFER_SIZE)
    return self._buffer

  #def freeBuffer(self):
  #  if self._buffer:
  #    dprint("free buffer")
  #    msvcrt.free(self._buffer)
  #    self._buffer = None

  @property
  def dll(self):
    if not self._dll:
      try:
        self._dll = ctypes.CDLL(ENGINE_DLL)
        dprint("nova engine dll is loaded")
      except Exception, e:
        dwarn("failed to load nova", e)
    return self._dll

  #def hasDll(self): return bool(self._dll)

  def _initPath(self):
    """Return the directory path of the dll
    @return  str not unicode (c_char_p)
    @raise  WindowsError, AttributeError
    """
    from win32api import GetModuleFileName
    dllpath = GetModuleFileName(self.dll._handle)
    #dllpath = dllpath.encode('utf8', errors='ignore')
    return os.path.dirname(dllpath)

  def init(self):
    """Initialize the engine
    @return  bool
    @raise  WindowsError, AttributeError

    Guessed:
    int __cdecl eg_init2(
      LPCSTR path, # directory of the engine dll
      int unknown) # offset? Always 0 in "LEC Japanese to English Translation Engine.exe"

    Or:
    int __cdecl eg_init(LPCSTR path)

    return -9998 (0xffffd8f2) if failed
    """
    dprint("enter")
    path = self._initPath()
    ok = 0 == self.dll.eg_init2(path, 0)
    dprint("leave: ok = %s" % ok)
    return ok

  def end(self):
    """Destroy the engine
    @return  bool
    @raise  WindowsError, AttributeError

    Guessed:
    int __cdecl eg_end()
    return value is the same as the eax value after msvcrt.free()
    """
    ok = 1 == self.dll.eg_end()
    dprint("ok = %s" % ok)
    return ok

  def translateOne(self, text):
    """
    @param  text  str not unicode
    @return  str
    @raise  WindowsError, AttributeError

    IDA suggested:
    int __cdecl eg_translate_one(int, int, int, int, char *, int, int)

    Guessed (see the engine exe):
    int __cdecl eg_translate_one(
      int unknown,  // always 0
      LPCSTR input, // [ss:local]
      int unknown,  // always 0
      int bufsz,
      LPSTR buf,    // output
      int unknown,  // always 0
      int unknown)  // always 0
    return 0 if succeeded.
    """
    bufsize = BUFFER_SIZE
    if self.BUFFER_THREAD_SAFE:
      # Limit buffer size would result in crash ... no idea why
      #bufsize = min(bufsize, len(text) * 100) # the translation should be no more larger than 100 times of Japanese
      buf = ctypes.create_string_buffer(bufsize)
    else:
      buf = self.buffer
    ok = 0 == self.dll.eg_translate_one(
        0, text, 0, bufsize, buf, 0, 0)
    return buf.value if ok else ""

class Loader(object):
  def __init__(self):
    self.__d = _Loader()

  def __del__(self):
    self.destroy()

  def init(self):
    d = self.__d
    if not d.initialized:
      try:
        if d.init():
          d.initialized = True
        else:
          d.end()
      except (WindowsError, AttributeError): pass
    return d.initialized

  def isInitialized(self): return self.__d.initialized

  def destroy(self):
    d = self.__d
    if d.initialized:
      try: d.end()
      except Exception, e: dwarn("warning: exception", e)
      d.initialized = False
    #d.freeBuffer()

  # NOTE: "～" ('\uff5e') is not available in shift-jis!
  def translate(self, text):
    """
    @param  text
    @return   unicode not None
    @throw  RuntimeError
    """
    try: return self.__d.translateOne(text
        .encode(ENGINE_ENCODING, errors='ignore')).decode(ENGINE_ENCODING, errors='ignore')
    #except UnicodeError:
    #  dwarn("failed to encode/decode string")
    except (WindowsError, AttributeError), e:
      dwarn("failed to load nova dll", e)
      raise RuntimeError("failed to access nova dll")

if __name__ == '__main__': # DEBUG
  lecpath = r"C:\Program Files\Power Translator 15"
  enginepath = lecpath + r"\Nova\JaEn"
  os.environ['PATH'] += os.pathsep + enginepath
  l = Loader()
  l.init()
  t = u"hello"
  ret = l.translate(t)
  print ret
  t = u"お花の匂い♪"
  ret = l.translate(t)
  print ret
  #t = u"「「寝る「「１つ次の時間帯へ「「どれもやめとく"
  #ret = l.translate(t)

  t = u"まあね♪スカートとはおさらばだし。ハーフパンツなんて久しぶり♪"
  ret = l.translate(t)

  print type(ret)
  print ret
  l.destroy()

# EOF

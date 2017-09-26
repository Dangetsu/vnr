# coding: utf8
# jbjct.py
# 1/3/2013 jichi
#
# Debug method: first find hotspots, then use OllyDbg to find runtime values

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import ctypes
#from sakurakit import msvcrt
from sakurakit.skdebug import dprint, dwarn

# See: http://en.wikipedia.org/wiki/Code_page
CODEPAGE_JA = 932
CODEPAGE_GB = 936
CODEPAGE_BIG5 = 950

BUFFER_SIZE = 3000 # allocate buffer size. p.s. max text size in VNR is 256 * 3=768. BUFFER_SIZE > 768 * 2

# Magic number! See WideCharToMultiByte used by DJC_OpenAllUserDic_Unicode in JBJCT.dll
#
# First call: ESI
# Second call:  ESI + 0x408
# Third call:  ESI + 0x810
USERDIC_PATH_SIZE = 0x204 # without sieof(wchar_t)
MAX_USERDIC_COUNT = 3 # maximum number of user-defined dic
USERDIC_BUFFER_SIZE = USERDIC_PATH_SIZE * MAX_USERDIC_COUNT # 1548, sizeof(wchar_t)

class _Loader(object):

  DLL_MODULE = 'JBJCT'
  BUFFER_THREAD_SAFE = True # whether the translation buffers should be thread-safe

  def __init__(self):
    self.initialized = False
    self._dll = None
    self._buffer1 = None
    self._buffer2 = None
    self._userdicBuffer = None

    self._JC_Transfer_Unicode = None # cached

  @property
  def buffer1(self):
    """
    @return  ctypes.c_wchar_p
    """
    if not self._buffer1:
      dprint("alloc buffer1")
      #ret = msvcrt.malloc(BUFFER_SIZE)
      #ret = ctypes.cast(ret, ctypes.c_wchar_p)
      self._buffer1 = ctypes.create_unicode_buffer(BUFFER_SIZE)
    return self._buffer1

  @property
  def buffer2(self):
    """
    @return  ctypes.c_wchar_p
    """
    if not self._buffer2:
      dprint("alloc buffer2")
      #ret = msvcrt.malloc(BUFFER_SIZE)
      #ret = ctypes.cast(ret, ctypes.c_wchar_p)
      self._buffer2 = ctypes.create_unicode_buffer(BUFFER_SIZE)
    return self._buffer2

  @property
  def userdicBuffer(self):
    """
    @return  POINTER(ctypes.c_wchar)
    """
    if not self._userdicBuffer:
      dprint("alloc userdic buffer")
      #from sakurakit import msvcrt
      #ret = msvcrt.malloc(USERDIC_BUFFER_SIZE)
      #ret = ctypes.cast(ret, ctypes.POINTER(ctypes.c_wchar))
      #self._userdicBuffer = ret
      self._userdicBuffer = ctypes.create_unicode_buffer(USERDIC_BUFFER_SIZE)
    return self._userdicBuffer

  #def freeBuffers(self):
  #  if self._buffer1:
  #    dprint("free buffer1")
  #    msvcrt.free(self._buffer1)
  #    self._buffer1 = None
  #  if self._buffer2:
  #    dprint("free buffer2")
  #    msvcrt.free(self._buffer2)
  #    self._buffer2 = None
  #  if self._userdicBuffer:
  #    dprint("free userdic buffer")
  #    msvcrt.free(self._userdicBuffer)
  #    self._userdicBuffer = None

  @property
  def dll(self):
    if not self._dll:
      try:
        self._dll = ctypes.CDLL(self.DLL_MODULE)
        dprint("jbjct dll is loaded")
      except Exception, e:
        dwarn("failed to load jbjct", e)
    return self._dll

  #def hasDll(self): return bool(self._dll)

  def openAllUserDic(self, paths):
    """Add one user dictionary.
    @param  paths  [unicode]  path to Jcuser.dic, but without ".dic" suffix.
                              At most 3 elements.
    @return  bool
    @raise  WindowsError, AttributeError

    Guessed from OllyDbg:
    //int __cdecl DJC_OpenAllUserDic_Unicode(LPWSTR, LPWSTR unknown, LPWSTR unknown, int unknown)
    int __cdecl DJC_OpenAllUserDic_Unicode(LPWSTR, int unknown)
    Return 1 or -255 if succeeded.

    According to how it is invoked in JCT.exe (push 0), unknown is always 0.
    This function will beep when failed.

    According to how DJC_OpenAllUserDic_Unicode invoke DJC_OpenAllUserDic,
    the first parameter type is supposed to be:
        wchar_t[0x408/sizeof(wchar_t)][3]

    10020150 >/$ 81EC 10060000  SUB ESP,0x610
    10020156  |. A1 50E70710    MOV EAX,DWORD PTR DS:[0x1007E750]
    1002015B  |. 33C4           XOR EAX,ESP
    1002015D  |. 898424 0C06000>MOV DWORD PTR SS:[ESP+0x60C],EAX
    10020164  |. 55             PUSH EBP
    10020165  |. 8B2D A4F20610  MOV EBP,DWORD PTR DS:[<&KERNEL32.WideCha>;  kernel32.WideCharToMultiByte
    1002016B  |. 56             PUSH ESI
    1002016C  |. 8BB424 1C06000>MOV ESI,DWORD PTR SS:[ESP+0x61C]
    10020173  |. 6A 00          PUSH 0x0                                 ; /pDefaultCharUsed = NULL
    10020175  |. 6A 00          PUSH 0x0                                 ; |pDefaultChar = NULL
    10020177  |. 68 04020000    PUSH 0x204                               ; |MultiByteCount = 204 (516.) ; jichi 12/31/2013: 0x204 comes from here
    1002017C  |. 8D4424 14      LEA EAX,DWORD PTR SS:[ESP+0x14]          ; |
    10020180  |. 50             PUSH EAX                                 ; |MultiByteStr
    10020181  |. 6A FF          PUSH -0x1                                ; |WideCharCount = FFFFFFFF (-1.)
    10020183  |. 56             PUSH ESI                                 ; |WideCharStr
    10020184  |. 6A 00          PUSH 0x0                                 ; |Options = 0
    10020186  |. 6A 00          PUSH 0x0                                 ; |CodePage = CP_ACP
    10020188  |. FFD5           CALL EBP                                 ; \WideCharToMultiByte
    1002018A  |. 8BC6           MOV EAX,ESI
    1002018C  |. 8D50 02        LEA EDX,DWORD PTR DS:[EAX+0x2]
    1002018F  |. 90             NOP

    """
    if not paths:
      return False
    if len(paths) > MAX_USERDIC_COUNT:
      dwarn("too many user-defined dictionaries")

    MAX_PATH_LENGTH = USERDIC_PATH_SIZE

    #path = os.path.splitext(path)[0] # remove ".dic" suffix
    buf = self.userdicBuffer
    ctypes.memset(buf, 0, USERDIC_BUFFER_SIZE) # zero memory

    for i in xrange(min(len(paths), MAX_USERDIC_COUNT)):
      path = paths[i]
      if len(path) > MAX_PATH_LENGTH:
        dwarn("path is too long: %s" % path)
        continue
      offset = i * USERDIC_PATH_SIZE
      for index, c in enumerate(path):
        buf[index + offset] = c

    ret = self.dll.DJC_OpenAllUserDic_Unicode(buf, 0)
    return ret in (1,-255)

  def closeAllUserDic(self):
    """Close all user dictionary.
    Guessed from OllyDbg:
    void __cdecl DJC_CloseAllUserDic(int unknown)

    According to how it is invoked in JCT.exe (push 1), unknown is always 1.
    Invoke this function multiple times will never crash.
    """
    self.dll.DJC_CloseAllUserDic(1)

  @property
  def JC_Transfer_Unicode(self):
    """
    @throw  AttributeError
    """
    if self._JC_Transfer_Unicode is None:
      #LPINT = ctypes.POINTER(ctypes.c_int)
      ret = self._JC_Transfer_Unicode = self.dll.JC_Transfer_Unicode
      #t = ctypes.wintypes
      #ret.restypes = int
      #ret.argtypes = t.INT, t.INT, t.INT, t.INT, t.INT, t.LPCWSTR, t.LPWSTR, t.LPVOID, t.LPWSTR, t.LPVOID
    return self._JC_Transfer_Unicode

  def transferUnicode(self, text, to, fr=CODEPAGE_JA):
    """
    @param  text  unicode  not str
    @param  to  uint  code page
    @param  fr  uint  code page
    @raise  WindowsError, AttributeError

    From IDA:
    int __cdecl JC_Transfer_Unicode(int, UINT CodePage, int, int, int, LPCWSTR lpWideCharStr, int, int, int, int)
    Values are get by runtime debugging.

    Guessed
    int __cdecl JC_Transfer_Unicode(
      HWND hwnd,
      UINT fromCodePage,
      UINT toCodePage,
      int unknown,
      int unknown,
      LPCWSTR from,
      LPWSTR to,
      int &toCapacity,
      LPWSTR buffer,
      int &bufferCapacity)

    Note: This function is not thread-safe!
    Using persistent buffers is faster, but not thread-safe!
    """
    size = BUFFER_SIZE
    if self.BUFFER_THREAD_SAFE:
      # Limit buffer size would result in crash ... no idea why
      #size = min(size, len(text) * 10) # the translation should be no more larger than 10 times of Japanese
      out = ctypes.create_unicode_buffer(size)
      buf = ctypes.create_unicode_buffer(size)
    else:
      out = self.buffer1
      buf = self.buffer2
    outsz = ctypes.c_int(size)
    bufsz = ctypes.c_int(size)
    #self.dll.JC_Transfer_Unicode(
    self.JC_Transfer_Unicode(
      0,    # int, unknown
      fr,   # uint from, supposed to be 0x3a4 (cp932)
      to,   # uint to, eighter cp950 or cp932
      1,    # int, unknown
      1,    # int, unknown
      text,
      out,  # wchar_t*
      ctypes.byref(outsz), # &int
      buf,  # wchar_t*
      ctypes.byref(bufsz)) # &int
    return out.value

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
      d.dll
      d.initialized = True
    except (WindowsError, AttributeError): pass

  def isInitialized(self): return self.__d.initialized

  def destroy(self):
    d = self.__d
    if d.initialized:
      self.clearUserDic()
      #d.freeBuffers()
      d.initialized = False

  def setUserDic(self, paths):
    """
    @param  paths  [unicode]  at most three elements
    @return   bool
    """
    try: return self.__d.openAllUserDic(paths)
    except (WindowsError, AttributeError):
      dwarn("failed to load jbjct dll, raise runtime error")
      #raise RuntimeError("failed to access jbjct dll")
      return False

  def clearUserDic(self):
    try: self.__d.closeAllUserDic()
    except (WindowsError, AttributeError):
      dwarn("failed to load jbjct dll, raise runtime error")
      #raise RuntimeError("failed to access jbjct dll")

  def translate(self, text, simplified=False):
    """
    @param  text  unicode  not str!
    @param  simplified  bool
    @return   unicode or None
    @throw  RuntimeError
    """
    try: return self.__d.transferUnicode(text,
        to = CODEPAGE_GB if simplified else CODEPAGE_BIG5)
    except (WindowsError, AttributeError), e:
      dwarn("failed to load jbjct dll, raise runtime error", e)
      raise RuntimeError("failed to access jbjct dll")

if __name__ == '__main__': # DEBUG
  import os
  os.environ['PATH'] += os.pathsep + r"Z:\Local\Windows\Applications\JBeijing7"
  ret = Loader().translate(u"お花の匂い")
  print ret

  ret = Loader().translate(u"せんせい")
  print ret
  l = Loader()

  l.setUserDic((
    u"../../../../../Dictionaries/jb/@jichi/JcUserdic/Jcuser",
    u"../../../../../Dictionaries/jb/@djz020815/JcUserdic/Jcuser",
  ))
  ret = l.translate(u"魑魅魍魎")
  print ret

  ret = l.translate(u"メルキア")
  print ret

  ret = l.translate(u"せんせい")
  print ret

  sys.exit(0)

  ret = Loader().translate(u"脱オタク気分", simplified=True)
  #print ret

  from PySide.QtGui import QApplication, QLabel
  a = QApplication(sys.argv)
  w = QLabel(ret)
  w.show()
  a.exec_()

# EOF

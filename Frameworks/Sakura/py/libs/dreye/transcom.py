# coding: utf8
# transcom.py
# 5/20/2013 jichi

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import ctypes, os
import win32api
#from sakurakit import msvcrt
from sakurakit.skdebug import dprint, dwarn
from sakurakit.skos import CwdChanger

JC_DLL = 'TransCOM' # ja => zhs
JC_BUFFER_SIZE = 3000 # allocate buffer size. p.s. max text size in VNR is 256 * 3=768. BUFFER_SIZE > 768 * 2

EC_DLL = 'TransCOMEC' # en => zhs
EC_BUFFER_SIZE = 10000 # allocate buffer size. p.s. max text size in VNR is 256 * 3=768. BUFFER_SIZE > 768 * 2

# Data files in DreyeMT/SDK
EC_DAT = 1
CE_DAT = 2
CJ_DAT = 3
JC_DAT = 10

JA_ENC = 'sjis'
ZH_ENC = 'gbk'
EN_ENC = 'utf8'

class _JCLoader(object):

  DLL = JC_DLL # str
  BUFFER_SIZE = JC_BUFFER_SIZE

  def __init__(self):
    self.initialized = False
    self._dll = None
    self._dllDirectory = None
    self._buffer = None

  @property
  def buffer(self):
    """
    @return  ctypes.c_char_p
    """
    if not self._buffer:
      dprint("alloc buffer")
      self._buffer = ctypes.create_string_buffer(self.BUFFER_SIZE)
    return self._buffer

  @property
  def dll(self):
    if not self._dll:
      try:
        self._dll = ctypes.CDLL(self.DLL)
        dprint("transcom dll is loaded")
      except (WindowsError, AttributeError), e:
        dwarn("failed to load transcom dll", e)
    return self._dll

  def _dllLocation(self):
    """
    @return  unicode
    @throw  WindowsError, AttributeError
    """
    return win32api.GetModuleFileName(self.dll._handle)

  @property
  def dllDirectory(self):
    """
    @return  unicode
    """
    if not self._dllDirectory:
      try: self._dllDirectory = os.path.dirname(self._dllLocation())
      except (WindowsError, AttributeError, TypeError, os.error), e: dwarn(e)
    return self._dllDirectory

  def init(self):
    """
    @return  bool
    @raise  WindowsError, AttributeError

    Guessed
    int __cdecl MTInitCJ(int dat_index)

    The dat_index is the date file index in DreyeMT/SDK.
    """
    with CwdChanger(self.dllDirectory):
      return -255 == self.dll.MTInitCJ(CJ_DAT)

  def destroy(self):
    """
    @return  bool
    @raise  WindowsError, AttributeError

    Guessed
    int __cdecl MTEndCJ()
    """
    return 1 == self.dll.MTEndCJ()

  def translate(self, text, dat):
    """
    @param  text  str  not unicode
    @param  dat  int
    @raise  WindowsError, AttributeError

    Guessed
    int __cdecl TranTextFlowCJ(
      LPCSTR src,
      LPSTR dest,
      int dest_size,
      int dat_index)
    """
    out = self.buffer
    with CwdChanger(self.dllDirectory):
      self.dll.TranTextFlowCJ(
        text,   # LPCSTR
        out,   # LPSTR
        self.BUFFER_SIZE,  # int
        dat)    # int
    return out.value

class JCLoader(object):
  def __init__(self):
    self.__d = _JCLoader()

  def __del__(self):
    self.destroy()

  def init(self):
    d = self.__d
    if d.initialized:
      return
    try:
      d.dll
      d.init()
      d.initialized = True
    except (WindowsError, AttributeError, TypeError): pass

  def isInitialized(self): return self.__d.initialized

  def destroy(self):
    d = self.__d
    if d.initialized:
      d.destroy()
      #d.freeBuffers()
      d.initialized = False

  def translate(self, text, to='zhs', fr='ja'):
    """
    @param  text  unicode  not str!
    @param  fr  unicode  lang
    @param  to  unicode  lang
    @return   unicode or None
    @throw  RuntimeError
    """
    try:
      jc = fr == 'ja'
      dat = JC_DAT if jc else CJ_DAT
      text = text.encode(JA_ENC if jc else ZH_ENC, errors='ignore')
      ret = self.__d.translate(text, dat)
      ret = ret.decode(ZH_ENC if jc else JA_ENC, errors='ignore')
      return ret
    except (WindowsError, AttributeError, TypeError), e:
      dwarn("failed to load transcome dll, raise runtime error", e)
      raise RuntimeError("failed to access transcom dll")
    #except UnicodeError, e:
    #  dwarn(e)

class _ECLoader(object):

  DLL = EC_DLL # str
  BUFFER_SIZE = EC_BUFFER_SIZE

  def __init__(self):
    self.initialized = False
    self._dll = None
    self._dllDirectory = None
    self._buffer = None

  @property
  def buffer(self):
    """
    @return  ctypes.c_char_p
    """
    if not self._buffer:
      dprint("alloc buffer")
      self._buffer = ctypes.create_string_buffer(self.BUFFER_SIZE)
    return self._buffer

  @property
  def dll(self):
    if not self._dll:
      try:
        self._dll = ctypes.CDLL(self.DLL)
        dprint("transcomec dll is loaded")
      except Exception, e:
        self._dll = None
        dwarn("failed to load transcomec dll", e)
    return self._dll

  def _dllLocation(self):
    """
    @return  str not unicode
    @throw  WindowsError, AttributeError
    """
    return win32api.GetModuleFileName(self.dll._handle)

  @property
  def dllDirectory(self):
    """
    @return  str not unicode
    """
    if not self._dllDirectory:
      try: self._dllDirectory = os.path.dirname(self._dllLocation())
      except (WindowsError, AttributeError, TypeError, os.error), e:
        dwarn(e)
    return self._dllDirectory

  def init(self):
    """
    @return  bool
    @raise  WindowsError, AttributeError

    Guessed
    int __cdecl MTInitEC(int dat_index)

    The dat_index is the date file index in DreyeMT/SDK.
    """
    with CwdChanger(self.dllDirectory):
      ret = -255 == self.dll.MTInitEC(EC_DAT)
    return ret

  def destroy(self):
    """
    @return  bool
    @raise  WindowsError, AttributeError

    Guessed
    int __cdecl MTEndEC()
    """
    return 1 == self.dll.MTEndEC()

  def translate(self, text,dat):
    """
    @param  text  str  not unicode
    @param  dat  int
    @raise  WindowsError, AttributeError

    Guessed
    int __cdecl TranTextFlowCJ(
      LPCSTR src,
      LPSTR dest,
      int dest_size,
      int dat_index)
    """
    out = self.buffer
    with CwdChanger(self.dllDirectory):
      self.dll.TranTextFlowEC(
        text,   # LPCSTR
        out,   # LPSTR
        self.BUFFER_SIZE,  # int
        dat)    # int
    return out.value

class ECLoader(object):
  def __init__(self):
    self.__d = _ECLoader()

  def __del__(self):
    self.destroy()

  def init(self):
    d = self.__d
    if d.initialized:
      return
    try:
      d.dll
      d.init()
      d.initialized = True
    except (WindowsError, AttributeError, TypeError): pass

  def isInitialized(self): return self.__d.initialized

  def destroy(self):
    d = self.__d
    if d.initialized:
      d.destroy()
      #d.freeBuffers()
      d.initialized = False

  def translate(self, text, to='zhs', fr='en'):
    """
    @param  text  unicode  not str!
    @param  simplified  bool
    @return   unicode not None
    @throw  RuntimeError
    """
    try:
      ec = fr == 'en'
      dat = EC_DAT if ec else CE_DAT
      text = text.encode(EN_ENC if ec else ZH_ENC, errors='ignore')
      ret = self.__d.translate(text, dat)
      ret = ret.decode(ZH_ENC if ec else EN_ENC, errors='ignore')
      return ret
    except (WindowsError, AttributeError, TypeError):
      dwarn("failed to load transcomec dll, raise runtime error")
      raise RuntimeError("failed to access transcomec dll")
    #except UnicodeError, e:
    #  dwarn(e)

if __name__ == '__main__': # DEBUG
  import os
  path = r"S:\Applications\Inventec\Dreye\9.0\DreyeMT\SDK\bin"
  os.environ['PATH'] += os.pathsep + path
  #t = JCLoader()
  t = ECLoader()
  t.init()
  #ret = t.translate(u"お花の匂い")
  ret = t.translate(u"hello world")

  from PySide.QtGui import QApplication, QLabel
  a = QApplication(sys.argv)
  w = QLabel(ret)
  w.show()
  a.exec_()

# EOF

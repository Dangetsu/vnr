# coding: utf8
# j2kengine.py
# 6/7/2013 jichi
#
# See: http://ohhara.sarang.net/ohbbhlp/
#
# int (__stdcall *J2K_InitializeEx)(const char *initStr, const char *homeDir);
# char * (__stdcall *J2K_TranslateMMNT)(int data0, const char *jpStr);
# int (__stdcall *J2K_FreeMem)(char *krStr);
# int (__stdcall *J2K_StopTranslation)(int data0);
# int (__stdcall *J2K_Terminate)(void);
# int (__stdcall *K2J_InitializeEx)(const char *initStr, const char *homeDir);
# char * (__stdcall *K2J_TranslateMMNT)(int data0, const char *krStr);
# int (__stdcall *K2J_FreeMem)(char *jpStr);
# int (__stdcall *K2J_StopTranslation)(int data0);
# int (__stdcall *K2J_Terminate)(void);
#
# About Ehnd
# - Source: https://github.com/sokcuri/ehnd
# - Dictionary 2015/04: http://sokcuri.neko.kr/220301117949
# - Binary v3: http://blog.naver.com/waltherp38/220267098421
# - Tutorial: http://blog.naver.com/waltherp38/220286266694
#
# Test Ehnd
# - Input: まあね♪スカートとはおさらばだし。ハーフパンツなんて久しぶり♪
# - ezTrans without ehnd: 그냥♪스커트와는 안녕히이고. 하프 팬츠는 오래간만♪
# - With ehnd 3.1 and 201504 script: 글쎄♪스커트와는 안녕히이고. 하프 팬츠 같은거 오래간만♪
#
# About unloading DLL:
# - Use FreeLibrary to unload: http://stackoverflow.com/questions/13128995/ctypes-unload-dll
# - Use GetModuleHandleA to check: http://stackoverflow.com/questions/11939290/how-do-i-find-out-if-my-program-has-a-certain-dll-already-loaded

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import ctypes, os
#from sakurakit import msvcrt
from sakurakit.skdebug import dprint, dwarn

# Import windows functions
import win32api
GetModuleFileName = win32api.GetModuleFileName # get eztr DLL parent folder
GetModuleHandleA = ctypes.windll.kernel32.GetModuleHandleA # Check if a DLL is loaded
FreeLibrary = ctypes.windll.kernel32.FreeLibrary # Decrease DLL reference count

EZTR_LICENSE = 'CSUSER123455'

EZTR_DLL_MODULE = 'J2KEngine'
EHND_DLL_MODULE = 'ehnd'
#EHND_DLL_MODULE = EZTR_DLL_MODULE # use native DLL

class _Loader(object):

  # See: http://en.wikipedia.org/wiki/Code_page
  INPUT_ENCODING = 'sjis' # Japanese
  OUTPUT_ENCODING = 'uhc' # Korean

  def __init__(self):
    self.initialized = False
    self.ehndEnabled = True

    self._eztrDirectory = None # cached
    self._ehndDll = None # VNR's ehnd dll
    self._eztrDll = None # the effective eztr dll, could be user-customized ehnd dll
    self._nativeEztrDll = None # the original eztr dll

  def getEhndDll(self):
    if not self._ehndDll:
      try:
        self._ehndDll = ctypes.WinDLL(EHND_DLL_MODULE)
        dprint("ehnd dll is loaded")
      except Exception, e:
        dwarn("failed to load ehnd", e)
    return self._ehndDll

  def getEztrDll(self):
    if not self._eztrDll:
      try:
        for suffix in '.dll', '.dlx':
          try:
            self._eztrDll = ctypes.WinDLL(EZTR_DLL_MODULE + suffix)
            dprint("%s is loaded" % (EZTR_DLL_MODULE + suffix))
            break
          except WindowsError: pass
      except Exception, e:
        dwarn("failed to load j2kengine", e)
    return self._eztrDll

  def getNativeEztrDll(self):
    if not self._nativeEztrDll:
      try:
        for suffix in '.dlx', '.dll':
          try:
            self._nativeEztrDll = ctypes.WinDLL(EZTR_DLL_MODULE + suffix)
            dprint("%s is loaded" % (EZTR_DLL_MODULE + suffix))
            break
          except WindowsError: pass
      except Exception, e:
        dwarn("failed to load j2kengine", e)
    return self._nativeEztrDll

  def getEztrDirectory(self):
    """
    @return  str not unicode
    @raise  and hence not made as property
    """
    if not self._eztrDirectory:
      dll = self.getNativeEztrDll()
      self._eztrDirectory = os.path.dirname(
        GetModuleFileName(dll._handle))
    return self._eztrDirectory

  def init(self):
    """
    @return  bool
    @raise

    Guessed:
    BOOL __stdcall J2K_InitializeEx(LPCSTR user_name, LPCSTR dat_path)
    """
    dll = self.getEhndDll() if self.ehndEnabled else self.getEztrDll()
    path = self.getEztrDirectory()
    path = os.path.join(path, 'Dat') # dic data path
    return 1 == dll.J2K_InitializeEx(EZTR_LICENSE, path)

  def terminate(self):
    """
    @raise

    Guessed:
    BOOL __stdcall J2K_Terminate()
    """
    dll = self._ehndDll if self.ehndEnabled else self._eztrDll
    if dll:
      dll.J2K_Terminate()

  def unloadDlls(self):
    self._ehndDll = self._eztrDll = self._nativeEztrDll = None
    for dll in EHND_DLL_MODULE, EZTR_DLL_MODULE + '.dll', EZTR_DLL_MODULE + '.dlx':
      h = GetModuleHandleA(dll)
      if h:
        ok = FreeLibrary(h)
        if ok:
          dprint("unload dll: %s" % dll)
        else:
          dwarn("failed to unload dll: %s" % dll)

  def translate(self, text):
    """
    @param  text  unicode
    @return  unicode
    @raise
    """
    if self.ehndEnabled:
      dll = self.getEhndDll()
      return self._dllTranslateA(dll, text)
    else:
      dll = self.getEztrDll()
      if self._isEhndDll(dll):
        return self._dllTranslateW(dll, text)
      else:
        return self._dllTranslateA(dll, text)

  def _isEhndDll(self, dll):
    """
    @param  dll  ctypes.DLL
    @return bool
    """
    return hasattr(dll, "J2K_TranslateMMNTW")

  def _dllTranslateA(self, dll, text):
    """Translate through Eztr
    @param  dll  ctypes.DLL
    @param  text  unicode
    @return  str not unicode
    @raise  WindowsError, AttributeError

    Guessed:
    char *  __stdcall J2K_TranslateMMNT(int data0, const char *jpStr)
    int  __stdcall J2K_FreeMem(char *krStr)
    """
    text = text.encode(self.INPUT_ENCODING, errors='ignore')
    addr = dll.J2K_TranslateMMNT(0, text)
    if not addr: # int here
      dwarn("null translation address")
      return ""
    text = ctypes.c_char_p(addr).value
    dll.J2K_FreeMem(addr)
    text = text.decode(self.OUTPUT_ENCODING, errors='ignore')
    return text

  def _dllTranslateW(self, dll, text):
    """Translate through Ehnd
    @param  dll  ctypes.DLL
    @param  text  unicode not str
    @return  unicode not str
    @raise  WindowsError, AttributeError
    """
    addr = dll.J2K_TranslateMMNTW(0, text)
    if not addr: # int here
      dwarn("null translation address")
      return ""
    text = ctypes.c_wchar_p(addr).value
    dll.J2K_FreeMem(addr)
    return text

class Loader(object):

  def __init__(self):
    self.__d = _Loader()

  def __del__(self):
    self.destroy()

  def destroy(self):
    d = self.__d
    if d.initialized:
      try: d.terminate()
      except Exception, e: dwarn(e)

  def init(self):
    d = self.__d
    if not d.initialized:
      try: d.initialized = d.init()
      except Exception, e: dwarn(e)

  def isInitialized(self): return self.__d.initialized

  def isEhndEnabled(self): return self.__d.ehndEnabled
  def setEhndEnabled(self, t): self.__d.ehndEnabled = t

  def unload(self):
    d = self.__d
    d.terminate()
    d.initialized = False
    d.unloadDlls()

  def reload(self):
    self.unload()
    self.init()

  def translate(self, text):
    """
    @param  text  unicode
    @return   unicode
    @throw  RuntimeError
    """
    try: return self.__d.translate(text)
    except (WindowsError, AttributeError), e:
      dwarn("failed to load j2kengine dll, raise runtime error", e)
      raise RuntimeError("failed to access j2kengine dll")
    #except UnicodeError, e:
    #  dwarn(e)

if __name__ == '__main__': # DEBUG
  import os
  import sys

  eztrPath = r"Z:\Local\Windows\Applications\ezTrans XP"
  os.environ['PATH'] += os.pathsep + eztrPath
  os.environ['PATH'] += os.pathsep + r"../../../../Boost/bin"
  os.environ['PATH'] += os.pathsep + r"../../../../Ehnd/bin"

  l = Loader()

  l.setEhndEnabled(False)
  l.init()
  #t = u"お花の匂い"
  #t = 「まあね♪スカートとはおさらばだし。ハーフパンツなんて久しぶり♪」
  #t = u"『まあね♪スカートとはおさらばだし。ハーフパンツなんて久しぶり♪』"
  #t = u"まあね♪スカートとはおさらばだし。ハーフパンツなんて久しぶり♪"
  t = u"蜜ドル辞典" # supposed to be 꿀도르 150328 : "전처리필터-사용자사전-후처리필터" OK.
  #t = u"久乃" # supposed to be 히사노
  ret = l.translate(t)

  #l.setEhndEnabled(False)
  #l.reload()
  #ret = l.translate(t)

  #import ctypes
  #h = ctypes.windll.kernel32.GetModuleHandleA(EHND_DLL_MODULE)
  #print h
  #print ctypes.windll.kernel32.FreeLibrary(h)
  #h = ctypes.windll.kernel32.GetModuleHandleA(EHND_DLL_MODULE)
  #print h

  # Without ehnd: 그냥♪스커트와는 안녕히이고. 하프 팬츠는 오래간만♪
  # With ehnd 3.1: 글쎄♪스커트와는 안녕히이고. 하프 팬츠 같은거 오래간만♪

  from PySide.QtGui import QApplication, QTextEdit
  a = QApplication(sys.argv)
  w = QTextEdit(ret)
  w.show()
  a.exec_()

# EOF

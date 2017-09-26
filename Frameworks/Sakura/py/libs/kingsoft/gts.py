# coding: utf8
# gts.py
# 9/17/2014 jichi
#
# Debug method: Use OllyDbg to debug SeniorTranslate.exe
#
# DLLs:
# - GTS/EnglishSChinese/EngSChSDK.dll
# - GTS/EnglishTChinese/EngTChSDK.dll
# - GTS/JapaneseSChinese/dlltest.exe
# - GTS/JapaneseSChinese/JPNSCHSDK.dll
# - GTS/JapaneseTChinese/JPNTCHSDK.dll
# - GTS/SChineseEnglish/SchEngSDK.dll
# - GTS/TChineseEnglish/TchEngSDK.dll
#
# Referenced texts in SeniorTranslate.exe:
#
#   0041F83F   MOV EDI,SeniorTr.0042FF68                 UNICODE "GTS\"
#   0041F8EA   MOV EDI,SeniorTr.0042FF68                 UNICODE "GTS\"
#   0041F973   PUSH SeniorTr.0042FF74                    ASCII "StartSession"
#   0041F97E   PUSH SeniorTr.0042FF84                    ASCII "EndSession"
#   0041F98C   PUSH SeniorTr.0042FF90                    ASCII "OpenEngine"
#   0041F99D   PUSH SeniorTr.0042FF9C                    ASCII "CloseEngineM"
#   0041F9A8   PUSH SeniorTr.0042FFAC                    ASCII "SetBasicDictPathM"
#   0041F9B6   PUSH SeniorTr.0042FFC0                    ASCII "SetProfDictPathM"
#   0041F9C7   PUSH SeniorTr.0042FFD4                    ASCII "RemoveProfDictPathM"
#   0041F9D2   PUSH SeniorTr.0042FFE8                    ASCII "GetProfDictPath"
#   0041F9E0   PUSH SeniorTr.0042FFF8                    ASCII "SetUserDictPathM"
#   0041F9F1   PUSH SeniorTr.0043000C                    ASCII "ExtractSentenceWM"
#   0041F9FC   PUSH SeniorTr.00430020                    ASCII "SimpleTransSentM"
#   0041FA0A   PUSH SeniorTr.00430034                    ASCII "TranslateParagraphs"
#   0041FA1B   PUSH SeniorTr.00430048                    ASCII "LookupDictionary5"
#   0041FA26   PUSH SeniorTr.0043005C                    ASCII "Translate_FileM"
#   0041FA34   PUSH SeniorTr.0043006C                    ASCII "AddWordM"
#   0041FA45   PUSH SeniorTr.00430078                    ASCII "DeleteWordM"
#   0041FA50   PUSH SeniorTr.00430084                    ASCII "SetTranslationOption2"
#   0041FA5E   PUSH SeniorTr.0043009C                    ASCII "SetTranslationOption3"
#   0041FA6F   PUSH SeniorTr.004300B4                    ASCII "TranslateSentence3"
#   0041FB6F   MOV EDI,SeniorTr.004300C8                 UNICODE "DCT"
#   0041FBB6   MOV EDI,SeniorTr.004300C8                 UNICODE "DCT"
#   0041FCD8   PUSH SeniorTr.004300D0                    ASCII "DCT"
#   0041FE18   MOV EDI,SeniorTr.004300D4                 UNICODE "\ProfDict.INI"
#   0041FE64   PUSH SeniorTr.004300F4                    UNICODE "User"
#   0041FE86   PUSH SeniorTr.004300F4                    UNICODE "User"
#   00420032   MOV EDI,SeniorTr.004300D4                 UNICODE "\ProfDict.INI"
#   0042016E   PUSH SeniorTr.004300F4                    UNICODE "User"
#   0042074B   MOV ESI,SeniorTr.004301D0                 UNICODE "UserDict.INI"
#   004207AC   PUSH SeniorTr.004301EC                    UNICODE "%s%s"
#   00420F47   PUSH SeniorTr.0043024C                    UNICODE "Item"
#   00420F97   PUSH SeniorTr.0043025C                    UNICODE ",,"
#   004210DB   PUSH SeniorTr.0043025C                    UNICODE ",,"
#   0042165D   PUSH SeniorTr.004300F4                    UNICODE "User"
#   00421A1C   MOV ECX,SeniorTr.004302C0                 ASCII "USW["
#   00421A3B   MOV EDX,SeniorTr.0042AC3C                 ASCII "GP

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import ctypes, os
import win32api
#from sakurakit import msvcrt
from sakurakit.skdebug import dprint, dwarn
from sakurakit.skunicode import u, u_sjis

SESSION_BUFFER_SIZE = 0x40 # the same as JBeijing
ZH_BUFFER_SIZE = 3000 # allocate buffer size. p.s. max text size in VNR is 256 * 3=768. BUFFER_SIZE > 768 * 2
EN_BUFFER_SIZE = 10000 # allocate buffer size. p.s. max text size in VNR is 256 * 3=768. BUFFER_SIZE > 768 * 2
#ENCODING = 'utf16' # unicode

DEFAULT_DIC = "DCT"
USER_DIC = "User"

PROF_DIC_ENABLED = False # disable prof dict by default that is slow

class _Loader(object):

  BUFFER_THREAD_SAFE = False # whether the translation buffers should be thread-safe

  def __init__(self, dllPath, bufferSize):
    self.dllPath = dllPath # unicode
    self.bufferSize = bufferSize # int

    self.initialized = False # bool
    self._dll = None
    self._dllDirectory = None # unicode
    self._sessionBuffer = None # char[]
    self._outputBuffer = None # wchar_t[]

    self.key = self._randomEngineKey() # int

  @staticmethod
  def _randomEngineKey():
    """
    @return  int
    """
    from time import time
    return int(time()) % 0xffff

  @property
  def sessionBuffer(self):
    """
    @return  ctypes.c_char_p
    """
    if not self._sessionBuffer:
      dprint("alloc session buffer")
      self._sessionBuffer = ctypes.create_string_buffer(SESSION_BUFFER_SIZE)
    return self._sessionBuffer

  @property
  def outputBuffer(self):
    """
    @return  ctypes.c_wchar_p
    """
    if not self._outputBuffer:
      dprint("alloc output buffer")
      self._outputBuffer = ctypes.create_unicode_buffer(self.bufferSize)
    return self._outputBuffer

  @property
  def dll(self):
    if not self._dll:
      try:
        self._dll = ctypes.WinDLL(self.dllPath)
        dprint("gts sdk dll is loaded")
      except Exception, e:
        dwarn("failed to load gts sdk dll", e)
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
    @return  str not unicode
    """
    if not self._dllDirectory:
      try: self._dllDirectory = os.path.dirname(self._dllLocation())
      except (WindowsError, AttributeError, TypeError, os.error), e: dwarn(e)
    return self._dllDirectory

  def init(self):
    """
    @return  bool
    @raise  WindowsError, AttributeError
    """
    return bool(self.dllDirectory) and self._startSession() and self._openEngine() and self._setDictionaries()

  def _setDictionaries(self):
    dprint("enter")
    path = self.dllDirectory

    # Load default dic, which is required
    defdic = os.path.join(path, DEFAULT_DIC)
    ret = self._setBasicDictPath(os.path.join(defdic)) # this cannot fail, or it won't work

    # This will double the translation time orz.
    # I should selectively enable the dict that is useful
    if PROF_DIC_ENABLED:
      # Load extra dic, which is optional
      priority = 0
      for dic in os.listdir(path):
        if dic not in (DEFAULT_DIC, USER_DIC):
          dicpath = os.path.join(path, dic)
          if os.path.isdir(dicpath):
            priority += 1
            self._setProfDictPath(dicpath, priority)

    # Load user dic
    from sakurakit import skfileio
    userdic = os.path.join(path, USER_DIC)
    if userdic and os.path.exists(userdic) and not skfileio.emptydir(userdic):
      self._setUserDictPathA(userdic)

    dprint("leave: ok = %s" % ret)
    return ret

  def _startSession(self):
    """
    @return  bool
    @raise  WindowsError, AttributeError

    Guessed:
    int __stdcall StartSession(LPCWSTR path, DWORD bufferStart, DWORD bufferStop, LPCWSTR pathName)

    path must be unicode instead of str.
    start and stop are a chunk of buffer, size = 0x40

    Debugging method: debug SeniorTranslate for StartSession
       054FFF10   0041FC12  RETURN to SeniorTr.0041FC12
       054FFF14   01554F98  UNICODE "C:\tmp\FASTAIT_PERSONAL\GTS\JapaneseSChinese\DCT"
       054FFF18   01550C60  ; pointer to a chunk of zeros
       054FFF1C   01550C20  ; pointer to 0x00
       054FFF20   01550C40  UNICODE "DCT"
       054FFF24   9A9C60FE
       054FFF28   015593A0
       054FFF2C   054FFF88
       054FFF30   00000488
       054FFF34   01550C40  UNICODE "DCT"
       054FFF38   01550C20
       054FFF3C   01550C60
       054FFF40   01554F98  UNICODE "C:\tmp\FASTAIT_PERSONAL\GTS\JapaneseSChinese\DCT"
       054FFF44   054FFF7C  Pointer to next SEH record
       054FFF48   00425D84  SE handler
       054FFF4C   00000003
       054FFF50   0040C48B  RETURN to SeniorTr.0040C48B from SeniorTr.0041FB40
    """
    dicpath = u(os.path.join(self.dllDirectory, DEFAULT_DIC))
    if not dicpath or not os.path.exists(dicpath):
      dwarn("gts dic directory does not exist")
      return False
    buf = self.sessionBuffer
    start = ctypes.addressof(buf)
    stop = start + SESSION_BUFFER_SIZE
    ok = 0 == self.dll.StartSession(dicpath, start, stop, DEFAULT_DIC)
    dprint("ok =", ok)
    return ok

  def _endSession(self):
    """
    @return  bool
    @raise  WindowsError, AttributeError

    Guessed:
    int __stdcall EndSession()
    """
    return 0 == self.dll.EndSession()

  def _openEngine(self):
    """
    @return  bool
    @raise  WindowsError, AttributeError

    Guessed:
    int __stdcall OpenEngine(DWORD key)
    """
    ok = 0 == self.dll.OpenEngine(self.key)
    dprint("ok =", ok)
    return ok

  def _closeEngine(self):
    """
    @return  bool
    @raise  WindowsError, AttributeError

    Guessed:
    int __stdcall CloseEngine()
    int __stdcall CloseEngineM(DWORD key)
    """
    return 0 == self.dll.CloseEngineM(self.key)

  def _setBasicDictPath(self, path):
    """
    @param  path  unicode
    @return  bool
    @raise  WindowsError, AttributeError

    Guessed:
    int __stdcall SetBasicDictPathM(int key, LPCSTR path)
    int __stdcall SetBasicDictPathW(int key, LPCWSTR path)

    path is the DCT path.
    """
    dprint("pass")
    return 0 == (
        self.dll.SetBasicDictPathM(self.key, path) if isinstance(path, str) else
        self.dll.SetBasicDictPathW(self.key, path))

  def _setProfDictPath(self, path, priority):
    """
    @param  path  unicode
    @param  priority  int
    @return  bool
    @raise  WindowsError, AttributeError

    Guessed:
    int __stdcall SetProfDictPathM(int key, LPCSTR path, int priority)
    int __stdcall SetProfDictPathW(int key, LPCWSTR path, int priority)

    path is any dict directory in the same directory of the dll.
    """
    #dprint("pass")
    return 0 == (
        self.dll.SetProfDictPathM(self.key, path, priority) if isinstance(path, str) else
        self.dll.SetProfDictPathW(self.key, path, priority))

  def _setUserDictPathA(self, path):
    """
    @param  path  str not unicode
    @return  bool
    @raise  WindowsError, AttributeError

    Guessed:
    int __stdcall SetUserDictPathM(int key, LPCSTR path)

    It is weid that there is no W version for this function.
    """
    dprint("pass")
    return 0 == self.dll.SetUserDictPathM(self.key, path)

  def destroy(self):
    """
    @return  bool
    @raise  WindowsError, AttributeError
    """
    return self._closeEngine() and self._endSession()

  def translate(self, text):
    """
    @param  text  unicode not str
    @raise  WindowsError, AttributeError

    Guessed
    int __stdcall SimpleTransSentM(int key, LPCWSTR input, LPWSTR buffer, int bufferSize, int unknown)

    The value of unknown is get by debugging JPNSCHSDK.dll in SeniorTranslate.exe
    """
    bufsize = self.bufferSize
    if self.BUFFER_THREAD_SAFE:
      # Limit buffer size would result in crash ... no idea why
      #bufsize = min(bufsize, len(text) * 10) # the translation should be no more larger than 10 times of Japanese
      buf = ctypes.create_string_buffer(bufsize)
    else:
      out = self.outputBuffer
    ok = 0 == self.dll.SimpleTransSentM(self.key, text, out, bufsize, 0x4) # 0x4 is magic number
    return out.value if ok else u''

class Loader(object):
  def __init__(self, dllPath, bufferSize): # unicode, int ->
    self.__d = _Loader(dllPath, bufferSize)

  def __del__(self):
    self.destroy()

  def init(self):
    d = self.__d
    if d.initialized:
      return
    #try:
    if True:
      d.dll
      d.init()
      d.initialized = True
    #except (WindowsError, AttributeError, TypeError): pass

  def isInitialized(self): return self.__d.initialized

  def destroy(self):
    d = self.__d
    if d.initialized:
      d.destroy()
      #d.freeBuffers()
      d.initialized = False

  def translate(self, text):
    """
    @param  text  unicode  not str
    @return   unicode or None
    @throw  RuntimeError
    """
    try:
      if isinstance(text, str):
        text = u_sjis(text)
        if not text:
          return ''
      return self.__d.translate(text)
    except (WindowsError, AttributeError, TypeError), e:
      dwarn("failed to load gts sdk dll, raise runtime error", e)
      raise RuntimeError("failed to access gts sdk dll")
    #except UnicodeError, e:
    #  dwarn(e)

if __name__ == '__main__': # DEBUG
  import os
  langs = 'jazhs'
  #langs = 'jazht'
  #langs = 'enzht'
  #langs = 'enzhs'
  #langs = 'zhsen'

  #s = u"こんにちは"
  #s = u"お花の匂い"
  #s = u"憎しみは憎しみしか生まない。"
  #s = u"123.45は憎しか生まない。"
  s = u"テキストまたはウェブサイトのアドレスを入力するか、ドキュメントを翻訳します。"
  #s = u"憎しみは憎しみしか生まない。 そんなことを聞いたことがありますが、誰でも人生の中で一度や二度、他人(親兄弟も ... 憎む理由はなんでしょうか？ 自分に不利益な何かをもたらしたから？ "
  #s = u"憎しみは憎しみしか生まない。"
  #s = u"そんなことを聞いたことがありますが、誰でも人生の中で一度や二度、他人(親兄弟も ... 憎む理由はなんでしょうか？ 自分に不利益な何かをもたらしたから？ "
  #s = u"そんなことを聞いたことがありますが、誰でも人生の中で一度や二度、他人(親兄弟も ... 憎む理由はなんでしょうか？ 自分に不利益な何かをもたらしたから？ "
  #s = u"自分に不利益な何かをもたらしたから？"
  #s = u"憎む理由はなんでしょうか？" # why this is very slow? certain phrase is missing?
  #s = "hello"
  #s = u'你好'
  #s = u'你说什么'
  #s = u'what did you say?'

  from fastait import DLLS

  path = r"Z:\Local\Windows\Applications\FASTAIT_PERSONAL"
  #path = r"C:\tmp\FASTAIT_PERSONAL"
  dllpath = DLLS[langs]
  dllpath = os.path.join(path, dllpath)
  bufsize = ZH_BUFFER_SIZE
  os.environ['PATH'] += os.pathsep + os.path.dirname(dllpath)
  t = Loader(dllpath, bufsize)
  t.init()

  from sakurakit.skprof import SkProfiler
  with SkProfiler():
    ret = t.translate(s)
  with SkProfiler():
    ret = t.translate(s)
  with SkProfiler():
    ret = t.translate(s)
  with SkProfiler():
    ret = t.translate(s)

  from PySide.QtGui import QApplication, QLabel
  a = QApplication(sys.argv)
  w = QLabel(ret)
  w.show()
  a.exec_()

# EOF

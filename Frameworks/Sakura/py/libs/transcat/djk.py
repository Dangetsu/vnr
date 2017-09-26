# coding: utf8
# djk.py
# 3/1/2015 jichi
#
# D_JK.dll is loaded.
# Though there is also a JKTrans function, which is not invoked by transcat though.
# TransCAT requires a Korean localed Windows to work properly.
#
# See: https://bitbucket.org/AralGood/araltrans-0.2
#
# TransCAT.h:
#   int (__stdcall * JK_TransStart)(const char *jpStr, int jpLen);
#   bool (__stdcall * JK_TransEndingEx)(int data1, const char *krStr, int jpLen);
#   int (__stdcall * GSetJK_gdDir)(int data1, const char *szDir);
#   int (__stdcall * GSetJK_gdTempGenbun)(int data1, const char *szStr);
#   int (__stdcall * GSetJK_gdTempTerget)(int data1, const char *szStr);
#   int (__stdcall * GSetJK_gdTempMorph)(int data1, const char *szStr);
#   int (__stdcall * GSetJK_gdTempChnGen)(int data1, const char *szStr);
#
#   int (__stdcall * GSetJK_gQUESTIONMARK)(int data1, int data2);
#   int (__stdcall * GSetJK_gEXCLAMATION)(int data1, int data2);
#   int (__stdcall * GSetJK_gSEMICOLONMARK)(int data1, int data2);
#   int (__stdcall * GSetJK_gCOLONMARK)(int data1, int data2);
#   int (__stdcall * GSetJK_gdChudanFlag)(int data1, int data2);
#   int (__stdcall * GSetJK_gdUseShiftJisCode)(int data1, int data2);
#   int (__stdcall * GSetJK_gdDdeSpaceCut)(int data1, int data2);
#   int (__stdcall * GSetJK_gnDdeTransFlag)(int data1, int data2);
#   int (__stdcall * GSetJK_gdFileTransFlag)(int data1, int data2);
#   int (__stdcall * GSetJK_gdLineFlag)(int data1, int data2);
#   int (__stdcall * GSetJK_gdLineLength)(int data1, int data2);
#   int (__stdcall * GSetJK_gdPeriodOnly)(int data1, int data2);
#   int (__stdcall * GSetJK_gdUseGairaiFlag)(int data1, int data2);
#   int (__stdcall * GSetJK_gdUseKanjiFlag)(int data1, int data2);
#   int (__stdcall * GSetJK_gbUnDDE)(int data1, int data2);
#
#   int (__stdcall * ControlJK_UserDic)(int data1);
#   int (__stdcall * GSetJK_UserDicInit)();
#   bool (__stdcall * GSetJK_ITEngineEx)(const char *szTmp, const char *szTmp2);
#
# TransCAT.cpp:
# - Translate:
#   int nBool = pThis->m_TCDLL.JK_TransStart(cszJpnText, strlen(cszJpnText));
#   char szTrans[2048] = {0,};
#   bool bTrans = pThis->m_TCDLL.JK_TransEndingEx(1, szTrans, strlen(cszJpnText));
#
# - Init:
#   DWORD dwOldProtect, dwTmpProtect;
#   BYTE editCode = 0xEB;
#   HMODULE hModule = NULL;
#   ::GetModuleHandleEx(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS, (LPCTSTR)pFuncAddr, &hModule);
#
#   ::VirtualProtect((BYTE*)hModule + 0xFC80, 1, PAGE_READWRITE, &dwOldProtect);
#   memset((BYTE*)hModule + 0xFC80,0xEB,1);
#   ::VirtualProtect((BYTE*)hModule + 0xFC80, 1, dwOldProtect, &dwTmpProtect);
#
#   ::VirtualProtect((BYTE*)hModule + 0xFC98, 1, PAGE_EXECUTE_READWRITE, &dwOldProtect);
#   memset((BYTE*)hModule + 0xFC98,0xEB,1);
#   ::VirtualProtect((BYTE*)hModule + 0xFC98, 1, dwOldProtect, &dwTmpProtect);
#
#   char szHomeDir[MAX_PATH];
#   ::WideCharToMultiByte(CP_ACP, 0, (LPCWSTR)m_strHomeDir, -1, szHomeDir, MAX_PATH, NULL, NULL);
#   m_TCDLL.GSetJK_gdDir(1, szHomeDir);
#   m_TCDLL.GSetJK_gdTempGenbun(1, "GENBUN_PJK");
#   m_TCDLL.GSetJK_gdTempTerget(1, "TERGET_PJK");
#   m_TCDLL.GSetJK_gdTempMorph(1, "MORPH_PJK");
#   m_TCDLL.GSetJK_gdTempChnGen(1, "KRNGEN_PJK");
#
#   m_TCDLL.GSetJK_gQUESTIONMARK(1, 0);
#   m_TCDLL.GSetJK_gEXCLAMATION(1, 0);
#   m_TCDLL.GSetJK_gSEMICOLONMARK(1, 0);
#   m_TCDLL.GSetJK_gCOLONMARK(1, 0);
#   m_TCDLL.GSetJK_gdChudanFlag(0, 0);
#   m_TCDLL.GSetJK_gdUseShiftJisCode(1, 1);
#   m_TCDLL.GSetJK_gdDdeSpaceCut(1, 0);
#   m_TCDLL.GSetJK_gnDdeTransFlag(1, 0);
#   m_TCDLL.GSetJK_gdFileTransFlag(1, 0);
#   m_TCDLL.GSetJK_gdLineFlag(1, 2);
#   m_TCDLL.GSetJK_gdLineLength(1, 48);
#   m_TCDLL.GSetJK_gdPeriodOnly(1, 0);
#   m_TCDLL.GSetJK_gdUseGairaiFlag(1, 0);
#   m_TCDLL.GSetJK_gdUseKanjiFlag(1, 1);
#   m_TCDLL.GSetJK_gbUnDDE(1, 0);
#
#   m_TCDLL.ControlJK_UserDic(1);
#   m_TCDLL.GSetJK_UserDicInit();
#
#   char str[1] = {0,};
#   bool bErr = m_TCDLL.GSetJK_ITEngineEx(str, str);

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import ctypes, os
import win32con, win32api
from sakurakit.skdebug import dprint, dwarn

BUFFER_SIZE = 3000 # allocate buffer size. p.s. max text size in VNR is 256 * 3=768. BUFFER_SIZE > 768 * 2

class _Loader(object):

  DLL_MODULE = 'D_JK'

  def __init__(self):
    self.initialized = False
    self._dll = None
    self._buffer = None # persistent buffer makes the translation not thread-safe
    self.tempDir = '' # A temporary directory

  @property
  def buffer(self):
    """
    @return  ctypes.c_char_p
    """
    if not self._buffer:
      dprint("alloc buffer")
      self._buffer = ctypes.create_string_buffer(BUFFER_SIZE)
    return self._buffer

  @property
  def dll(self):
    if not self._dll:
      try:
        self._dll = ctypes.WinDLL(self.DLL_MODULE)
        dprint("D_JK dll is loaded")
      except Exception, e:
        dwarn("failed to load D_JK", e)
    return self._dll

  @staticmethod
  def _normalizeDirPath(path, encoding='utf8'):
    """
    @param  str or unicode
    @return  str
    """
    if not path:
      return ''
    path = path.replace('/', '\\')
    if isinstance(path, unicode):
      path = path.encode(enoding)
    if path[-1] != '\\':
      path += '\\' # must end with '\'
    return path

  def init(self):
    """
    @return  bool
    @raise
    """
    # Get DLL location
    dllHandle = self.dll._handle # DWORD module
    dllPath = win32api.GetModuleFileName(dllHandle)
    appDir = os.path.dirname(dllPath) # TransCAT location

    appDir = self._normalizeDirPath(appDir)

    tempDir = self.tempDir
    if not tempDir:
      tempDir = ''
    else:
      if not os.path.exists(tempDir):
        os.makedirs(tempDir)
      tempDir = self._normalizeDirPath(tempDir)

    # Import needed Windows functions
    kernel32 = ctypes.windll.kernel32
    GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS = 4 # not exist in win32con
    GetModuleHandleExA = kernel32.GetModuleHandleExA
    VirtualProtect = kernel32.VirtualProtect

    pFuncAddr = win32api.GetProcAddress(dllHandle, "GSetJK_ITEngineEx")
    hModule = ctypes.c_long(0)
    GetModuleHandleExA(GET_MODULE_HANDLE_EX_FLAG_FROM_ADDRESS, pFuncAddr, ctypes.byref(hModule))
    hModule = hModule.value # convert to C long type

    # Hack dll memory or it will raise illegal access to 0xeb error
    EDIT_CODE = 0xeb
    for offset, permission in (
        (0xfc80, win32con.PAGE_READWRITE),
        (0xfc98, win32con.PAGE_EXECUTE_READWRITE),
      ):
      dwOldProtect = ctypes.c_long(0)
      VirtualProtect(hModule + offset, 1, permission, ctypes.byref(dwOldProtect))
      ctypes.memset(hModule + offset, EDIT_CODE, 1)
      dwTmpProtect = ctypes.c_long(0)
      VirtualProtect(hModule + offset, 1, dwOldProtect, ctypes.byref(dwTmpProtect))

    # *_PJK files must be in a directory where VNR always have read/write permission
    # By default, TransCAT is installed to ProgramFiles which require admin privilege to modify.

    dll = self.dll

    dll.GSetJK_gdDir(1, appDir) # optional if it is the same as the current directory
    dll.GSetJK_gdTempGenbun(1, tempDir + "GENBUN_PJK") # VNR must have read/write access to this temp file
    dll.GSetJK_gdTempTerget(1, tempDir + "TERGET_PJK") # VNR must have read/write access to this temp file
    dll.GSetJK_gdTempMorph(1, tempDir + "MORPH_PJK") # VNR must have read/write access to this temp file
    dll.GSetJK_gdTempChnGen(1, tempDir + "KRNGEN_PJK") # VNR must have read/write access to this temp file
    dll.GSetJK_gQUESTIONMARK(1, 0)
    dll.GSetJK_gEXCLAMATION(1, 0)
    dll.GSetJK_gSEMICOLONMARK(1, 0)
    dll.GSetJK_gCOLONMARK(1, 0)
    dll.GSetJK_gdChudanFlag(0, 0)
    dll.GSetJK_gdUseShiftJisCode(1, 1)
    dll.GSetJK_gdDdeSpaceCut(1, 0)
    dll.GSetJK_gnDdeTransFlag(1, 0)
    dll.GSetJK_gdFileTransFlag(1, 0)
    dll.GSetJK_gdLineFlag(1, 2)
    dll.GSetJK_gdLineLength(1, 48)
    dll.GSetJK_gdPeriodOnly(1, 0)
    dll.GSetJK_gdUseGairaiFlag(1, 0)
    dll.GSetJK_gdUseKanjiFlag(1, 1)
    dll.GSetJK_gbUnDDE(1, 0)

    dll.ControlJK_UserDic(1)
    dll.GSetJK_UserDicInit()

    s = '' # char s[1] = {'0'};
    res = dll.GSetJK_ITEngineEx(s, s)
    ok = res == 1
    return ok

  def translate(self, text):
    """
    @param  text  str not unicode
    @return  str not unicode
    @raise  WindowsError, AttributeError
    """
    dll = self.dll
    res = dll.JKTransStart(text, len(text))
    if res == 2:
      buf = self.buffer
      ok = dll.JKTransEndingEx(1, ctypes.byref(buf), len(buf))
      if ok == 1:
        #dll.JKFreeMem(buf) # buffer not freed but being reused
        return buf.value
    dwarn("translate functions return false")
    return ''

class Loader(object):

  # See: http://en.wikipedia.org/wiki/Code_page
  INPUT_ENCODING = 'sjis' # Japanese
  OUTPUT_ENCODING = 'uhc' # Korean

  def __init__(self, tmpdir=''):
    """
    @param* tmpdir  unicode
    """
    self.__d = _Loader()
    self.__d.tempDir = tmpdir

  def __del__(self):
    self.destroy()

  def init(self):
    d = self.__d
    if d.initialized:
      return
    try: d.initialized = d.init()
    except Exception, e:
      dwarn(e)

  def isInitialized(self): return self.__d.initialized

  def destroy(self): pass

  def translate(self, text):
    """
    @param  text  unicode
    @return   unicode
    @throw  RuntimeError
    """
    try: return self.__d.translate(
        text.encode(self.INPUT_ENCODING, errors='ignore')).decode(self.OUTPUT_ENCODING, errors='ignore')
    except (WindowsError, AttributeError), e:
      dwarn("failed to load D_JK dll, raise runtime error", e)
      raise RuntimeError("failed to access D_JK dll")
    #except UnicodeError, e:
    #  dwarn(e)

if __name__ == '__main__': # DEBUG
  import os
  os.environ['PATH'] += os.pathsep + r"Z:\Local\Windows\Applications\DICO SYSTEM\TransCAT KJJK"
  l = Loader()
  l.init()

  #ret = l.translate(u"お花の匂い☆")
  ret = l.translate(u"「まあね♪スカートとはおさらばだし。ハーフパンツなんて久しぶり♪」")

  from PySide.QtGui import QApplication, QTextEdit
  a = QApplication(sys.argv)
  w = QTextEdit(ret)
  w.show()
  a.exec_()

# EOF

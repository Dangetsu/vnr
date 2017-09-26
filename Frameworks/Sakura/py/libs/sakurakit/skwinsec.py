# coding: utf8
# skwinsec.py
# 12/11/2012 jichi
# Windows only

SE_DEBUG_PRIVILEGE = 'SeDebugPrivilege'
SE_TIMEZONE_PRIVILEGE = 'SeTimeZonePrivilege'

import skos
if skos.WIN:
  import os
  import win32api, win32con, win32security
  import skwin, skwinapi
  from skdebug import dprint, dwarn

  # See: http://code.msdn.microsoft.com/windowsdesktop/CppUACSelfElevation-981c0160/sourcecode?fileId=21590&pathId=2074248535
  def elevate(path=None, params=None, cwd=None, hwnd=0):
    """
    @param  path  str or None  If none, elevate current process
    @param  cwd  str or None  If none, use the dirname of path
    @param  hwnd  parent window or 0
    @return  bool
    """
    op = 'runas'
    path = path or win32api.GetModuleFileName(None) # python path
    cwd = cwd or (os.path.dirname(path) if path else "")
    try:
      # See: http://timgolden.me.uk/pywin32-docs/win32api__ShellExecute_meth.html
      win32api.ShellExecute(hwnd, op, path, params, cwd, win32con.SW_SHOW)
      return True
    except:
      return False

  # See: http://code.msdn.microsoft.com/windowsdesktop/CppUACSelfElevation-981c0160/sourcecode?fileId=21590&pathId=2074248535
  def is_elevated():
    """
    @return  bool or None  if the current process is elevated, or None on xp
    """
    try:
      ph =  win32api.GetCurrentProcess()
      tok = win32security.OpenProcessToken(ph, win32con.TOKEN_QUERY)

      # type(tic) == TokenInformationClass
      b = win32security.GetTokenInformation(tok, win32security.TokenElevation)
      return bool(b)
    except: pass # could be windows XP

  class _SkProcessElevator: pass
  class SkProcessElevator:
    def __init__(self, priv):
      """
      @param  priv  unicode or [unicode] or None
      """
      d = self.__d = _SkProcessElevator()

      if type(priv) in (str, unicode):
        priv = [priv]

      d.token = None    # process token
      try:
        d.privileges = [(  # current or previous privileges
          win32security.LookupPrivilegeValue('', p),
          win32con.SE_PRIVILEGE_ENABLED,
        ) for p in priv] if priv else [] # [] not None
      except Exception, e: # pywintypes.error
        dwarn(e)
        d.privileges = None

    def __enter__(self):
      d = self.__d
      if not d.privileges:
        dwarn("failed to elevate privilege. This is might be a Windows XP machine")
        return

      # See: http://msdn.microsoft.com/ja-jp/library/windows/desktop/ms724944%28v=vs.85%29.aspx
      # See: http://nullege.com/codes/search/win32security.AdjustTokenPrivileges
      # See: http://www.oschina.net/code/explore/chromium.r67069/third_party/python_24/Lib/site-packages/win32/Demos/security/setkernelobjectsecurity.py

      #pid = win32api.GetCurrentProcessId()
      #ph = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, 0, pid)

      ph =  win32api.GetCurrentProcess()
      #d.token = win32security.OpenProcessToken(ph, win32con.TOKEN_ALL_ACCESS)
      d.token = win32security.OpenProcessToken(ph,
          win32con.TOKEN_ADJUST_PRIVILEGES|win32con.TOKEN_QUERY)
      d.privileges = win32security.AdjustTokenPrivileges(d.token, 0, d.privileges)

      if win32api.GetLastError():
        dwarn("failed to elevate process privilege")
      else:
        dprint("process privileges elevated")
      return self

    def __exit__(self, *err):
      d = self.__d
      if d.token:
        if d.privileges is not None:
          win32security.AdjustTokenPrivileges(d.token, 0, d.privileges)
        try: win32api.CloseHandle(d.token)
        except Exception, e: dwarn("windows error:", e)
        d.token = None

    def isElevated(self):
      """
      @return  bool  if contain token
      """
      return bool(self.__d.token)

  PROCESS_INJECT_ACCESS = (
      win32con.PROCESS_CREATE_THREAD |
      win32con.PROCESS_QUERY_INFORMATION |
      win32con.PROCESS_VM_OPERATION |
      win32con.PROCESS_VM_WRITE |
      win32con.PROCESS_VM_READ)

  INJECT_TIMEOUT = 3000 # 3 seconds

  def getModuleFunctionAddress(func, module=None):
    """
    @param  func  str
    @param  module  str
    @return  int  address
    """
    return win32api.GetProcAddress(
        win32api.GetModuleHandle(module),
        func)

  # See: inject.cpp from translation aggregator
  def injectfunc1(addr, arg, argsize, pid=0, handle=None, timeout=INJECT_TIMEOUT):
    """Inject function with 1 argument
    Either pid or the process handle should be specified
    @param  addr  LONG  function memory address
    @param  arg  LPVOID
    @param  argsize  int
    @param  pid  LONG
    @param  handle  HANDLE
    @param  timeout  int  msecs
    @return  bool
    """
    dprint("enter: pid = %s" % pid)
    isLocalHandle = False # bool
    if not handle and pid:
      isLocalHandle = True
      try:
        handle = win32api.OpenProcess(PROCESS_INJECT_ACCESS, 0, pid)
        if not handle:
          with SkProcessElevator(SE_DEBUG_PRIVILEGE) as priv:
            if priv.isElevated():
              handle = win32api.OpenProcess(PROCESS_INJECT_ACCESS, 0, pid)
      except Exception, e:
        dwarn("windows error:", e)
    if not handle:
      dprint("exit: error: failed to get process handle")
      return False

    ret = False
    hProcess = handle
    try:
      data = arg
      dataSize = argsize

      # Reserved & commit
      # http://msdn.microsoft.com/en-us/library/windows/desktop/aa366803%28v=vs.85%29.aspx
      # http://msdn.microsoft.com/en-us/library/ms810627.aspx
      remoteData = skwinapi.VirtualAllocEx(
          hProcess, # process
          None,  # __in_opt address
          dataSize,  # data size
          win32con.MEM_RESERVE|win32con.MEM_COMMIT,
          win32con.PAGE_READWRITE)
      if remoteData:
        if skwinapi.WriteProcessMemory(hProcess, remoteData, data, dataSize, None):
          hThread = skwinapi.CreateRemoteThread(
              hProcess,
              None, 0,
              skwinapi.LPTHREAD_START_ROUTINE(addr),
              remoteData,
              0, None)
          if hThread:
            skwinapi.WaitForSingleObject(hThread, timeout)
            win32api.CloseHandle(hThread)
            ret = True
        skwinapi.VirtualFreeEx(hProcess, remoteData, dataSize, win32con.MEM_RELEASE)
    except Exception, e:
      dwarn("windows error:", e)
    if isLocalHandle: # only close the handle if I create it
      try: win32api.CloseHandle(hProcess)
      except Exception, e: dwarn("windows error:", e)
    dprint("exit: ret = ok")
    return ret

  # See: inject.cpp from translation aggregator
  def injectdll(dllpath, pid=0, handle=None, timeout=INJECT_TIMEOUT):
    """Either pid or the process handle should be specified
    @param  dllpath  unicode ABSOLUTE path to dll
    @param  pid  LONG
    @param  handle  HANDLE
    @param  timeout  int  msecs
    @return  bool
    """
    #if not dllpath or not os.path.exists(dllpath):
    #  dwarn("error: dll does not exist")
    #  return False
    dprint("enter: pid = %s" % pid)
    try: dllpath = dllpath.decode('utf8')
    except UnicodeDecodeError:
      dwarn("exit: error: failed to decode dll path to utf8")
      return False
    LOADLIBRARYW = getModuleFunctionAddress('LoadLibraryW', 'kernel32.dll')
    if not LOADLIBRARYW:
      dprint("exit error: cannot find LoadLibraryW from kernel32")
      return False
    data = dllpath
    dataSize = len(dllpath) * 2 + 2 # L'\0'
    ok = injectfunc1(LOADLIBRARYW, data, dataSize, pid=pid, handle=handle, timeout=timeout)
    dprint("exit: ret = ok")
    return ok

  def unloaddll(dllhandle, pid=0, handle=None, timeout=INJECT_TIMEOUT):
    """Either pid or the process handle should be specified
    @param  dllhandle  handle of the injected dll
    @param  pid  LONG
    @param  handle  HANDLE
    @param  timeout  int  msecs
    @return  bool
    """
    dprint("enter: pid = %s" % pid)
    LOADLIBRARYW = getModuleFunctionAddress('LoadLibraryW', 'kernel32.dll')
    if not LOADLIBRARYW:
      dprint("exit error: cannot find LoadLibraryW from kernel32")
      return False
    data = dllhandle
    dataSize = 4 # size of DWORD
    ok = injectfunc1(LOADLIBRARYW, data, dataSize, pid=pid, handle=handle, timeout=timeout)
    dprint("exit: ret = ok")
    return 0

  class _SkProcessCreator: pass
  class SkProcessCreator:
    def __init__(self, path, *args, **kwargs):
      """
      @param  path  unicode
      @param  args  passed to skwin.create_process
      @param  kwargs  passed to skwin.create_process
      """
      d = self.__d = _SkProcessElevator()
      d.path = path
      d.args = args
      d.kwargs = kwargs

    def __enter__(self):
      d = self.__d
      d.hProcess, d.hThread, d.dwProcessId, d.dwThreadId = skwin.create_process(
          d.path, suspended=True, complete=True, *d.args, **d.kwargs)
      dprint("pid = %i" % d.dwProcessId)
      return self

    def __exit__(self, *err):
      d = self.__d
      if d.hThread:
        ok = skwin.resume_thread(d.hThread)
        dprint("resume thread: %s" % ok)

    @property
    def path(self): return self.__d.path
    @property
    def processId(self): return self.__d.dwProcessId
    @property
    def processHandle(self): return self.__d.hProcess
    @property
    def threadId(self): return self.__d.dwThreadId
    @property
    def threadHandle(self): return self.__d.hThread

# EOF

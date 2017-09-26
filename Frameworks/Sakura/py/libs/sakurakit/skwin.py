# coding: utf8
# skwin.py
# 10/5/2012 jichi
# Windows only

import skos
if skos.WIN:
  import os
  from datetime import datetime
  import ctypes
  import pythoncom
  import win32api, win32con, win32gui, win32process
  from win32com.shell import shell, shellcon
  import pywintypes
  from skdebug import dprint, dwarn

  import skwinapi, skpyapi
  import msvcrt

  ## Debug ##

  def get_last_error():
    return win32api.GetLastError()

  ## Global properties ##

  def enable_drop_event(hwnd=None):
    """
    @return  bool

    Always return true on Windows XP.

    See: http://helgeklein.com/blog/2010/03/how-to-enable-drag-and-drop-for-an-elevated-mfc-application-on-vistawindows-7/

    // ChangeWindowMessageFilter
    typedef BOOL (WINAPI *PFN_CHANGEWINDOWMESSAGEFILTER) (UINT, DWORD);

    HMODULE hModule = GetModuleHandle (TEXT(“user32.dll”));
    PFN_CHANGEWINDOWMESSAGEFILTER pfnChangeWindowMessageFilter = (PFN_CHANGEWINDOWMESSAGEFILTER) GetProcAddress (hModule, “ChangeWindowMessageFilter”);

    Then you can use it like this:

    (*pfnChangeWindowMessageFilter) (WM_DROPFILES, MSGFLT_ADD);
    """
    ret = False
    wms = win32con.WM_DROPFILES, win32con.WM_COPYDATA, skwinapi.WM_COPYGLOBALDATA
    try:
      if hwnd:
        # http://answers.microsoft.com/en-us/windows/forum/windows_7-files/file-drag-n-drop-via-wmdropfiles-doesnt-work-in/d172ed8c-1a5b-e011-8dfc-68b599b31bf5?msgId=2e77dbec-495b-e011-8dfc-68b599b31bf5
        ret = not skwinapi.ChangeWindowMessageFilterEx or all(
          skwinapi.ChangeWindowMessageFilterEx(hwnd, it, skwinapi.MSGFLT_ALLOW, 0)
            for it in wms)
      else:
        # http://answers.microsoft.com/en-us/windows/forum/windows_7-files/file-drag-n-drop-via-wmdropfiles-doesnt-work-in/d172ed8c-1a5b-e011-8dfc-68b599b31bf5?msgId=2e77dbec-495b-e011-8dfc-68b599b31bf5
        ret = not skwinapi.ChangeWindowMessageFilter or all(
          skwinapi.ChangeWindowMessageFilter(it, skwinapi.MSGFLT_ADD)
            for it in wms)
    except Exception, e: dwarn(e)
    return ret

  ## Types ##

  def qrect_from_rect(rect):
    left, top, right, bottom = rect
    from PySide.QtCore import QRect
    return QRect(left, top, right - left, bottom - top)

  def hwnd_from_wid(winId):
    """
    @param  winId  QtWidgets.WId as PyObject
    @return HWND as ctypes.voidp

    Used to convert PySide WId to HWND.
    This is a PySide specific issue. In PyQt, WId is the same as HWND
    See: http://www.expobrain.net/2011/02/22/handling-win32-windows-handler-in-pyside/
    """
    return skpyapi.lp_from_pycobj(winId)

  def wid_from_hwnd(hwnd):
    """
    @param  hwnd  ulong
    @return  PyObject
    """
    return skpyapi.pycobj_from_lp(hwnd)

  ## Code page ##

  def get_code_page():
    """
    @return  int
    """
    return skwinapi.GetACP()

  ## Path ##

  def to_short_path(path):
    """
    @param  path  unicode
    @return  unicode or "" if not exists
    """
    try: return win32api.GetShortPathName(path)
    except Exception, e: dwarn(e); return ""

  def to_long_path(path):
    """
    @param  path  unicode
    @return  unicode or "" if not exists
    """
    try: return win32api.GetLongPathName(path)
    except Exception, e: dwarn(e); return ""

  ## Process ##

  def kill_my_process(ret=0):
    # http://snipplr.com/view/60057/
    # http://stackoverflow.com/questions/1533200/qt-kill-current-process/9920452#9920452
    win32api.TerminateProcess(win32api.GetCurrentProcess(), ret)

  def kill_process(pid, ret=0):
    """
    @param  pid  long
    @return  bool
    """
    ret = False
    try:
      # http://snipplr.com/view/60057/
      h = win32api.OpenProcess(win32con.PROCESS_TERMINATE, False, pid)
      if h:
        ret = win32api.TerminateProcess(h, ret)
        win32api.CloseHandle(h)
    except Exception, e: dwarn(e)
    return ret

  def is_process_active(pid):
    """
    @param  pid  long
    @return  bool
    """
    ret = False
    try:
      h = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
      if h:
        status = win32process.GetExitCodeProcess(h)
        ret = status == win32con.STILL_ACTIVE
        win32api.CloseHandle(h)
    except: pass
    #except Exception, e: dwarn(e)
    return ret

  def create_process(path, params=None, environ=None, unicode_environ=True, suspended=False, complete=False):
    """
    @param  path  unicode  path to executable
    @param* params  [unicode param] or None
    @param* environ A dictionary/tuple of string/unicode or None to inherit the current environment.
    @param* unicode_environ  bool  if env contains unicode string
    @param* suspended  bool  whether CREATE_SUSPENDED
    @param* complete  bool  whether return everything
    @return  long pid if not complete else (hProcess, hThread, dwProcessId, dwThreadId)
    """
    assert path, "path does not exist"
    path = path.replace('/', '\\') # to native path
    exe = path
    cmdline = None
    pwd = os.path.dirname(path) or None
    if environ:
      e = os.environ.copy()
      e.update(environ)
      if not unicode_environ:
        environ = e
      else:
        try: environ = {unicode(k):unicode(v) for k,v in e.iteritems()}
        except UnicodeDecodeError, e:
          dwarn(e)
          environ = None

    flags = win32process.CREATE_DEFAULT_ERROR_MODE
    if environ and unicode_environ:
      flags |= win32process.CREATE_UNICODE_ENVIRONMENT

    if suspended:
      flags |= win32process.CREATE_SUSPENDED

    if params:
      args = '" "'.join(params)
      cmdline = u'"%s" "%s"' % (path, args)

    try:
      #si = win32process.STARTUPINFO()
      ##hProcess, hThread, dwProcessId, dwThreadId = win32process.CreateProcess(
      #ret = win32process.CreateProcess(
      #  exe, cmdline,
      #  None, None,   # security attributes
      #  False,        # inherited
      #  flags, environ, pwd,
      #  si) # output
      #return ret if complete else ret[2]

      pi = skwinapi.PROCESS_INFORMATION()
      si = skwinapi.STARTUPINFOW()
      #psi = ctypes.pointer(si)
      #size = ctypes.c_int(ctypes.sizeof(startup_info))
      #ctypes.windll.kernel32.RtlZeroMemory(psi, size)
      if cmdline:
        cmdline = ctypes.create_unicode_buffer(cmdline)
      if environ:
        environ = "\0".join("%s=%s" % (k,v) for k,v in environ.iteritems()) + "\0"
      ok = skwinapi.CreateProcessW(
        exe, cmdline,
        None, None,   # LPSECURITY_ATTRIBUTES lpProcessAttributes, LPSECURITY_ATTRIBUTES lpThreadAttributes,
        False,        # inherited
        flags, environ, pwd,
        ctypes.pointer(si), # output
        ctypes.pointer(pi)) # output
      if complete:
        return (pi.hProcess, pi.hThread, pi.dwProcessId, pi.dwThreadId) if ok else (None, None, 0, 0)
      else:
        return pi.dwProcessId if ok else 0
    #except pywintypes.error, e:
    except Exception, e:
      dwarn(e)
      return (None,None,0,0) if complete else 0

  def resume_thread(hThread):
    """
    @param   hThread  HANDLE
    @return  bool
    """
    try: return win32process.ResumeThread(hThread) >= 0
    #except pywintypes.error, e:
    except Exception, e:
      dwarn(e)
      return False

  def get_process_path(pid):
    """
    @param  pid  long
    @return  unicode or ""
    """
    path = ""
    try:
      h = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ, False, pid)
      if h:
        # This function returns WCHAR
        path = win32process.GetModuleFileNameEx(h, 0)
        win32api.CloseHandle(h)
    except Exception, e: dwarn(e)
    return path
    #return u(path)

  def get_process_name(pid):
    """
    @param  pid  long
    @return  unicode or ""
    """
    # Should use GetModuleBaseName, which is, however, not included in win32process
    path = get_process_path(pid)
    if path:
      path = os.path.basename(path)
    return path

  ## Window ##

  def get_window_class(hwnd):
    """
    @param  hwnd  HWND
    @return  unicode or ""
    @throw  when hwnd is not a window handle
    """
    ret = u""
    bufsz = 256
    buf = msvcrt.malloc(bufsz)
    buf = ctypes.cast(buf, ctypes.c_wchar_p)
    ok = skwinapi.RealGetWindowClass(hwnd, buf, bufsz/2)
    if ok:
      ret = buf.value
    msvcrt.free(buf)
    return ret

  def is_window(hwnd):
    """
    @param  hwnd  HWND
    @return  unicode or ""
    """
    try: return bool(win32gui.IsWindow(hwnd))
    except: return False

  def get_window_parent(hwnd):
    """
    @param  hwnd  HWND
    @return  0
    """
    try: return win32gui.GetParent(hwnd)
    except: return 0

  def is_window_visible(hwnd):
    """
    @param  hwnd  HWND
    @reutrn  bool
    """
    try: return bool(win32gui.IsWindowVisible(hwnd))
    except: return False

  def is_window_minimized(hwnd):
    """
    @param  hwnd  HWND
    @reutrn  bool
    """
    try: return bool(win32gui.IsIconic(hwnd))
    except: return False

  def minimize_window(hwnd):
    """
    @param  hwnd  HWND
    @reutrn  bool
    """
    try: return bool(win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE))
    except: return False

  def get_window_menu(hwnd):
    """
    @param  hwnd  HWND
    @return  ulong
    """
    try: return win32gui.GetMenu(hwnd)
    except: return 0

  def set_window_menu(hwnd, hmenu):
    """
    @param  hwnd  HWND
    @param  hwnd  HWND
    @return  bool
    """
    try: return bool(win32gui.SetMenu(hwnd, hmenu))
    except: return False

  def get_window_rect(hwnd):
    """
    @param  hwnd  HWND
    @return  (left, top, right, bottom) not None
    """
    try: return win32gui.GetWindowRect(hwnd)
    except: return 0, 0, 0, 0

  def window_has_rect(hwnd):
    """
    @param  hwnd  HWND
    @return  bool
    """
    left, top, right, bottom = get_window_rect(hwnd)
    return right > left and bottom > top

  def get_window_size(hwnd):
    """
    @param  hwnd  HWND
    @return  (int width, int height) not None
    """
    left, top, right, bottom = get_window_rect(hwnd)
    return right - left, bottom - top

  def get_content_size(hwnd):
    """
    @param  hwnd  HWND
    @return  (int width, int height)
    """
    try: return win32gui.GetClientRect(hwnd)[2:] # only return bottom and right
    except: return 0, 0

  def get_screen_size():
    """
    @return  int width, int height
    """
    return win32api.GetSystemMetrics(win32con.SM_CXSCREEN), win32api.GetSystemMetrics(win32con.SM_CYSCREEN)

  # See: http://www.msghelp.net/showthread.php?tid=67047&pid=740345
  def is_window_fullscreen(hwnd):
    left, top, right, bottom = get_window_rect(hwnd)
    return (left < 50 and top < 50 and # left top is in the corner
        right - left >= win32api.GetSystemMetrics(win32con.SM_CXSCREEN) and
        bottom - top >= win32api.GetSystemMetrics(win32con.SM_CYSCREEN))

  def window_has_title(hwnd):
    try: bool(win32gui.GetWindowText(hwnd))
    except: return False

  def get_window_text(hwnd, size=256):
    """
    @param  hwnd  HWND
    @param* size  int maximum buffer size
    @return  unicode  not None
    """
    #size = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
    ##buf = ctypes.create_unicode_buffer(size)
    #buf = ctypes.create_string_buffer(size)
    #win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, size, buf)
    #return buf.value.decode('sjis')
    try:
      size = 1 + skwinapi.SendMessageW(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
      buf = ctypes.create_unicode_buffer(size)
      size = skwinapi.SendMessageW(hwnd, win32con.WM_GETTEXT, size, ctypes.addressof(buf))
      if size > 0:
        return buf.value
    except: pass
    #except Exception, e: dwarn(e)
    return ""

  def set_window_text(hwnd, text):
    """
    @param  hwnd  HWND
    @param  text  unicode
    @return  bool

    See: http://stackoverflow.com/questions/1100605/settext-of-textbox-in-external-app-win32-api
    """
    #size = win32gui.SendMessage(hwnd, win32con.WM_GETTEXTLENGTH, 0, 0)
    ##buf = ctypes.create_unicode_buffer(size)
    #buf = ctypes.create_string_buffer(size)
    #win32gui.SendMessage(hwnd, win32con.WM_GETTEXT, size, buf)
    #return buf.value.decode('sjis')
    try:
      buf = ctypes.create_unicode_buffer(text)
      size = skwinapi.SendMessageW(hwnd, win32con.WM_SETTEXT, 0, ctypes.addressof(buf))
      return size > 0
    except: return False

  #def get_window_text(hwnd, size=256):
  #  """
  #  @param  hwnd  HWND
  #  @param* size  int maximum buffer size
  #  @return  unicode  not None
  #  """
  #  text = win32gui.GetWindowText(hwnd)
  #  return u(text)
  #  buf = ctypes.create_unicode_buffer(size)
  #  size = skwinapi.GetWindowTextW(hwnd, buf, size)
  #  return buf.value if size > 0 else ""

  #def get_window_text_a(hwnd):
  #  return win32gui.GetWindowText(hwnd)

  def get_window_process_id(hwnd):
    try: return win32process.GetWindowThreadProcessId(hwnd)[1]
    except: return 0

  def get_window_thread_id(hwnd):
    try: return win32process.GetWindowThreadProcessId(hwnd)[0]
    except: return 0

  def get_window_thread_process_id(hwnd):
    """
    @return  long tid, long pid
    """
    try: return win32process.GetWindowThreadProcessId(hwnd)
    except: return 0, 0

  #def qrect_from_rect(left, top, right, bottom):
  #  return QtCore.QRect(left, top, right - left, bottom - top)

  ## Desktop (current thread) ##

  def get_active_window():
    """Within current thread
    @return  HWND or ?
    """
    return win32gui.GetActiveWindow()

  def set_active_window(hwnd):
    """Within current thread
    @param  hwnd  HWND
    """
    try: return bool(win32gui.SetActiveWindow(hwnd))
    except: return False

  def get_focus_window():
    """Within current thread
    @return  HWND or ?
    """
    return win32gui.GetFocus()

  def set_focus_window(hwnd):
    """Within current thread
    @param  hwnd  HWND
    """
    try: return bool(win32gui.SetFocus(hwnd))
    except: return False

  def get_foreground_window():
    return win32gui.GetForegroundWindow()

  # Doing this will make many game to lose focus
  def set_foreground_window(hwnd):
    """
    @param  hwnd  HWND
    @return  bool
    """
    try: return bool(win32gui.SetForegroundWindow(hwnd))
    except: return False

  def set_top_window(hwnd):
    """
    @param  hwnd  HWND
    @return  bool
    """
    try: return bool(win32gui.BringWindowToTop(hwnd))
    except: return False

  # Not working for inter-thread windows
  # see: http://stackoverflow.com/questions/6381198/get-window-z-order-with-python-windows-extensions
  #def get_top_window(hwnd):
  #  return ?.GetTopWindow(hwnd)

  def get_window_children(hwnd):
    """
    @param  pid long
    @return  [long]
    """
    ret = []
    try:
      win32gui.EnumChildWindows(hwnd,
          lambda wid, lp: lp.append(wid),
          ret)
      return ret
    except: return ret

  def get_child_window(hwnd):
    """
    @param  hwnd  long
    @return  long
    """
    try: return win32gui.GetWindow(hwnd, win32con.GW_CHILD)
    except: return 0

  def get_next_window(hwnd):
    """
    @param  hwnd  long
    @return  long  sibling
    """
    try: return win32gui.GetWindow(hwnd, win32con.GW_HWNDNEXT)
    except: return 0

  def get_previous_window(hwnd):
    """
    @param  hwnd  long
    @return  long  sibling
    """
    try: return win32gui.GetWindow(hwnd, win32con.GW_HWNDPREV)
    except: return 0

  def get_first_window(hwnd):
    """
    @param  hwnd  long
    @return  long  sibling
    """
    try: return win32gui.GetWindow(hwnd, win32con.GW_HWNDFIRST)
    except: return 0

  def get_last_window(hwnd):
    """
    @param  hwnd  long
    @return  long  sibling
    """
    try: return win32gui.GetWindow(hwnd, win32con.GW_HWNDLAST)
    except: return 0

  def get_process_windows(pid):
    """
    @param  pid long
    @return  [long]
    """
    def proc(wid, lp):
      if get_window_process_id(wid) == lp[0]:
        lp[1].append(wid)
    lp = pid, []
    try:
      win32gui.EnumWindows(proc, lp)
      return lp[1]
    except Exception, e:
      dwarn(e)
      return []

  def get_thread_windows(tid):
    """
    @param  tid long
    @return  [long]
    """
    def proc(wid, lp):
      if get_window_thread_id(wid) == lp[0]:
        lp[1].append(wid)
    lp = tid, []
    try:
      win32gui.EnumWindows(proc, lp)
      return lp[1]
    except: return []

  ## App ##

  def set_app_id(name):
    """
    @param  unicode
    @return  bool
    """
    try: return 0 == skwinapi.SetCurrentProcessExplicitAppUserModelID(name)
    except Exception, e:
      dwarn(e)
      return False

  # No idea why this does not work
  #def get_app_id(maxlen=255):
  #  """
  #  @param* maxlen  int
  #  @return  unicode or None
  #  """
  #  try:
  #    buf = ctypes.create_unicode_buffer(maxlen)
  #    if 0 == skwinapi.SetCurrentProcessExplicitAppUserModelID(ctypes.addressof(buf)):
  #      return buf.value
  #  except Exception, e: dwarn(e)

  ## Task bar ##

  # See: http://stackoverflow.com/questions/10085381/how-to-detect-if-autohidden-taskbar-is-visible-or-not
  def get_taskbar_window():
    """
    @return  HWND
    """
    return win32gui.FindWindow("Shell_TrayWnd", "")

  # See: http://stackoverflow.com/questions/10085381/how-to-detect-if-autohidden-taskbar-is-visible-or-not
  # Magic numbers: 4 (vertical) and 2 (horizontal)
  def is_taskbar_visible(hwnd=None):
    """
    @param  hwnd  HWND or None
    @return  bool  if taskbar has a visible size on the desktop
    """
    left, top, right, bottom = get_window_rect(hwnd or get_taskbar_window())
    return (bottom > 4 and right > 2 and
            top > win32api.GetSystemMetrics(win32con.SM_CYSCREEN) - 4 and
            left > win32api.GetSystemMetrics(win32con.SM_CXSCREEN) - 2)

  TASKBAR_EDGES = {
    'b': shellcon.ABE_BOTTOM,
    't': shellcon.ABE_TOP,
    'l': shellcon.ABE_LEFT,
    'r': shellcon.ABE_RIGHT,
  }
  def is_taskbar_autohide(align='b'):
    """
    @param  align  'l', 'r', 't', or 'b'
    """
    abd = skwinapi.APPBARDATA(uEdge = TASKBAR_EDGES.get(align) or shellcon.ABE_BOTTOM)
    abd.cbSize = ctypes.sizeof(abd)
    try: return bool(skwinapi.SHAppBarMessage(
        shellcon.ABM_GETAUTOHIDEBAR, ctypes.byref(abd)))
    except Exception, e:
      dwarn(e)
      return False

  def set_taskbar_autohide(t, align='b', hwnd=None):
    """
    @param  t  bool
    @param  hwnd  HWND
    @param  align  'l', 'r', 't', or 'b'
    @return  bool
    """
    abd = skwinapi.APPBARDATA(
      uEdge=TASKBAR_EDGES.get(align) or shellcon.ABE_BOTTOM,
      hWnd=hwnd or get_taskbar_window(),
      #lParam = win32con.TRUE if t else win32con.FALSE,
      lParam = shellcon.ABS_AUTOHIDE if t else 0, # Always disable ABS_ALWAYSONTOP
    )
    abd.cbSize = ctypes.sizeof(abd)
    try:
      skwinapi.SHAppBarMessage(
          skwinapi.ABM_SETSTATE, ctypes.byref(abd))
      return True
    except Exception, e:
      dwarn(e)
      return False

  def get_taskbar_width(hwnd=None):
    left, top, right, bottom = get_window_rect(
        hwnd or get_taskbar_window())
    return right - left

  def get_taskbar_height(hwnd=None):
    left, top, right, bottom = get_window_rect(
        hwnd or get_taskbar_window())
    return bottom - top

  def get_taskbar_rect(hwnd=None):
    """
    @param  hwnd  HWND
    @return  (left, top, right, bottom) not None
    """
    abd = skwinapi.APPBARDATA(hWnd = hwnd or get_taskbar_window())
    abd.cbSize = ctypes.sizeof(abd)
    try:
      ok = skwinapi.SHAppBarMessage(
          shellcon.ABM_GETTASKBARPOS, ctypes.byref(abd))
      if ok:
        r = abd.rc
        return r.left, r.top, r.right, r.bottom
    except Exception, e: dwarn(e)
    return 0, 0, 0, 0

  ## Screen ##

  # http://www.news2news.com/vfp/?example=374&ver=vcpp
  # http://sourceforge.net/p/pywin32/bugs/480/

  def get_display(id=0):
    """
    @param* id  int
    @return  DisplaySettings or None
    """
    try:
      dev = win32api.EnumDisplayDevices(DevNum=id)
      return win32api.EnumDisplaySettings(dev.DeviceName, win32con.ENUM_CURRENT_SETTINGS)
    except Exception, e: dwarn(e)

  def get_display_resolution(display=None):
    """
    @return  (int w, int h) not None
    """
    try:
      if not display:
        display = get_display()
      return display.PelsWidth, display.PelsHeight
    except Exception, e:
      dwarn(e)
      return 0, 0

  def test_display_resolution(size, display=None):
    """
    @param  size  (int w, int h)
    @return  bool
    """
    try:
      if not display:
        display = get_display()
      #if size == (display.PelsWidth, display.PelsHeight):
      #  return True
      display.PelsWidth, display.PelsHeight = size
      return win32con.DISP_CHANGE_SUCCESSFUL == win32api.ChangeDisplaySettings(display, win32con.CDS_TEST)
    except Exception, e:
      dwarn(e)
      return False

  def set_display_resolution(size, display=None):
    """
    @param  size  (int w, int h)
    @return  bool
    """
    try:
      if not display:
        display = get_display()
      if size == (display.PelsWidth, display.PelsHeight):
        return True
      display.PelsWidth, display.PelsHeight = size
      return win32con.DISP_CHANGE_SUCCESSFUL == win32api.ChangeDisplaySettings(display, 0) # 0 means do change
    except Exception, e:
      dwarn(e)
      return False

  def get_display_resolutions(id=0):
    """
    @param* id  int  device id
    @return  set((int w, int h))
    """
    ret = set()
    try:
      dev = win32api.EnumDisplayDevices(DevNum=id)
      mode = 0
      while True:
        s = win32api.EnumDisplaySettings(dev.DeviceName, mode)
        if not s: break
        ret.add((s.PelsWidth, s.PelsHeight))
        mode += 1
    except: pass
    return ret

  ## Messages ##

  def send_window_message(hwnd, msg, wparam=0, lparam=0):
    """
    @param  hwnd  long
    @param  msg  long
    @return  long
    """
    try: return win32gui.SendMessage(hwnd, msg, wparam, lparam)
    except: return 0

  def post_window_message(hwnd, msg, wparam=0, lparam=0):
    """
    @param  hwnd  long
    @param  msg  long
    @return  bool
    """
    try:
      win32gui.PostMessage(hwnd, msg, wparam, lparam) # return None
      return True
    except: return False

  def send_window_command(hwnd, cmd):
    """
    @param  hwnd  long
    @param  cmd  long
    @return  bool
    """
    try: return 0 == win32gui.SendMessage(hwnd, win32con.WM_COMMAND, cmd, 0)
    except: return False

  def post_window_command(hwnd, cmd):
    """
    @param  hwnd  long
    @param  cmd  long
    @return  bool
    """
    try:
      win32gui.PostMessage(hwnd, win32con.WM_COMMAND, cmd, 0)
      return True
    except: return False

  #def click_window(hwnd):
  #  """
  #  @param  hwnd  long
  #  @return  bool
  #  """
  #  return not send_window_message(hwnd, win32con.BM_CLICK)

  ## Mouse and keyboard ##

  def send_key(hwnd, vk):
    """Synchronize in the same process
    @param  hwnd
    @param  vk  int
    @return  bool
    """
    try:
      err1 = win32gui.SendMessage(hwnd, win32con.WM_KEYDOWN, vk, 0)
      err2 = win32gui.SendMessage(hwnd, win32con.WM_KEYUP, vk, 0)
      return not err1 and not err2
    except: return False

  def send_input_key(vk):
    """
    @param  vk  int
    @return  bool
    """
    try:
      inp = skwinapi.INPUT(
        type = win32con.INPUT_MOUSE,
        ki = skwinapi.KEYBDINPUT(
          wVk = vk,
        ),
      )
      sz = ctypes.sizeof(inp)
      if skwinapi.SendInput(1, inp, sz):
        inp.ki.dwFlags = win32con.KEYEVENTF_KEYUP
        return skwinapi.SendInput(1, inp, sz) > 0
    except Exception, e: dwarn(e)
    return False

  def post_key(hwnd, vk):
    """Async
    @param  hwnd
    @param  vk  int
    @return  bool
    """
    try:
      win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, vk, 0)
      win32api.PostMessage(hwnd, win32con.WM_KEYUP, vk, 0)
      return True
    except: return False

  def send_key_return(hwnd):
    """Async
    @param  hwnd
    @return  bool
    """
    return send_key(hwnd, win32con.VK_RETURN)

  def post_key_return(hwnd):
    """Async
    @param  hwnd
    """
    post_key(hwnd, win32con.VK_RETURN)

  def is_key_pressed(vk):
    """
    @param  vk  int
    @return  bool
    """
    return bool(win32api.GetKeyState(vk) & 0xF0)

  def is_key_toggled(vk):
    """
    @param  vk  int
    @return  bool
    """
    return bool(win32api.GetKeyState(vk) & 0x0F)

  def is_key_shift_pressed(): return is_key_pressed(win32con.VK_SHIFT)
  def is_key_alt_pressed(): return is_key_pressed(win32con.VK_MENU)
  def is_key_control_pressed(): return is_key_pressed(win32con.VK_CONTROL)
  def is_key_win_pressed():
    return is_key_pressed(win32con.VK_LWIN) or is_key_pressed(win32con.VK_RWIN)

  def is_mouse_left_button_pressed(): return is_key_pressed(win32con.VK_LBUTTON)
  def is_mouse_right_button_pressed(): return is_key_pressed(win32con.VK_RBUTTON)
  def is_mouse_middle_button_pressed(): return is_key_pressed(win32con.VK_MBUTTON)

  def get_double_click_time():
    """
    @return  int
    """
    return win32api.GetDoubleClickTime()

  def post_mouse_move(x=0, y=0, relative=True):
    """
    @param  x  int
    @param  y  int
    @param  relative  bool
    """
    fpos = 0 if relative else win32con.MOUSEEVENTF_ABSOLUTE
    win32api.mouse_event(fpos|win32con.MOUSEEVENTF_MOVE, x, y, 0, 0)

  def post_mouse_click(x=0, y=0, button='l', relative=True):
    """
    @param  x  int
    @param  y  int
    @param  button  'l', 'r', or 'm'
    @param  relative  bool
    """
    fpos = 0 if relative else win32con.MOUSEEVENTF_ABSOLUTE

    if button == 'l':
      flags = win32con.MOUSEEVENTF_LEFTDOWN, win32con.MOUSEEVENTF_LEFTUP
    elif button == 'r':
      flags = win32con.MOUSEEVENTF_RIGHTDOWN, win32con.MOUSEEVENTF_RIGHTUP
    elif button == 'm':
      flags = win32con.MOUSEEVENTF_MIDDLEDOWN, win32con.MOUSEEVENTF_MIDDLEUP
    else:
      flags = ()

    for f in flags:
      win32api.mouse_event(fpos|f, x, y, 0, 0)

  def post_mouse_press(x=0, y=0, button='l', relative=True):
    """
    @param  x  int
    @param  y  int
    @param  button  'l', 'r', or 'm'
    @param  relative  bool
    """
    fpos = 0 if relative else win32con.MOUSEEVENTF_ABSOLUTE

    if button == 'l':
      f = win32con.MOUSEEVENTF_LEFTDOWN
    elif button == 'r':
      f = win32con.MOUSEEVENTF_RIGHTDOWN
    elif button == 'm':
      f = win32con.MOUSEEVENTF_MIDDLEDOWN
    else:
      f = 0
    win32api.mouse_event(fpos|f, x, y, 0, 0)

  def post_mouse_release(x=0, y=0, button='l', relative=True):
    """
    @param  x  int
    @param  y  int
    @param  button  'l', 'r', or 'm'
    @param  relative  bool
    """
    fpos = 0 if relative else win32con.MOUSEEVENTF_ABSOLUTE

    if button == 'l':
      f = win32con.MOUSEEVENTF_LEFTUP
    elif button == 'r':
      f = win32con.MOUSEEVENTF_RIGHTUP
    elif button == 'm':
      f = win32con.MOUSEEVENTF_MIDDLEUP
    else:
      f = 0
    win32api.mouse_event(fpos|f, x, y, 0, 0)

  def get_mouse_pos():
    """
    @return  (int x, int y)  global pos
    """
    return win32api.GetCursorPos()

  def get_window_at(x, y):
    """
    @param  x  int not float
    @param  y  int not float
    @return  hwnd
    """
    return win32gui.WindowFromPoint((x, y))

  ## Shell ##

  def trash_file(path, hwnd=0):
    """
    @param  path  str or unicode
    @param  hwnd  HWND or 0
    @return  bool  if succeed
    """
    op = skwinapi.SHFILEOPSTRUCTW(
      wFunc = shellcon.FO_DELETE,
      hwnd = hwnd,
      pFrom = ctypes.wintypes.LPCWSTR(path + '\0'),
      pTo = None,
      fAnyOperationsAborted = 0,
      lpszProgressTitle = None,
      fFlags = shellcon.FOF_ALLOWUNDO|shellcon.FOF_NOCONFIRMATION|shellcon.FOF_NOERRORUI|shellcon.FOF_SILENT
    )
    err = skwinapi.SHFileOperationW(ctypes.byref(op))
    return err == 0

  ## Datetime ##

  #def systemtime_from_unixtime(timestamp):
  #  if not timestamp:
  #    return skwinapi.SYSTEMTIME()
  #  dt = datetime.fromtimestamp(timestamp)
  #  return skwinapi.SYSTEMTIME(
  #    dt.year,
  #    dt.month,
  #    dt.weekday(),
  #    dt.day,
  #    dt.hour,
  #    dt.minute,
  #    dt.second,
  #    0, # unixtime does not have milliseconds
  #  )

  def get_time_zone_info():
    """
    @return (int bias, unicode standardName, tuple standardTime, int standardBias,
                       unicode daylightName, tuple daylightTime, int daylightBias)
    """
    # ret: int daylight offset, tz info
    # param: True  use time tuple instead
    _, tzi = win32api.GetTimeZoneInformation(True)
    return tzi

  def set_time_zone_info(tzi):
    """
    @param  (int bias, unicode standardName, tuple standardTime, int standardBias,
                       unicode daylightName, tuple daylightTime, int daylightBias)
    @return  bool  if ok
    """
    value = skwinapi.TIME_ZONE_INFORMATION(
      tzi[0],
      tzi[1], skwinapi.SYSTEMTIME(*tzi[2]), tzi[3],
      tzi[4], skwinapi.SYSTEMTIME(*tzi[5]), tzi[6],
    )
    ok = skwinapi.SetTimeZoneInformation(ctypes.byref(value))
    return bool(ok)

  def set_time_zone_to_jst():
    """
    @return  bool  if succeeded
    """
    return set_time_zone_info(skwinapi.TZI_ASIA_JAPAN)

  ## Files ##

  def set_file_hidden(path): # str -> bool
    try: bool(win32api.SetFileAttributes(path, win32con.FILE_ATTRIBUTE_HIDDEN))
    except: return false

  def set_file_readonly(path): # str -> bool
    try: bool(win32api.SetFileAttributes(path, win32con.FILE_ATTRIBUTE_READONLY))
    except: return false

  def set_file_normal(path): # str -> bool
    try: bool(win32api.SetFileAttributes(path, win32con.FILE_ATTRIBUTE_READONLY))
    except: return False

  ## Launch ##

  def open_cpl(path): # unicode -> bool
    # http://stackoverflow.com/questions/19508268/how-to-open-control-panel-in-python-using-win32-extension
    try:
      import skproc
      return bool(skproc.detachgui(['control.exe', path]))
    except Exception, e:
      dwarn(e)
      return False

  def install_msi_admin(path): # unicode -> bool
    try: return elevate('msiexec.exe', ('/i', path))
    except Exception, e:
      dwarn(e)
      return False

  def install_msi_normal(path): # unicode -> bool
    try:
      import skproc
      return bool(skproc.detachgui(['msiexec.exe', '/i', path]))
    except Exception, e:
      dwarn(e)
      return False

  def install_msi(path, admin=False): # unicode -> bool
    if admin:
      import skwinsec
      if skwinsec.is_elevated() == False:
        return install_msi_admin(path)
    return install_msi_normal(path)

  ## Shell ##

  def create_com_client(name): # str -> client or None
    import win32com.client
    try: return win32com.client.Dispatch(name)
    except Exception, e: dwarn(e)

  WSH = None
  def wsh():
    """
    @return  WScript client or None
    """
    global WSH
    if not WSH:
      WSH = create_com_client('WScript.Shell')
    return WSH

  SHELL = None
  def shell():
    """
    @return  Shell.Application client or None
    """
    global SHELL
    if not SHELL:
      SHELL = create_com_client('Shell.Application')
    return SHELL

  # See: elevate.vbs
  def elevate(path, args): # str, str
    try:
      quoted = ' '.join(("%s" % it for it in args))
      shell().ShellExecute(path, quoted, '', 'runas')
      return True
    except Exception, e:
      dwarn(e)
      return False

  # http://stackoverflow.com/questions/397125/reading-the-target-of-a-lnk-file-in-python
  def get_link_target_wsh(path):
    """
    @param  path  unicode  shortcut file location
    Wreturn  unicode or None

    Note: though returning unicode, the characters are illegal.
    """
    try: return wsh().CreateShortcut(path).Targetpath
    #except Exception, e: dwarn(e)
    except Exception, e: dwarn(e)

  # See: http://mail.python.org/pipermail/python-win32/2011-March/011281.html
  # See: http://timgolden.me.uk/pywin32-docs/win32com.shell_and_Windows_Shell_Links.html
  def get_link_target_com(path):
    """
    @param  path  unicode  shortcut file location
    Wreturn  str not unicode, or None
    """
    #from win32com.shell import shell #, shellcon
    try:
      link = pythoncom.CoCreateInstance(
        shell.CLSID_ShellLink,
        None,
        pythoncom.CLSCTX_INPROC_SERVER,
        shell.IID_IShellLink
      )
      link.QueryInterface(pythoncom.IID_IPersistFile).Load(path)
      #ret, _ = link.GetPath(shell.SLGP_UNCPRIORITY)
      ret, _ = link.GetPath(0)
      #return u(ret)
      return ret
    #except Exception, e: dwarn(e)
    except: pass

  get_link_target = get_link_target_com

if __name__ == '__main__':
  path = ur"D:\Library\Desktop\GalGame\「虜ノ契」.lnk"
  print os.path.exists(path)
  print get_link_target(path)

# It is really weird that the following lien would crash LEC pars ...
#  print '?' in get_link_target(path)

# EOF

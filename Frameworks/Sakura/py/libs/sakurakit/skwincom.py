# coding: utf8
# skwincom.py
# 4/1/2013 jichi
# Windows only

import skos
if skos.WIN:
  import pythoncom # Automatically invoke OleInitialize

  def coinit(threading=None):
    """
    @param  threading  bool or None
    """
    if threading is None: # The same as STA
      pythoncom.CoInitialize() # this function returns None
    elif threading: # Multi-thread apartment (MTA)
      pythoncom.CoInitializeEx(pythoncom.COINIT_MULTITHREADED)
    else: # Single thread apartment (STA)
      pythoncom.CoInitializeEx(pythoncom.COINIT_APARTMENTTHREADED)

  def couninit():
    pythoncom.CoUninitialize()

  class SkCoInitializer:
    def __init__(self, threading=None):
      self.threading = threading # bool or None
    def __enter__(self):
      coinit(self.threading)
      return self
    def __exit__(self, *err):
      couninit()

  #class SkCoProcessInitializer:
  #  def __enter__(self): pythoncom.OleInitialize()
  #  def __exit__(self, *err): pythoncom.OleUninitialize()

else: # On mac

  class SkCoInitializer:
    def __init__(self, threading=None): self.threading = threading
    def __enter__(self): pass
    def __exit__(self, *err): pass

# EOF

# Given the following, no need to bother CoInitialize/CoUninitialize for single-thread app
# Using OleInitialize/OleUninitialize is enough for process-level managerment
# Ole.. is for current process, while Co... is for current thread.
#
# http://msdn.microsoft.com/en-us/library/windows/desktop/ms690134%28v=vs.85%29.aspx
# Typically, the COM library is initialized on an apartment only once. Subsequent calls will succeed, as long as they do not attempt to change the concurrency model of the apartment, but will return S_FALSE. To close the COM library gracefully, each successful call to OleInitialize, including those that return S_FALSE, must be balanced by a corresponding call to OleUninitialize.
# http://msdn.microsoft.com/en-us/library/windows/desktop/ms688715%28v=vs.85%29.aspx
# A thread must call CoUninitialize once for each successful call it has made to the CoInitialize or CoInitializeEx function, including any call that returns S_FALSE. Only the CoUninitialize call corresponding to the CoInitialize or CoInitializeEx call that initialized the library can close it.
  #OLE_INIT = False
  #def ole_initialized(): return OLE_INIT

  #def ole_initialize():
  #  # Example: http://mail.python.org/pipermail/python-list/2010-January/564424.html
  #  global OLE_INIT
  #  if not OLE_INIT:
  #    pythoncom.OleInitialize()
  #    OLE_INIT = True

  #def ole_uninitialize():
  #  global OLE_INIT
  #  if OLE_INIT:
  #    #pythoncom.OleUninitialize()
  #    pythoncom.CoUninitialize()
  #    OLE_INIT = False


# coding: utf8
# curtheme.py
# 10/6/2012 jichi

#_PYTHON_PATH = os.path.dirname(sys.executable)
#_CURSOR_PATH = os.path.abspath(_PYTHON_PATH + "/../Sakura/res/cursors")

#def beep():
#  print '\a'
#  #from Qt5.QtWidgets import QApplication
#  #QApplication.beep()

# Mouse theme

from sakurakit import skos
if skos.WIN:
  from sakurakit.skdebug import dprint

  OS_CURSORS = {} # {IDC:HCURSOR}

  import atexit
  import win32api, win32con
  from sakurakit import skwinapi

  def load():
    import config
    for idc_name, curfile in config.CURSOR_LOCATIONS.iteritems():
      idc = getattr(win32con, idc_name)
      assert idc, "invalid idc name"
      OS_CURSORS[idc] = skwinapi.CopyCursor(
          win32api.LoadCursor(0, idc))

      hcur = skwinapi.LoadCursorFromFileW(curfile)
      if hcur:
        skwinapi.SetSystemCursor(hcur, idc)
    dprint("pass")

  def unload():
    if OS_CURSORS:
      for idc, hcur in OS_CURSORS.iteritems():
        skwinapi.SetSystemCursor(hcur, idc)
      OS_CURSORS.clear()
      dprint("pass")

  #import atexit
  #atexit.register(unload)
  from PySide.QtCore import QCoreApplication
  QCoreApplication.instance().aboutToQuit.connect(unload)

else:
  def load(): pass
  def unload(): pass

# EOF

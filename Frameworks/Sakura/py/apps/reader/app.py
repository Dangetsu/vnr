# coding: utf8
# app.py
# 10/8/2012 jichi

__all__ = 'Application',

from PySide.QtCore import QTranslator, QObject
from Qt5.QtWidgets import QApplication
from sakurakit import skos
from sakurakit.skdebug import dprint, dwarn, derror
from mytr import mytr_
import config, rc, settings

#if skos.WIN:
#  from win32con import WM_QUIT, WM_ENDSESSION, WM_QUERYENDSESSION

def ignoreWindowsExceptions():
  from sakurakit import skwinapi
  @skwinapi.LPTOP_LEVEL_EXCEPTION_FILTER
  def exceptionFilter(e):
    """
    LONG WINAPI exceptionFilter(PEXCEPTION_POINTERS e)
    """
    derror("Application exception")

  skwinapi.SetUnhandledExceptionFilter(exceptionFilter)
  dprint("pass")

#class _Application:
#
#  def __init__(self, q):
#    q.aboutToQuit.connect(self._onAboutToQuit)
#
#  def _onAboutToQuit(self):
#    dprint("pass")

class Application(QApplication):
  def __init__(self, argv):
    super(Application, self).__init__(argv)

    self.setApplicationName(mytr_("Visual Novel Reader"))
    self.setApplicationVersion(str(config.VERSION_TIMESTAMP))
    self.setOrganizationName(config.VERSION_ORGANIZATION)
    self.setOrganizationDomain(config.VERSION_DOMAIN)
    self.setWindowIcon(rc.icon('logo-reader'))

    #if skos.WIN:
    #  ignoreWindowsExceptions()

    dprint("pass")

  def setFontFamily(self, family):
    dprint(family)
    font = self.font()
    font.setFamily(family)
    self.setFont(font)

  # FIXME: wParam does not exist in PySide MSG
  # Bug: https://bugreports.qt-project.org/browse/PYSIDE-84
  #def winEventFilter(self, msg):
  #  """
  #  @param  msg  PySide.QtCore.MSG
  #  @return  bool
  #  """
  #  # See: http://stackoverflow.com/questions/19195935/how-to-detect-windows-shutdown-or-logoff-in-qt
  #  if msg.wParam in (WM_QUIT, WM_ENDSESSION, WM_QUERYENDSESSION):
  #    dprint("quit")
  #  return super(Application, self).winEventFilter(msg)

  def notify(self, receiver, event):
    """@reimp @protected
    virtual bool notify(QObject *receiver, QEvent *e)

    See: http://www.02.246.ne.jp/~torutk/cxx/qt/QtMemo.html
    """
    try:
      if isinstance(receiver, QObject): # receiver could be QCursor. Only notify QObject
        return super(Application, self).notify(receiver, event)
    except KeyboardInterrupt, e:
      derror(e)
    except Exception, e:
      derror(e)
      if skos.WIN:
        import win32api, win32con
        win32api.MessageBox(None, """\
I am sorry that VNR got an unexpected error m(_ _)m
I am not sure what is happening, and whether you have to restart VNR T_T
Feel free to complain to me (annotcloud@gmail.com) if this error keeps bothering you.

ERROR MESSAGE BEGIN
%s
ERROR MESSAGE END""" % e,
            "VNR Error",
            win32con.MB_OK|win32con.MB_ICONERROR)
    return True

  @staticmethod
  def applicationLocale():
    #lang = settings.global_().userLanguage()
    lang = settings.global_().uiLanguage()
    locale = config.language2locale(lang)
    return locale

  def loadTranslations(self):
    locale = self.applicationLocale()
    #if locale in config.TR_LOCALES:
    dprint("loading translation for %s" % locale)

    t = QTranslator(self)
    ok = t.load('qt_%s' % locale, config.QT_TRANSLATIONS_LOCATION)
    #assert ok, "failed to load qt translation"
    if ok:
      self.installTranslator(t)
    else:
      location = config.QT_TRANSLATIONS_LOCATION
      dprint("cannot find translation at %s" % location)

    for location in config.TR_LOCATIONS:
      t = QTranslator(self)
      ok = t.load(locale, location)
      #assert ok, "failed to load translation"
      if ok:
        self.installTranslator(t)
      else:
        dprint("cannot find translation at %s" % location)

# EOF

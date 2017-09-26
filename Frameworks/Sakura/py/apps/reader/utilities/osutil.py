# coding: utf8
# osutil.py
# 10/14/2012 jichi

import os, datetime
from PySide import QtCore
from Qt5.QtWidgets import QDesktopServices
from sakurakit import skclip, skos, skwin
from sakurakit.skclass import memoized
from sakurakit.skdebug import dprint, dwarn
#from sakurakit.skqml import QmlObject
from mytr import my, mytr_
import features, growl, proxy

def get_relpath(path): # unicode -> unicode
  return os.path.relpath(os.path.abspath(path), os.path.abspath(os.getcwd())) # Does not work on Wine
  #return os.path.relpath(os.path.abspath(path), os.path.abspath(QtCore.QCoreApplication.applicationDirPath()))

def _clip(text):
  """
  @param  text
  """
  try: skclip.settext(text)
  except Exception, e: dwarn(e)

def path_url(path):
  """
  @param  path  unicode
  @return  unicode
  """
  return QtCore.QUrl.fromLocalFile(path).toString()

def url_path(url):
  """
  @param  url  unicode
  @return  unicode
  """
  ret = QtCore.QUrl(url).toLocalFile()
  ret = QtCore.QDir.toNativeSeparators(ret)
  return ret

def open_location(path):
  """
  @param  path  str  path to local file
  @return  if succeed
  """
  #dprint("path = %s" % path)
  dprint(path)
  _clip(path)
  try: path = os.path.abspath(path)
  except: pass
  return QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(path))

def open_url(url):
  """
  @param  url  str or QUrl
  @return  if succeed

  See: http://pythonconquerstheuniverse.wordpress.com/2010/10/16/how-to-open-a-web-browser-from-python/
  """
  # jichi 9/26/2013 FIXME: Neither QDesktopServices nor webbrowser work on wine
  # More than that, they will hang VNR ><
  #dprint("url = %s" % url)
  dprint(url)
  if isinstance(url, QtCore.QUrl):
    t = url.toString()
    _clip(t)
  else:
    t = url
    _clip(t)
  if proxy.manager().isBlockedUrl(t):
    growl.msg(my.tr("Open in VNR's browser for sites that might be blocked"))
    from scripts import browser
    browser.open(t)
  elif features.WINE:
    dwarn("disabled under wine") # this will hang several seconds on wine
    #if isinstance(url, QtCore.QUrl):
    #  url = url.toString()
    #os.startfile(url)
  else:
    growl.msg(mytr_("Open in external browser"))
    QDesktopServices.openUrl(url)
  #if isinstance(url, QtCore.QUrl):
  #  url = url.toString()
  #import webbrowser
  #return webbrowser.open(url)

def normalize_path(path):
  """Return unicode unix-format path
  @param  path  str or None
  @return  unicode or ""
  """
  return QtCore.QDir.fromNativeSeparators(path).lower() if path else ""

def backup_file(path, fmt="%Y-%m-%d", now=None):
  try:
    base, ext = os.path.splitext(path)
    if now is None:
      now = datetime.datetime.now()
    bakfile = "%s.%s%s" % (base, now.strftime(fmt), ext)

    dprint("from: %s" % path)
    dprint("to: %s" % bakfile)
    if QtCore.QFile.exists(bakfile) and QtCore.QFile.exists(path):
      dprint("overwrite previous backup")
      QtCore.QFile.remove(bakfile)
    ok = QtCore.QFile.copy(path, bakfile)
    if not ok:
      dwarn("warning: backup failed")

  except AttributeError:
    dwarn("warning: failed to backup file '%s'" % path)

class _BackupFileManager: pass
#@QmlObject
class BackupFileManager(QtCore.QObject):
  def __init__(self, parent=None):
    super(BackupFileManager, self).__init__(parent)
    d = self.__d = _BackupFileManager()
    d.files = {} # files indexed by its normalized path

    QtCore.QCoreApplication.aboutToQuit.connect(self.backupNow)

  def backupLater(self, path):
    if path:
      self.__d.files[normalize_path(path)] = path

  def backupNow(self):
    map(backup_file, self.__d.files.itervalues())
    self.__d.files = {}

@memoized
def backup_file_manager(): return BackupFileManager()
def backup_file_later(path): backup_file_manager().backupLater(path)

# EOF

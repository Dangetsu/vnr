# coding: utf8
# main.py
# 11/29/2013 jichi

__all__ = 'MainObject',

import os
from PySide.QtCore import Qt, QCoreApplication, QObject
from sakurakit import skevents, skfileio
from sakurakit.skclass import Q_Q, memoizedproperty
from sakurakit.skcontainer import uniquelist
from sakurakit.skdebug import dprint, dwarn
from sakurakit import skos
from tr import my
import growl

_MAX_RETRIES = 7 # maximum retry count

def _is_good_video(path):
  """
  @param  path  unicode
  @return  bool
  """
  return bool(path) and skfileio.filesize(path) > 1000 # at least 1K

# MainObject private data
@Q_Q
class _MainObject(object):
  def __init__(self):
    self._quited = False
    self.location = '' # unicode
    self.vids = [] # [str]
    self._vidCount = 0 # int
    self._cvid = '' # str  current VID
    self._cpath = '' # unicode  current path
    self._retryCount = 0 # retry count
    self._failedVids = [] # [str]
    self._visitedUrls = set() # downloaded urls

  def setLocation(self, v):
    self.location = v
    if v and not os.path.exists(v):
      try: os.makedirs(v)
      except OSError:
        dwarn("warning: failed to create directory: %s" % v)
        self.quit()

  def setVideoIds(self, l):
    self.vids = l
    self._vidCount = len(l)

  def createLog(self):
    dprint("enter")
    from datetime import datetime
    path = os.path.join(self.location, 'URL.txt')
    now = datetime.now()
    ts = now.strftime("%Y-%m-%d %H:%M")
    lines = ["Created by by VNR at %s" % ts]
    lines.extend(self.vids)
    try:
      with open(path, 'w') as f:
        f.write('\n'.join(lines))
    except IOError, e: dwarn(e)
    dprint("leave")

  @memoizedproperty
  def window(self):
    import window
    ret = window.MainWindow()
    ret.closeRequested.connect(self._confirmQuit, Qt.QueuedConnection)

    g = self.growlBean
    g.message.connect(ret.appendMessage)
    g.warning.connect(ret.appendWarning)
    g.error.connect(ret.appendError)
    g.notification.connect(ret.appendNotification)
    g.pageBreak.connect(ret.appendNewLine)
    return ret

  @memoizedproperty
  def growlBean(self):
    from growl import GrowlBean
    return GrowlBean(self.q)

  @memoizedproperty
  def solver(self):
    from clipconv import YouTubeSolver
    ret = YouTubeSolver(self.q)
    ret.setWebView(self.window.webView())
    # This could crash?
    #ret.setParentWidget(self.window)
    ret.urlSolved.connect(self._save)
    ret.aborted.connect(self._retry)

    qApp = QCoreApplication.instance()
    qApp.aboutToQuit.connect(ret.stop)
    return ret

  @property
  def networkAccessManager(self):
    return self.solver.networkAccessManager()

  @memoizedproperty
  def downloader(self):
    from dl import Downloader
    ret = Downloader(self.q, self.networkAccessManager)
    ret.finished.connect(self._continue, Qt.QueuedConnection)
    ret.aborted.connect(self._retry)

    qApp = QCoreApplication.instance()
    qApp.aboutToQuit.connect(ret.abort)
    return ret

  def quit(self):
    if not self._quited:
      self._quited = True
      qApp = QCoreApplication.instance()
      qApp.quit()

  def _confirmQuit(self):
    import prompt
    if prompt.confirmQuit():
      self.quit()

  def _save(self, url, name):
    """
    @param  url  QString
    @param  name  QString
    """
    if url in self._visitedUrls:
      growl.warn(("[main] %s: %s" % (my.tr("pass"), url)))
    else:
      self._visitedUrls.add(url)
      growl.notify("[main] %s: %s" % (my.tr("download"), name))
      growl.notify("[main] %s: %s" % (my.tr("url"), url))
      self._cpath = os.path.join(self.location, name)
      self.downloader.get(url, self._cpath)

  def start(self):
    """Start downloading vids """
    growl.msg("[main] %s: %s" % (my.tr("directory to save"), self.location))
    growl.msg("[main] %s (%s): %s" % (my.tr("vids to download"),
      len(self.vids), ", ".join(self.vids)))
    self._next()

  def _retry(self):
    if not self._quited:
      if self._cvid:
        self._retryCount += 1
        if self._retryCount > _MAX_RETRIES:
          growl.error("[main] %s (%i/%i)" % (my.tr("too many retries"), _MAX_RETRIES, _MAX_RETRIES))
          self._failedVids.append(self._cvid)
        else:
          growl.warn("[main] %s (%i/%i)" % (my.tr("retry"), self._retryCount, _MAX_RETRIES))
          self.vids.insert(0, self._cvid)
      self._next()

  def _continue(self):
    if self._cvid and self._cpath and not _is_good_video(self._cpath):
      if os.path.exists(self._cpath):
        growl.warn("[main] %s: %s" % (my.tr("remove failed file"), self._cpath))
        skfileio.removefile(self._cpath)
      self._retry()
    else:
      self._next()

  def _next(self):
    """Download first vids"""
    dprint("enter: vids count = %i" % len(self.vids))
    if self.vids:
      growl.pageBreak()
      self._cvid = self.vids.pop(0)
      index = self._vidCount - len(self.vids)
      growl.notify("[main] %s (%i/%i): %s" %
          (my.tr("processing"), index, self._vidCount, self._cvid))
      self.solver.solve(self._cvid)
    else:
      self._finish()
    dprint("leave")

  def _finish(self):
    if self._failedVids:
      growl.pageBreak()
      growl.error("[main] %s: %s" % (my.tr("failed videos"), ", ".join(self._failedVids)))
    else:
      skos.open_location(self.location)
      self.quit()

class MainObject(QObject):
  """Root of most objects"""

  # Supposed to be top-level, no parent allowed
  def __init__(self, parent=None):
    dprint('enter')
    super(MainObject, self).__init__(parent)
    self.__d = _MainObject(self)
    dprint('leave')

  def run(self, args):
    """Starting point for the entire app
    @param  args  [unicode]
    """
    dprint("enter: args =", args)
    args = args[2:] # remove the leading python exe and the script name

    d = self.__d
    args = [it for it in args if not it.startswith('--')]
    if len(args) < 2:
      dwarn("missing arguments")
      d.quit()
    else:
      d.setLocation(args[0])
      d.setVideoIds(uniquelist(args[1:]))
      if len(d.vids) > 1:
        d.createLog()
      dprint("show root window")

      #d.window.debugRequested.connect(d.solver.show)

      d.window.show()

      skevents.runlater(d.start)

    dprint("leave")

# EOF

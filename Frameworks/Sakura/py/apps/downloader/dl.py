# coding: utf8
# main.py
# 11/29/2013 jichi

__all__ = 'Downloader',

if __name__ == '__main__': # DEBUG
  import debug
  debug.initenv()

import os
from PySide.QtCore import Signal, QObject, QUrl
from PySide.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from sakurakit import skdatetime, skfileio
from sakurakit.skclass import Q_Q
from sakurakit.skdebug import dprint, dwarn
from tr import my
import growl

_TMP_SUFFIX = '.download'
_CHUNK_SIZE = 8192 # I/O chunk size

_PROGRESS_INTERVAL = 1 # 1 second

class Downloader(QObject):

  def __init__(self, parent=None, nam=None):
    """
    @param* parent  QObject
    @param* nam  QNetworkAccessManager
    """
    super(Downloader, self).__init__(parent)
    self.__d = _Downloader(self, nam)

  started = Signal()
  finished = Signal()
  aborted = Signal()
  progress = Signal(long, long) # qint64 bytesReceived, qint64 bytesTotal

  def networkAccessManager(self): return self.__d.nam
  def setNetworkAccessManager(self, v): self.__d.nam = v

  def isRunning(self): return bool(self.__d.file)

  def stop(self): self.__d.stop()
  def abort(self): self.__d.abort()

  def get(self, url, path):
    """
    @param  url  unicode or QUrl
    @param  unicode  path
    @return  bool  whether succeeded
    """
    dprint('enter:', url)
    d = self.__d
    d.stop()
    if d.openFile(path):
      if not isinstance(url, QUrl):
        url = QUrl(url)
      d.request = QNetworkRequest(url)
      ok = d.start()
    else:
      ok = False
    dprint('leave: ret = %s' % ok)
    return ok

@Q_Q
class _Downloader:
  def __init__(self, q, nam):
    self.nam = nam or QNetworkAccessManager(q)
    self.request = None # QNetworkRequest or None
    self.reply = None # QNetworkReply or None
    self.path = '' # unicode
    self.file = None # python file object
    self._progressTime = 0 # long
    self._progressBytes = 0 # long

  @property
  def tmpPath(self):
    """
    @return  unicode
    """
    return self.path + _TMP_SUFFIX if self.path else ''

  # Start/stop download

  def stop(self):
    dprint('enter')
    if self.file:
      self.closeFile()
    self._removeTmpFile()
    if self.reply:
      if not self.reply.isFinished() and self.reply.error() == QNetworkReply.NoError:
        dwarn("abort reply")
        self.reply.abort()
      #self.reply.deleteLater()
      self.reply = None
    if self.request:
      self.request = None
    self._progressTime = 0
    self._progressBytes = 0
    dprint('leave')

  def start(self):
    self.reply = self.nam.get(self.request)
    self.reply.error.connect(self.abort)
    self.reply.readyRead.connect(self.writeFile)
    self.reply.finished.connect(self.finish)
    self.reply.downloadProgress.connect(self._progress) # FIXME: cannot directly connect to q
    growl.notify("[download] %s" % my.tr("start"))
    self.q.started.emit()
    dprint('pass')
    return True

  def _progress(self, availableBytes, totalBytes):
    """
    @param  availableBytes  long
    @param  totalBytes  long
    """
    if totalBytes:
      now = skdatetime.current_unixtime()
      if availableBytes == totalBytes or now > self._progressTime + _PROGRESS_INTERVAL:
        percent = '{0:.1f}%'.format(100 * availableBytes/float(totalBytes))
        eta = ''
        if self._progressTime and now != self._progressTime:
          kbps = (availableBytes - self._progressBytes) / (1024.0 * (now - self._progressTime)) # KBps
          speed = ' {0:.1f}KBps'.format(kbps) # leading space
          if kbps:
            seconds = (totalBytes - availableBytes) / (kbps * 1024.0)
            if seconds < 90:
              eta = ' ETA {0:.1f}sec'.format(seconds) # leading space
            else:
              minutes = seconds / 60.0
              eta = ' ETA {0:.1f}min'.format(minutes) # leading space
        else:
          speed = ""
        msg = "%s %i/%i%s%s" % (percent, availableBytes, totalBytes, speed, eta)
        dprint(msg)
        growl.msg("[download] %s: %s" % (my.tr("progress"), msg))
        self.q.progress.emit(availableBytes, totalBytes)
        self._progressTime = now
        self._progressBytes = availableBytes

  def abort(self):
    dprint('enter')
    msg = self.reply.errorString() if self.reply else ''
    self._removeTmpFile()
    self.stop()
    self.q.aborted.emit()
    growl.warn("[download] %s: %s" % (my.tr("error"), msg or my.tr("unknown error")))
    growl.warn("[download] %s" % my.tr("abort"))
    dprint('leave:', msg)

  def finish(self):
    dprint('enter')
    self.writeFile() # write for the last chunk
    self.stop()
    growl.notify("[download] %s" % my.tr("clean up"))
    self.q.finished.emit()
    dprint('leave')

  # File IO

  def _removeTmpFile(self):
    path = self.tmpPath
    if path and os.path.exists(path):
      skfileio.removefile(path)

  def openFile(self, path):
    """
    @param  path  unicode
    @return  bool
    """
    dprint('enter:', path)
    growl.msg("[download] %s: %s" % (my.tr("create file"), path))
    self.path = path
    try:
      self.file = open(self.tmpPath, 'wb')
      ok = True
    except IOError, e:
      growl.error("[download] %s: %s" % (my.tr("failed to create file"), path))
      dwarn(e)
      ok = False
    dprint('leave: ret = %s' % ok)
    return ok

  def closeFile(self):
    """
    @return  bool
    """
    dprint('enter')
    ok = False
    if self.file:
      growl.msg("[download] %s" % my.tr("closing file"))
      try:
        self.file.close()
        if self.path and os.path.exists(self.path):
          growl.notify("[download] %s: %s" % (my.tr("remove existing file"), self.path))
          dprint("remove existing file:", self.path)
          skfileio.trashfile(self.path)
        ok = skfileio.rename(self.tmpPath, self.path)
      except IOError, e: dwarn(e)
      self.file = None
      if not ok:
        growl.msg("[download] %s: %s" % (my.tr("failed to close file"), self.path))
    dprint('leave: ret = %s' % ok)
    return ok

  def writeFile(self):
    """
    @return  bool
    """
    if self.file and self.reply and self.reply.bytesAvailable() and self.reply.error() == QNetworkReply.NoError:
      try:
        data = self.reply.read(_CHUNK_SIZE)
        while data:
          self.file.write(data)
          data = self.reply.read(_CHUNK_SIZE)
        return True
      except IOError, e: dwarn(e)
    return False

if __name__ == '__main__':
  a = debug.app()
  dl = Downloader()
  url = 'http://www.google.com'
  path = 'tmp.html'

  #url = 'http://srv53.clipconverter.cc/download/z7eVcKN0t4Kwam1om5yVcW2s26SqaGy0l5abbXFgnGprabV70szTe6ie3pemp56q/'
  #path = 'tmp.mp4'

  dl.get(url, path)
  for sig in dl.finished, dl.aborted:
    sig.connect(a.quit)
  a.exec_()

# EOF

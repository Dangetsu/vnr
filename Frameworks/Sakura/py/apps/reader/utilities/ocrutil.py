# coding: utf8
# ocrutil.py
# 9/15/2014 jichi

from functools import partial
from sakurakit import skthreads
from sakurakit.skdebug import dwarn
from sakurakit.skwincom import SkCoInitializer
from modi import modi
import main

# Note: the read functions might raise if the image path does not exist on Windows XP

from PySide.QtCore import QMutex
READ_MUTEX = QMutex() # sync access would crash

class _ReadLocker():
  def __init__(self):
    self.locked = False
  def __enter__(self):
    self.locked = READ_MUTEX.tryLock()
    if self.locked:
      return self
    else:
      dwarn("failed to lock mutex due to contention")
      return
  def __exit__(self, *err):
    if self.locked:
      READ_MUTEX.unlock()

def readtext(path, lang, async=False):
  """
  @param  path  unicode
  @param  lang  unicode
  @param* async  bool
  @return  unicode
  """
  return skthreads.runsync(partial(_readtext_async, path, lang)) if async else _readtext_sync(path, lang)

def readtexts(path, lang, async=False):
  """
  @param  path  unicode
  @param  lang  unicode
  @param* async  bool
  @return  [unicode]
  """
  return skthreads.runsync(partial(_readtexts_async, path, lang)) if async else _readtexts_sync(path, lang)

def _readtext_async(*args, **kwargs):
  with SkCoInitializer():
    return _readtext_sync(*args, **kwargs)

def _readtexts_async(*args, **kwargs):
  with SkCoInitializer():
    return _readtexts_sync(*args, **kwargs)

def _readtext_sync(*args, **kwargs):
  with _ReadLocker():
    return modi.readtext(*args, **kwargs)

def _readtexts_sync(*args, **kwargs):
  with _ReadLocker():
    return modi.readtexts(*args, **kwargs)

# EOF

# coding: utf8
# trcache.py 8
# /23/2014 jichi

import os, sqlite3
from PySide.QtCore import QObject
from sakurakit import skfileio
from sakurakit.skclass import memoized
from sakurakit.skdebug import dprint, dwarn
from trdb import trdb
import rc

class _TranslationCacheManager:

  def __init__(self):
    self.locks = {} # {str key, bool}

  def add(self, key, fr, to, text, translation):
    dbpath = rc.trdb_path(key=key, fr=fr, to=to)
    if not os.path.exists(dbpath):
      dirpath = os.path.dirname(dbpath)
      if not os.path.exists(dirpath):
        skfileio.makedirs(dirpath)
      if trdb.createdb(dbpath):
        dprint("create translation database:", dbpath)
      else:
        dwarn("failed to create translation database:", dbpath)
        return False

    try:
      with sqlite3.connect(dbpath) as conn:
        cur = conn.cursor()
        trdb.insertentry(cur, text, translation)
        conn.commit()
        return True
    except Exception, e:
      dwarn(e)

    skfileio.removefile(dbpath)
    return False

  def get(self, key, fr, to, text):
    dbpath = rc.trdb_path(key=key, fr=fr, to=to)
    if os.path.exists(dbpath):
      try:
        with sqlite3.connect(dbpath) as conn:
          return trdb.queryvalue(conn.cursor(), text)
      except Exception, e:
        dwarn(e)

# Persistent cache implement using sqlite
# TODO: Use QTimer to batch adding translations
class TranslationCacheManager(QObject):

  def __init__(self, parent=None):
    super(TranslationCacheManager, self).__init__(parent)
    self.__d = _TranslationCacheManager()

  def get(self, key, *args, **kwargs):
    """
    @param  key  str  translator key
    @param  fr  str  language
    @param  to  str  language
    @param  text  unicode
    @return  unicode or None
    """
    d = self.__d
    if not d.locks.get(key):
      return d.get(key, *args, **kwargs)

  def add(self, key, *args, **kwargs):
    """
    @param  key  str  translator key
    @param  fr  str  language
    @param  to  str  language
    @param  text  unicode
    @param  translation  unicode
    @return  bool  whether succeed
    """
    d = self.__d
    if d.locks.get(key):
      return False
    d.locks[key] = True
    ok = d.add(key, *args, **kwargs)
    d.locks[key] = False
    return ok

@memoized
def manager(): return TranslationCacheManager()
add = manager().add # make the function faster
get = manager().get # make the function faster

# EOF

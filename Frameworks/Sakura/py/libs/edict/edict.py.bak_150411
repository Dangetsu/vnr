# coding: utf8
# edict.py
# 11/25/2012 jichi
# See: http://cjklib.org/0.3/library/cjklib.dictionary.html
#
# The EDICT class from cjklib is not thread safe.
# So, it must be warmed up in the main thread.

__all__ = 'NullEdict', 'Edict'

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import os, re
from sakurakit import skpaths
#from sakurakit.skclass import memoizedproperty
from sakurakit.skdebug import dprint, dwarn

class NullEdict(object):
  def __init__(self, location=None):
    self.d = None
    self.location = location
  def valid(self): return True
  def lookup(self, text, **kwargs): return []
  def complete(self, text): pass
  def translate(self, text, **kwargs): pass

class Edict(object):

  RECONNECT = True # Automatically recreate connection

  @property
  def d(self):
    """
    @return  EDICT
    """
    if not self._d and self.location:
      try:
        dbfile = self.location
        dburl = "sqlite:///%s" % (
            skpaths.abspath(dbfile).replace(os.path.sep, '/'))
        dprint("url = %s" % dburl)

        from cjklib.dictionary import EDICT
        ret = EDICT(databaseUrl=dburl)
        ret.getAll(limit=1) # warmup, in case the db file is corrupted
        if self.RECONNECT:
          ret.db.connection.close()
        self._d = ret
      except Exception, e:
        dwarn(e)
    return self._d

  def __init__(self, location=None):
    self._d = None # edict instance
    self.location = location # unicode or None

  def connect(self): self.d.db.connection = self.d.db.engine.connect()
  def disconnect(self): self.d.db.connection.close()

  def valid(self):
    """
    @return  bool
    """
    return bool(self.d)

  def lookup(self, text, complete=False, **kwargs):
    """Return list of translations if exist, or list of reversed translations
    @param  text  unicode
    @param* complete  bool  not enabled by default, since getFor can also search for translation
    @param* limit  int  maximum account
    @yield  EntryTuple as an alias of sqlalchemy named table

    The EntryTuple has following named columns:
    - Headword  unicode  the matched word
    - Reading  unicode  the yomigana
    - Translation  unicode  the description
    """
    #if self.d:
    try:
      if self.RECONNECT:
        self.connect()
      for it in self.d.getFor(text, **kwargs):
        complete = False
        yield it
      if complete:
        text = self.complete(text)
        if text:
          for it in self.lookup(text, **kwargs):
            yield it
      if self.RECONNECT:
        self.disconnect()
    except Exception, e: # in case the db file is deleted
      dwarn(e)

  #def warmup(self):
  #  self.lookup('')

  _complete_dict0 = {
    u'れ': u'る', # 守れる
    u'べ': u'る', # しゃべる
    u'え': u'る', # 聞こえる
    u'め': u'る', # 死ぬ
    u'ね': u'る', # ねる
    u'ぺ': u'る', # 食べる
    u'て': u'る', # 知ってる
    #u'で': u'る', # 出る
    u'じ': u'る', # 信じる
  }
  _complete_dict1 = {
    u'わ': u'う', # 言う
    #u'い': u'う', # 言う
    u'い': u'く', # 動いた => 動く
    u'っ': u'う', # 言っ => 言う
    #u'っ': u'る', # 知って => 知ってる, but 言っ does not work
    u'ち': u'つ', # 死なせて => 死ぬ
    u'か': u'く', # 聞か => 聞く
    u'き': u'く', # 書き
    u'が': u'ぐ', # 仰ぐ
    u'ぎ': u'ぐ', # 仰ぐ
    u'ら': u'る',
    u'り': u'る',
    u'ま': u'む', # 止む
    u'み': u'む',
    u'な': u'ぬ', # 死なせて => 死ぬ
    u'に': u'ぬ', # 死になさい => 死ぬ
    #u'ん': u'ぬ', # 死ん => 死ぬ
    u'ん': u'む', # 移り住ん => 移り住む
  }
  _complete_trim_chars = u'ぁ', u'ぇ', u'ぃ', u'ぉ', u'ぅ' #, u'っ', u'ッ'
  def complete(self, text):
    """
    @param  text  unicode
    @return  unicode or None
    """
    if text and len(text) > 1:
      size = len(text)
      while len(text) > 1:
        if text[-1] in self._complete_trim_chars:
          text = text[:-1]
        else:
          break
      while len(text) > 1:
        if text[0] in self._complete_trim_chars:
          text = text[1:]
        else:
          break
      if size != len(text):
        return text
      last = text[-1]
      t = self._complete_dict0.get(last)
      if t:
        return text + t
      t = self._complete_dict1.get(last)
      if t:
        return text[:-1] + t

  _rx_tr1 = re.compile('|'.join((
    r'^/\(.+?\) (?=[a-zA-Z0-9.])',
    r'^/',
    r'[/(].*',
  )))
  _rx_tr2 = re.compile('|'.join((
    r'^(?:to|\.+) ', # remove leading "to" and ".."
    r'from which.*', # remove trailing clause
    r'[.]+$', # remove trailing dots
  )))
  def translate(self, text, wc=5, limit=3, complete=True):
    """Translate Japanese word to English
    @param  text  unicode
    @param* wc  int  count of word -1
    @param* limit  int  maximum tuples to look up
    @param* complete  bool  enabled by default
    @return  unicode or None

    Return the first hitted word in the dictionary.
    """
    if text and self.d:
      try:
        if self.RECONNECT:
          self.connect()
        for it in self.d.getForHeadword(text, limit=limit):
          ret = self._rx_tr2.sub('',
            self._rx_tr1.sub('', it.Translation).strip()
          ).strip()
          if ret and (not wc or ret.count(' ') <= wc):
            if self.RECONNECT:
              self.disconnect()
            return ret
        if self.RECONNECT:
          self.disconnect()
        if complete:
          text = self.complete(text)
          if text:
            return self.translate(text, wc=wc, limit=limit)
      except Exception, e: # in case the db file is deleted
        dwarn(e)

if __name__ == '__main__':
  t = u"殺す"
  t = u"政治"
  t = u"声"
  t = u"出身"
  t = u"裁判"
  t = u"可愛い"
  t = u"大柴"
  t = u"身長"
  t = u"体重"
  t = u"茶道"
  t = u"結婚"
  t = u"採集"
  t = u"ヤング"
  t = u"どこ"
  t = u"佐藤"
  t = u"雫"
  t = u"街"
  t = u"晴明"
  t = u"安倍"
  t = u"エミリ"
  t = u"春日"
  t = u"友達"
  t = u"石浦"
  t = u"能力"
  t = u"人気"
  t = u"任せ"
  t = u"幸せ"
  t = u"忘れる"
  t = u"忘れ"
  t = u"止めっ"
  t = u'移り住ん'
  t = u'移り住む'
  t = u'頼ま'
  t = u'頼む'
  t = u'聞く'
  t = u'聞か'
  t = u'討ち'
  t = u'討つ'
  t = u'動い'
  t = u'動く'
  t = u'知って'
  t = u'言わ'
  t = u'行きぁ'
  enamdictdb = '/Library/Application Support/cjklib/enamdict.db'
  #edictdb = '/Library/Application Support/cjklib/edict.db'
  #edictdb = 'S:/stream/Library/Dictionaries/edict.db'
  #edictdb = u'S:/中文/Library/Dictionaries/edict.db'
  edictdb = '../../../../../../Caches/Dictionaries/EDICT/edict.db'
  edict = Edict(edictdb)
  #enamdict = Edict(enamdictdb)
  #for index, it in enumerate(enamdict.lookup(t)):
  #  print '#%i:' % index, it
  #  print it.Headword
  #  print it.Reading
  #  print it.Translation
  for index, it in enumerate(edict.lookup(t, complete=True)):
    #print '#%i:' % index, it
    #print it.Headword
    #print it.Reading
    print index
    print it.Headword
    print it.Translation
  #print "enam translation:"
  #print enamdict.translate(t)

  print "edict translation:"
  print edict.translate(t)

# EOF

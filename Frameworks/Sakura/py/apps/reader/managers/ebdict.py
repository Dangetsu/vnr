# coding: utf8
# ebdict.py
# 3/29/2013 jichi
#
# The file name is not "epwing.py", which conflict with "epywing" module.

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

import os, re
import eblib
from sakurakit.skclass import memoized
from sakurakit.skdebug import dwarn
from convutil import wide2thin, zhs2zht
import rc

def init():
  eblib.eb_initialize_library()
  import atexit
  atexit.register(eblib.eb_finalize_library)
init()

## Gaiji ##

def narrow_gaiji(code):
  """
  @param  code  int
  @return  unicode
  """
  return 'h%04X' % code

def wide_gaiji(code):
  """
  @param  code  int
  @return  unicode
  """
  return 'z%04X' % code

def ebxac_gaiji(code):  # FIXME: caiji code is incorrect
  """
  @param  code  int
  @return  unicode
  """
  return 'c%04X' % code

## EB Renderer ##

class EBTest(eblib.EB):
  """For testing purpose only"""
  def hook_narrow_font(self, container, code):
    """@reimp"""
    self.write_text("<gaiji=h%04x>" % code)
  def hook_wide_font(self, container, code):
    """@reimp"""
    self.write_text("<gaiji=z%04x>" % code)
  def hook_begin_reference(self, container):
    """@reimp"""
    self.write_text("<reference>")
  def hook_end_reference(self, container, page, offset):
    """@reimp"""
    self.write_text("</reference=%x:%x>" % (page, offset))
  def hook_begin_keyword(self, container):
    """@reimp"""
    self.write_text("<keyword>")
  def hook_end_keyword(self, container):
    """@reimp"""
    self.write_text("</keyword>")

class EBHtml(eblib.EB):
  def __init__(self, path, gaiji={}):
    """
    @param  path  unicode
    @param  gaiji  {str:unicode} not None
    """
    super(EBHtml, self).__init__(path)
    self.gaiji = gaiji

  # Overridden hooks

  def hook_newline(self, _):
    """@reimp"""
    self.write_text("<br/>")

  def hook_narrow_font(self, _, code):
    """@reimp"""
    self.write_gaiji(narrow_gaiji(code))
  def hook_wide_font(self, _, code):
    """@reimp"""
    self.write_gaiji(wide_gaiji(code))
  def hook_ebxac_gaiji(self, _, code):
    """@reimp"""
    # FIXME: not working
    #self.write_gaiji(ebxac_gaiji(code))
    pass

  # Helpers

  def write_gaiji(self, key):
    t = self.gaiji.get(key) or ' ' # space by default
    self.write_text(t)

class EBShiori(EBHtml):
  def __init__(self, path, gaiji={}):
    super(EBShiori, self).__init__(path, gaiji=gaiji)

  """Used in kagami/shiori.qml"""
  def hook_begin_reference(self, _):
    """@reimp"""
    self.write_text('<span class="sr">')
  def hook_end_reference(self, _, page, offset):
    """@reimp"""
    #self.write_text("</reference=%x:%x>" % (page, offset))
    self.write_text("</span>")
  def hook_begin_keyword(self, _):
    """@reimp"""
    self.write_text('<span class="sk">')
  def hook_end_keyword(self, _):
    """@reimp"""
    self.write_text("</span>")

class EBChineseShiori(EBShiori):

  def __init__(self, path, gaiji={}):
    super(EBChineseShiori, self).__init__(path, gaiji=gaiji)
    self.zht = False # bool  whether transform to traditional Chinese

  def write_byte2_gb2312(self, b2):
    """@reimp"""
    t = b2.decode('gb2312', errors='ignore')
    if t:
      if self.zht:
        t = zhs2zht(t)
      self.write_text(t)

## EPWING Manager ##

class _EBook:

  def __init__(self, encoding, ebcls, gaiji):
    self.EB = ebcls  # eblib.EB.class
    self._eb = None  # eblib.EB  or None
    self.encoding = encoding # str
    self.gaiji = gaiji # {str:unicode}
    self.path = None # unicode

  @property
  def eb(self):
    if not self._eb and self.verifyPath(self.path):
      try:
        eb = self.EB(self.path, gaiji=self.gaiji)
        if self._verifyEB(eb):
          self._eb = eb
      except Exception, e:
        dwarn(e)
    return self._eb

  def resetEb(self): self._eb = None

  @staticmethod
  def verifyPath(path):
    """
    @param  path  unicode
    @return  bool
    """
    return bool(path) and os.path.exists(path) and (
      os.path.exists(os.path.join(path, 'CATALOG')) or
      os.path.exists(os.path.join(path, 'CATALOGS'))
    )

  @staticmethod
  def _verifyEB(eb):
    """
    @param  eb  eblib.EB
    @return  bool
    @throw  eb.EBError
    """
    return bool(eb and eb.subbook_list())

class EBook(object):
  def __init__(self, encoding='euc_jp', gaiji={}, eb=EBShiori):
    """
    @param  encoding  unicode
    @param  eb  eblib.EB
    @param  gaiji  {str key:unicode gaiji}
    """
    self.__d = _EBook(encoding, eb, gaiji)

  ## Properties ##

  def eb(self): return self.__d.eb

  def location(self):
    """
    @return  unicode
    """
    return self.__d.path

  def setLocation(self, value):
    d = self.__d
    if d.path != value:
      d.path = value
      d.resetEb()

  @staticmethod
  def verifyLocation(path):
    """
    @param  path  unicode
    @return  bool
    """
    return _EBook.verifyPath(path)

  def exists(self):
    """
    @return  bool
    """
    return bool(self.__d.eb)

  ## Actions ##

  def lookup(self, text):
    """
    @return  [eblib.EB_Hit] not None
    """
    try: return self.__d.eb.search_word(
        text.encode(self.__d.encoding, errors='ignore'))
    #except UnicodeEncodeError:
    #  dwarn("failed to decode text")
    except TypeError: # eb is None
      dwarn("eb is not ready")
    return []

  def render(self, text):
    """
    @yield  unicode
    """
    for hit in self.lookup(text):
      yield self.renderText(wide2thin(hit.text().decode('utf8', errors='ignore')))
      #try: yield hit.text().decode('utf8')
      #except UnicodeDecodeError: dwarn("failed to decode text")

  ## Protected ##

  def renderText(self, text): return text # unicode -> unicode

# 岩波書店 広辞苑
class KojienDic(EBook):
  NAME = 'KOJIEN'   # must be consistent with gaiji
  URL = "http://www.iwanami.co.jp/moreinfo/1301610/"
  #URL = "http://www.iwanami.co.jp/kojien/"

  def __init__(self):
    super(KojienDic, self).__init__(
        eb=EBShiori,
        #encoding='euc_jp',
        gaiji=rc.gaiji_dict(self.NAME))

# 三省堂 スーパー大辞林第二版
class DaijirinDic(EBook):
  NAME = 'DAIJIRIN'   # must be consistent with gaiji
  URL = "http://daijirin.dual-d.net"

  def __init__(self):
    super(DaijirinDic, self).__init__(
        eb=EBShiori,
        #encoding='euc_jp',
        gaiji=rc.gaiji_dict(self.NAME))

  _rx_garbage = re.compile(ur'{?■.■}?') # Such as: "■一■ " or " {■二■}"
  def renderText(self, text):
    """@reimp"""
    return self._rx_garbage.sub('', text) if text else ''

# 小学館 大辞泉
class DaijisenDic(EBook):
  NAME = 'DAIJISEN'   # must be consistent with gaiji
  URL = "http://www.daijisen.jp"

  def __init__(self):
    super(DaijisenDic, self).__init__(
        eb=EBShiori,
        #encoding='euc_jp',
        gaiji=rc.gaiji_dict(self.NAME))

# 小学館 日中統合辞書
class ZhongriDic(EBook):
  NAME = 'ZHONG_RI'   # must be consistent with gaiji
  URL = "http://amazon.co.jp/dp/4099068676"
  #URL = "http://www.shogakukan.co.jp/"

  def __init__(self):
    super(ZhongriDic, self).__init__(
        eb=EBChineseShiori,
        gaiji=rc.gaiji_dict(self.NAME))

  def convertsToTraditional(self):
    """ren
    @return  bool
    """
    return self.exists() and self.eb().zht
  def setConvertsToTraditional(self, value):
    if self.exists():
      self.eb().zht = value

# 講談社 日中辞典
class KoudanjcDic(EBook):
  NAME = 'KOUDANJC' # gaiji not defined though
  URL = "http://bookclub.kodansha.co.jp/product?isbn=9784062653329"
  #URL = "http://www.shogakukan.co.jp/"

  def __init__(self):
    super(ZhongriDic, self).__init__(
        eb=EBChineseShiori)
        #gaiji=rc.gaiji_dict(self.NAME))

  def convertsToTraditional(self):
    """ren
    @return  bool
    """
    return self.exists() and self.eb().zht

  def setConvertsToTraditional(self, value):
    if self.exists():
      self.eb().zht = value

# Downloadable FPW

class FreePWING(EBook): # Free EPWING
  language = ''

  def __init__(self, *args, **kwargs):
    super(FreePWING, self).__init__(*args, **kwargs)

  def name(self): return 'fpw' # abstract

  def render(self, *args, **kwargs): # override
    if not self.exists():
      from mytr import my
      import growl
      # Note: The following warning is not translated into Chinese
      growl.warn(my.tr("{0} does not exist. Please try redownload it in Preferences").format(self.name()))
    else:
      for it in super(FreePWING, self).render(*args, **kwargs):
        yield it

  def translate(self, text):
    """
    @param  text  unicode
    @return  unicode or None
    """
    try:
      for it in self.lookup(text):
        text = it.text().decode('utf8', errors='ignore') # decode might throw key error?!
        if text:
          from dictp import jmdictp
          return jmdictp.parsedef(text, self.language)
    except Exception, e: dwarn(e)

# 和独辞書
class WadokuDic(FreePWING):
  NAME = 'WADOKU'   # must be consistent with gaiji
  language = 'ru' # override
  URL = "http://www.wadoku.de/wiki/display/WAD/Downloads+und+Links"

  def __init__(self):
    super(WadokuDic, self).__init__(
        eb=EBShiori,
        gaiji=rc.gaiji_dict(self.NAME))

  def name(self): return "Wadoku" # override

  def renderText(self, text): # override
    text = text.replace('|| ', '')
    if '[1]' in text:
      text = text.replace('[1]', '<ol>[1]')
      text = text.replace('<br/><ol>', '<ol>')
      text = re.sub(r'\[[0-9]+\]', r'<li>', text)
      text += '</ol>'
    return text

# JMDict
class JMDict(FreePWING):
  NAME = 'JMDict'

  #http://ftp.monash.edu.au/pub/nihongo/UPDATES
  URL = "ftp://ftp.monash.edu.au/pub/nihongo"

  def __init__(self, language): # str
    self.language = language # override
    super(JMDict, self).__init__(eb=EBShiori)
        #encoding='utf8')

  def name(self): return "JMDict-" + self.language # override

  def renderText(self, text):
    import _dictman # FIXME: cross package
    return _dictman.render_jmdict(text, self.language)

@memoized
def kojien():
  """
  @return  EBook
  """
  ret = KojienDic()
  import settings
  ret.setLocation(settings.global_().kojienLocation())
  return ret

@memoized
def daijirin():
  """
  @return  EBook
  """
  ret = DaijirinDic()
  import settings
  ret.setLocation(settings.global_().daijirinLocation())
  return ret

@memoized
def daijisen():
  """
  @return  EBook
  """
  ret = DaijisenDic()
  import settings
  ret.setLocation(settings.global_().daijisenLocation())
  return ret

@memoized
def zhongri():
  """
  @return  EBook
  """
  ret = ZhongriDic()
  import settings
  ss = settings.global_()
  ret.setLocation(ss.zhongriLocation())
  # Converting chinese is disabled so that it will not mess up the Japanese kanji
  #ret.setConvertsToTraditional(ss.convertsChinese())
  #ss.convertsChineseChanged.connect(ret.setConvertsToTraditional)
  return ret

@memoized
def wadoku():
  """
  @return  EBook
  """
  ret = WadokuDic()
  import dicts
  path = dicts.wadoku().path
  ret.setLocation(path)
  return ret

JMDICT = {}
def jmdict(lang):
  """
  @return  EBook
  """
  ret = JMDICT.get(lang)
  if not ret:
    ret = JMDICT[lang] = JMDict(lang)
    import dicts
    path = dicts.jmdict(lang).path
    ret.setLocation(path)
  return ret

if __name__ == '__main__':
  import os, sys

  #for t in zhongri().render(u"かわいい"):
  #  print type(t)
  #sys.exit(0)

  #for t in wadoku().render(u"かわいい"):
  #  print type(t), t
  #sys.exit(0)

  #sys.exit(0)

  #DIC_ENC = 'euc_jp'
  #DIC_ENC = 'sjis'
  #DIC_DEC = 'euc_jp'
  #DIC_DEC = 'utf8'

  #DIC_NAME = 'KOJIEN'

  #DIC_NAME = 'ZHONG_RI'
  #DIC_NAME = 'freJMD'
  #DIC_NAME = 'jr-edict'

  #DIC_NAME = 'WADOKU'
  #DIC_ENC = 'euc_jp'
  #DIC_DEC = 'euc_jp'

  gaiji = {}

  #relpath = 'JMDict/fr.fpw'
  #dic_path = '../../../../../../Caches/Dictionaries/' + relpath
  #dic_path = os.path.abspath(dic_path)
  #print dic_path
  #dic_path = '/Local/Windows/Applications/EB/DAIJIRIN'
  dic_path = '/Local/Windows/Applications/EB/KOUDANJC'
  #dic_path = '/Local/Windows/Applications/EB/ZHONG_RI'

  gaiji = rc.gaiji_dict('ZHONG_RI')

  #dic_path = 'S:/Applications/EB/WADOKU/wadoku_epwing_jan2012'
  if len(sys.argv) == 2:
    dic_path = sys.argv[1]

  #eblib.eb_initialize_library()
  eb = EBChineseShiori(dic_path, gaiji=gaiji)
  #eb = EBShiori(dic_path, gaiji=gaiji)
  #eb = EBShiori(dic_path, gaiji=gaiji)
  #eb.zht = True
  #eb = EBTest(dic_path)
  #for subbook in eb.subbook_list():
  #  print "#%d. %s (%s)" % (subbook,
  #              eb.subbook_title(subbook).decode(DIC_DEC),
  #              eb.subbook_directory(subbook).decode(DIC_DEC))

  eb = JMDict('fr')
  import os
  print os.path.exists(dic_path)
  eb.setLocation(dic_path)

  #from PySide.QtGui import *
  #def show(t):
  #  import sys
  #  a = QApplication(sys.argv)
  #  w = QLabel(t)
  #  w.show()
  #  a.exec_()

  t = u'綺麗'
  #t = u'万歳'
  hits = eb.render(t)
  for it in hits:
    print it
  #hits = eb.search_word(t.encode(DIC_ENC))
  #if hits:
  #  hit = hits[0]
  #  #print hit.text().decode(DIC_ENC)
  #  t = hit.text()
  #  print type(t)
  #  tt = t.decode(DIC_DEC, errors='ignore')
  #  show(tt)
  #else:
  #  print "no hits"

  #eblib.eb_finalize_library()

# EOF

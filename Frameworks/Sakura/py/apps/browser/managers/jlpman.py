# coding: utf8
# jlpman.py
# 3/28/2014 jichi

from sakurakit.skclass import memoized
from sakurakit.skdebug import dwarn

@memoized
def manager(): return JlpManager()

class JlpManager:

  def __init__(self):
    self.__d = _JlpManager()

  def isAvailable(self):
    return bool(self.__d.mecabdic and self.__d.tagger())

  def setRubyType(self, v):
    self.__d.rubytype = v # str

  def setMeCabDicType(self, v):
    self.__d.mecabdic = v # str

  def parseToRuby(self, text): #
    return self.__d.parseToRuby(text)
    #return [
    #  [
    #    ("助平","すけべい", "feature1", 'word1'),
    #    ("助平1","すけべい2", "feature2", 'word2'),
    #  ],
    #]

class _JlpManager:
  def __init__(self):
    self._tagger = None
    #self.rubytype = mecabdef.RB_HIRA # str
    self.rubytype = 'hira'
    self.mecabdic = ''
    self.mecabfmt = None

  # MeCab

  def tagger(self):
    if self._tagger is None and self.mecabdic:
      try:
        from mecabjlp import mecabfmt, mecabtag
        #import rc
        #rcfile = rc.mecab_rc_path(self.mecabdic)
        #mecabtag.setenvrc(rcfile)
        self.mecabfmt = mecabfmt.getfmt(self.mecabdic)
        self._tagger = mecabtag.createtagger()
      except Exception, e:
        dwarn(e)
        self._tagger = False
    return self._tagger

  def parseToRuby(self, text): # unicode ->
    tagger = self.tagger()
    if tagger:
      from mecabjlp import mecabrender
      it = mecabrender.parseparagraph(text,
          tagger=tagger,
          fmt=self.mecabfmt,
          ruby=self.rubytype)
      return list(it)

# EOF

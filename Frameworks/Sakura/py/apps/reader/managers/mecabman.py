# coding: utf8
# mecabman.py
# 10/12/2012 jichi
import os
from sakurakit.skclass import memoized
from sakurakit.skdebug import dprint, dwarn
from mecabparser import mecabdef, mecabformat
from convutil import kata2hira, kata2romaji
from mytr import my
import dictman, growl, rc

ROMAJI_RUBY_TYPES = (
  #mecabdef.RB_KATA,
  #mecabdef.RB_HIRA,
  mecabdef.RB_ROMAJI,
  mecabdef.RB_TR,
  mecabdef.RB_RU,
  mecabdef.RB_UK,
  mecabdef.RB_EL,
  mecabdef.RB_KO,
  mecabdef.RB_VI,
  mecabdef.RB_TH,
  mecabdef.RB_AR,
)

@memoized
def manager(): return MeCabManager()

## Manager class

class _MeCabManager:
  def __init__(self):
    self.translateEnabled = False
    self.userdicEnabled = False
    self._parserWithUserdic = None
    self._parserWithoutUserdic = None

  def getParser(self):
    """
    @return mecabparser.MeCabParser or None
    """
    return self._getParserWithUserdic() if self.userdicEnabled else self._getParserWithoutUserdic()

  def isParserLoaded(self):
    return bool(self._parserWithUserdic or self._parserWithoutUserdic)

  def _getParserWithoutUserdic(self):
    if not self._parserWithoutUserdic:
      if not os.path.exists(rc.DIR_UNIDIC):
        dwarn("missing unidic")
        growl.warn(my.tr("MeCab UniDic dictionary not found"))
        return
      from mecabparser import mecabparser
      self._parserWithoutUserdic = mecabparser.MeCabParser()
      dprint("create mecab without userdic")
    return self._parserWithoutUserdic

  def _getParserWithUserdic(self):
    if not self._parserWithUserdic:
      userdic = rc.MECAB_EDICT_PATH
      userdic = os.path.relpath(userdic, os.getcwd())
      # use relative path to avoid spaces and illegal unicode characters
      if not os.path.exists(userdic):
        dwarn("missing edict: %s" % userdic)
        growl.warn(my.tr("MeCab EDICT dictionary not found"))
        return self._getParserWithoutUserdic()
      from mecabparser import mecabparser
      ret = mecabparser.MeCabParser()
      ret.tagger().setUserdic(userdic)
      self._parserWithUserdic = ret
      dprint("create mecab with userdic")
    return self._parserWithUserdic

class MeCabManager:

  def __init__(self):
    self.__d = _MeCabManager()

  def isLoaded(self): return self.__d.isParserLoaded()

  def isEdictEnabled(self, t): return self.__d.userdicEnabled
  def setEdictEnabled(self, t):
    dprint(t)
    self.__d.userdicEnabled = t

  def isTranslateEnabled(self, t): return self.__d.translateEnabled
  def setTranslateEnabled(self, t):
    dprint(t)
    self.__d.translateEnabled = t

  def parse(self, text, rubyType, rubyKana=False):
    """
    @param  rubyType  str
    @param* rubyKana  bool
    @yield  (unicode surface, unicode ruby, unicode feature) or return None
    """
    tr = dictman.manager().translateJapanese if self.__d.translateEnabled and dictman.manager().japaneseTranslateLanguages() else None
    try: return self.__d.getParser().iterparseToRuby(text, rubyType, tr=tr, show_ruby_kana=rubyKana)
    except Exception, e: dwarn(e)

  def toRomaji(self, text, capital=True):
    """
    @param  text  unicode
    @param  capital  bool
    @return  unicode
    """
    try: return self.__d.getParser().toRomaji(text, capital=capital)
    except Exception, e: dwarn(e)
    return ''

  def toRuby(self, text, rubyType):
    """
    @param  text  unicode
    @param  rubyType  str
    @return  unicode
    """
    try: return self.__d.getParser().toRuby(text, rubyType)
    except Exception, e: dwarn(e)
    return ''

## Render feature

def renderfeature(feature, fmt=mecabformat.UNIDIC_FORMATTER):
  """
  @param  feature  unicode
  @return  unicode

  Example feature: 名詞,サ変接続,*,*,*,*,感謝,カンシャ,カンシャ
  Input feature:
    品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形,活用型,原形,読み,発音
  Rendered feature:
    原形,発音,品詞,品詞細分類1,品詞細分類2,品詞細分類3,活用形
  """
  if not feature:
    return ''
  feature = feature.replace('*', '').split(',')
  ret = filter(bool, feature[:fmt.COL_BASIC]) # keep all first role columns
  suffix = ''
  try:
    surface = fmt.getsurface(feature)
    kata = fmt.getkata(feature)
    hira = kata2hira(kata)

    v = fmt.getorigin(feature)
    if v and v not in (surface, kata, hira):
      ret.append(v)

    v = fmt.getdictype(feature)
    if v == fmt.DIC_EDICT:
      ret.append('EDICT')
    else:
      ret.append('UNIDIC')

    if fmt.isdic(feature):
      v = fmt.getdictrans(feature)
      if v:
        suffix = "<br/>" + v # change to the second line
    else:
      v = fmt.getsource(feature)
      if v:
        if '-' in v:
          v = v.partition('-')[2]
        if v and v not in (surface, kata, hira):
          ret.insert(0, v)

    if kata:
      romaji = kata2romaji(kata)
      if romaji != surface:
        ret.insert(0, romaji)
      if hira and hira not in (surface, romaji):
        ret.insert(0, hira)

    if surface:
      ret.insert(0, surface)
  except IndexError: pass

  return ','.join(ret) + suffix

## Render table

ROLE_COLOR_ALPHA = 30
ROLE_COLORS = {
  mecabdef.ROLE_NAME: 'rgba(255,0,0,%s)'    % ROLE_COLOR_ALPHA, # red
  mecabdef.ROLE_PLACE: 'rgba(255,0,0,%s)'   % ROLE_COLOR_ALPHA, # = name
  mecabdef.ROLE_PRONOUN: 'rgba(255,0,0,%s)' % ROLE_COLOR_ALPHA, # = name
  mecabdef.ROLE_PHRASE: 'rgba(255,0,0,%s)'  % ROLE_COLOR_ALPHA, # = name

  mecabdef.ROLE_NOUN: 'rgba(0,255,0,%s)'    % ROLE_COLOR_ALPHA, # green
  mecabdef.ROLE_NUM: 'rgba(0,255,0,%s)'     % ROLE_COLOR_ALPHA, # = noun
  mecabdef.ROLE_ADN: 'rgba(0,255,0,%s)'     % ROLE_COLOR_ALPHA, # = noun
  mecabdef.ROLE_PREFIX: 'rgba(0,255,0,%s)'  % ROLE_COLOR_ALPHA, # = noun
  mecabdef.ROLE_SUFFIX: 'rgba(0,255,0,%s)'  % ROLE_COLOR_ALPHA, # = noun, dangling
  mecabdef.ROLE_MARK: 'rgba(0,255,0,%s)'    % ROLE_COLOR_ALPHA, # = noun, dangling

  mecabdef.ROLE_VERB: 'rgba(255,0,255,%s)'  % ROLE_COLOR_ALPHA, # magenta
  mecabdef.ROLE_ADV: 'rgba(255,0,255,%s)'   % ROLE_COLOR_ALPHA, # = verb
  mecabdef.ROLE_AUX: 'rgba(255,0,255,%s)'   % ROLE_COLOR_ALPHA, # = verb, dangling

  mecabdef.ROLE_A: 'rgba(255,255,0,%s)'     % ROLE_COLOR_ALPHA, # yellow
  mecabdef.ROLE_ADJ: 'rgba(255,255,0,%s)'   % ROLE_COLOR_ALPHA, # = a

  mecabdef.ROLE_CONJ: 'rgba(0,0,255,%s)'    % ROLE_COLOR_ALPHA, # blue
  mecabdef.ROLE_INTERJ: 'rgba(0,0,255,%s)'  % ROLE_COLOR_ALPHA, # = conj
  mecabdef.ROLE_PART: 'rgba(0,0,255,%s)'    % ROLE_COLOR_ALPHA, # = conj, dangling
}
def _iterrendertable(text, rubyType, rubyKana=False, features=None, charPerLine=100, rubySize=10, colorize=False, rubyInverted=False, annotated=False, highlight=False, center=True, fmt=mecabformat.UNIDIC_FORMATTER):
  """
  @param  text  unicode
  @param  rubyType  str
  @param* rubyKana  bool
  @param* charPerLine  int  maximum number of characters per line
  @param* rubySize  float
  @param* rubyInverted  bool
  @param* colorsize  bool
  @param* annotated  bool
  @param* highlight  bool
  @param* center  bool
  @param* features  {unicode surface:(unicode feature, fmt)} or None
  @param* fmt  mecabfmt
  @yield  unicode  HTML table
  """
  q = manager().parse(text, rubyType, rubyKana=rubyKana)
  if q:
    render = rc.jinja_template('html/furigana').render

    i = j = 0
    line = []
    lineCount = 0 # int  estimated line width, assume ruby has half width
    hasfeature = features is not None

    PADDING_FACTOR = 0.3
    LATIN_YOMI_WIDTH = 0.33 # = 2/6
    KANJI_YOMI_WIDTH = 0.55 # = 1/2

    ANNOT_ZOOM = 0.9
    ANNOT_WIDTH = LATIN_YOMI_WIDTH * ANNOT_ZOOM
    # yomi size / surface size

    #if rubyInverted:
    #  yomiWidth = 1 if mecabdef.rb_is_wide(rubyType) else 0.8
    #else:
    yomiWidth = KANJI_YOMI_WIDTH if mecabdef.rb_is_wide(rubyType) else LATIN_YOMI_WIDTH

    roundRubySize = int(round(rubySize)) or 1
    annotSize = int(round(rubySize * ANNOT_ZOOM)) or 1
    paddingSize = int(round(rubySize * PADDING_FACTOR)) or 1 if rubyInverted else 0

    role = None
    roleExists = False
    rubyExists = False
    color = lastColor = None

    ANNOT_FONT = 'Tahoma'

    for surface, yomi, feature, surface_type in q:
      #colorChanged = False

      if hasfeature:
        features[surface] = feature

      if annotated or not colorize and highlight:
        role = fmt.getrole(feature)
        if role == mecabdef.ROLE_PUNCT:
          role = None

      if colorize:
        if surface_type == mecabdef.SURFACE_KANJI:
          i += 1
          color = 'rgba(255,0,0,40)' if i % 2 else 'rgba(255,255,0,40)' # red or yellow
        elif surface_type == mecabdef.SURFACE_KANA:
          j += 1
          #color = 'rgba(0,255,0,40)' if j % 2 else 'rgba(255,0,255,40)' # green or magenta
          color = 'rgba(0,255,0,40)' if j % 2 else 'rgba(0,0,255,40)' # green or blue
        else:
          color = None
      elif highlight:
        if lastColor and role in (mecabdef.ROLE_PART, mecabdef.ROLE_AUX, mecabdef.ROLE_SUFFIX, mecabdef.ROLE_MARK):
          color = lastColor
        else:
          lastColor = color = ROLE_COLORS.get(role)
          #if lastColor != color:
          #  lastColor = color
          #  colorChanged = True

      width = max(
        len(surface),
        (len(yomi) * yomiWidth + (1 if rubyInverted else 0)) if yomi else 0, # +1 when inverted for paddingSize
        len(surface) * yomiWidth + 1 if rubyInverted else 0, # in case yomi is empty
        (len(role) + 1) * ANNOT_WIDTH if annotated and role else 0,
      )
      if width + lineCount <= charPerLine:
        pass
      elif line:
        yield render({
          'tuples': line,
          'rubySize': roundRubySize,
          'paddingSize': paddingSize,
          'center': center,
          'annotSize': annotSize,
          'annotExists': annotated and roleExists,
          'rubyExists': rubyExists,
          'annotFont': ANNOT_FONT,
        })
        line = []
        lineCount = 0
        roleExists = False
        rubyExists = False
      if rubyInverted and yomi:
        #if surface:
        #  surface = wide2thin(surface)
        if mecabdef.rb_has_case(rubyType) and len(yomi) > 2: #or colorChanged)
          yomi = yomi.title()
        t = yomi, surface, (role if annotated else None), color
      else:
        t = surface, yomi, (role if annotated else None), color
      if role:
        roleExists = True
      if yomi:
        rubyExists = True
      line.append(t)
      lineCount += width
    if line:
      yield render({
        'tuples': line,
        'center': center,
        'rubySize': roundRubySize,
        'paddingSize': paddingSize,
        'annotSize': annotSize,
        'annotExists': annotated and roleExists,
        'rubyExists': rubyExists,
          'annotFont': ANNOT_FONT,
      })

def rendertable(*args, **kwargs):
  """Parameters are the same as _iterrendertable"""
  return ''.join(_iterrendertable(*args, **kwargs))

# EOF

#_rx_spaces = re.compile(r'\s+')
#_rx_match_spaces = re.compile(r'^\s+$')
#
### Render HTML ruby ##
#
#_WORD_CSS_CLASSES = 'word2', 'word1', 'word4', 'word3'
#def _renderruby_word_iter(text, hasClass, features, **kwargs):
#  """
#  @yield  (str styleClass or None, unicode surface, unicode furigana not None)
#  """
#  l = []
#  i = j = 0
#  hasfeature = features is not None
#  styleClass = None
#  for it in parse(text, type=True, reading=True, feature=hasfeature, **kwargs):
#    if hasfeature:
#      surface, ch, yomi, f, fmt = it
#    else:
#      surface, ch, yomi = it
#    if hasClass:
#      styleClass = None
#      if ch in (mecabdef.TYPE_VERB, mecabdef.TYPE_NOUN, mecabdef.TYPE_KATAGANA):
#        i += 1
#        #color = 'rgba(255,0,0,40)' if i % 2 else 'rgba(255,255,0,40)'   # red or cyan
#        styleClass = _WORD_CSS_CLASSES[i % 2]
#      elif ch == mecabdef.TYPE_MODIFIER: # adj or adv
#        j += 1
#        #color = "rgba(0,255,0,40)" if j % 2 else "rgba(0,0,255,40)" # green or blue
#        styleClass = _WORD_CSS_CLASSES[2 + j % 2]
#    if hasfeature:
#      features[surface] = f, fmt
#    yield styleClass, surface, yomi or ''
#
#def _renderruby_word(text, hasClass, **kwargs):
#  """
#  @return  unicode  HTML
#  """
#  q = _renderruby_word_iter(text, hasClass=hasClass, **kwargs)
#  if hasClass:
#    return ''.join('<ruby class="%s"><rb>%s</rb><rt>%s</rt></ruby>' % it for it in q)
#  else:
#    return ''.join('<ruby><rb>%s</rb><rt>%s</rt></ruby>' % it[1:] for it in q)
#
##_rx_spaces = re.compile(r'\s+')
#def _renderruby_segment(text, **kwargs):
#  """
#  @return  unicode  HTML
#  """
#  return ' '.join(_renderruby_word(it, **kwargs)
#      for it in _rx_spaces.split(text) if it)
#
#__SENTENCE_DELIM = u"\n。!！？♪…【】■" # missing "?", which would cause trouble when it comes to "(?)"
#_SENTENCE_SET = frozenset(__SENTENCE_DELIM)
#_SENTENCE_RE = re.compile(r"(%s)" % '|'.join(_SENTENCE_SET))
#def _renderruby_sentence_iter(text, **kwargs):
#  """
#  @yield  unicode
#  """
#  for it in _SENTENCE_RE.split(text):
#    if it:
#      if it in _SENTENCE_SET:
#        yield it
#      else:
#        yield _renderruby_segment(it, **kwargs)
#
#def _renderruby_sentence(text, **kwargs):
#  """
#  @return  unicode  HTML
#  """
#  return ''.join(' ' if _rx_match_spaces.match(it) else '<span class="sentence">%s</span>' % it
#      for it in _renderruby_sentence_iter(text, **kwargs) if it)
#
#_rx_html_tags = re.compile(r"(<.+?>)")
#def _renderruby_html_iter(text, **kwargs):
#  """
#  @yield  unicode  HTML
#  """
#  for it in _rx_html_tags.split(text):
#    if it:
#      if it[0] == '<':
#        yield it
#      elif _rx_match_spaces.match(text):
#        yield ' '
#      else:
#        yield _renderruby_sentence(it, **kwargs)
#
#def _renderruby_html(text, **kwargs):
#  """
#  @return  unicode  HTML
#  """
#  return ''.join(_renderruby_html_iter(text, **kwargs))
#
#def renderruby(text, html=False, termEnabled=False, hasClass=True, furiType=defs.FURI_HIRA, features=None):
#  """
#  @param  text  unicode
#  @param* html  bool  whether input text contains html tags
#  @param* termEnabled  bool  whether use termman
#  @param* furiType  int
#  @param* hasClass  bool  whether have style classes
#  @param* features  {unicode surface:unicode feature} or None
#  @return  unicode  HTML ruby list
#  """
#  if not text:
#    return ''
#  if html:
#    return _renderruby_html(text,
#        termEnabled=termEnabled, hasClass=hasClass, furiType=furiType, features=features)
#  else:
#    return _renderruby_segment(text,
#        termEnabled=termEnabled, hasClass=hasClass, furiType=furiType, features=features)
#
#class MeCabCoffeeBean(QObject):
#  def __init__(self, parent=None):
#    super(MeCabCoffeeBean, self).__init__(parent)
#
#  @Slot(unicode, bool, result=unicode)
#  def toRuby(self, text, html):
#    """
#    @param  text  unicode  HTML
#    @param  html  bool  whether input text contains html tags
#    @return  unicode  HTML
#    """
#    return manager.toRuby(text, html)
#
#  @Slot(unicode, result=unicode)
#  def toYomi(self, text):
#    """
#    @param  text  unicode  plain text
#    @return  unicode  plain text
#    """
#    return manager().toYomi(text)
#
### Highlighter ##
#
#class MeCabHighlighter(QSyntaxHighlighter):
#
#  def highlightBlock(self, text):
#    """@reimp @protected"""
#    if not _MP.enabled:
#      return
#    i = j = 0
#    offset = 0
#    for surface, ch in parse(text, type=True):
#      offset += len(surface)
#      if ch in (mecabdef.TYPE_VERB, mecabdef.TYPE_NOUN, mecabdef.TYPE_KATAGANA):
#        i += 1
#        color = Qt.red if i % 2 else Qt.cyan
#        alpha = 40
#      elif ch == mecabdef.TYPE_MODIFIER: # adj or adv
#        j += 1
#        color = Qt.green if j % 2 else Qt.magenta
#        alpha = 20
#      else:
#        continue
#      color = QColor(color)
#      color.setAlpha(alpha)
#
#      fmt = QTextCharFormat()
#      fmt.setBackground(color)
#
#      length = len(surface)
#      start = offset - length
#      self.setFormat(start, length, fmt)
#
#@Q_Q
#class _QmlMeCabHighlighter(object):
#  def __init__(self):
#    self.enabled = False
#    self.document = None # QTextDocument
#
#  # WHY weakref do not work here? This will cause memory leak!
#  #@property
#  #def document(self):
#  #  """
#  #  @return  QTextDocument or None
#  #  """
#  #  try: return self._document_ref()
#  #  except (AttributeError, TypeError): pass
#
#  #@document.setter
#  #def document(self, value):
#  #  self._document_ref = weakref.ref(value) if value else None
#
#  @property
#  def highlighter(self):
#    try: return self._highlighter_ref()
#    except AttributeError:
#      obj = MeCabHighlighter(self.q)
#      #obj.setDocument(self.document)
#      self._highlighter_ref = weakref.ref(obj)
#      return self._highlighter_ref()
#
#  def hasHighlighter(self): return hasattr(self, '_highlighter_ref')
#
#  def clearDocument(self):
#    #self.q.setDocument(None)
#    self.document = None
#    self.highlighter.setDocument(None)
#    #self.q.documentChanged.emit(None)
#
##@QmlObject # jichi: why not needed?
#class QmlMeCabHighlighter(QObject):
#  def __init__(self, parent=None):
#    super(QmlMeCabHighlighter, self).__init__(parent)
#    self.__d = _QmlMeCabHighlighter(self)
#
#  def setDocument(self, doc):
#    d = self.__d
#    if d.document is not doc:
#      if doc:
#        doc.destroyed.connect(d.clearDocument)
#      d.document = doc
#      if d.hasHighlighter():
#        d.highlighter.setDocument(doc if d.enabled else None)
#      self.documentChanged.emit(doc)
#
#  documentChanged = Signal(QObject) # QtWidgets.QTextDocument
#  document = Property(QObject,
#      lambda self: self.__d.document,
#      setDocument,
#      notify=documentChanged)
#
#  def setEnabled(self, value):
#    d  = self.__d
#    if value != d.enabled:
#      d.enabled = value
#      d.highlighter.setDocument(d.document if value else None)
#      self.enabledChanged.emit(value)
#  enabledChanged = Signal(bool)
#  enabled = Property(bool,
#      lambda self: self.__d.enabled,
#      setEnabled,
#      notify=enabledChanged)

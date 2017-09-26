# coding: utf8
# api.py
# 8/10/2014

__all__ = 'MachineTranslator',

if __name__ == '__main__':
  import sys
  sys.path.append('..')

from sakurakit.skdebug import dwarn

from rule import RuleBuilder
RULE_BUILDER = RuleBuilder()

INPUT_LANGUAGE = 'ja'
INPUT_SEPARATOR = ''

# Rule

def createrule(source, target, language):
  """
  @param  source  unicode
  @param  target  unicode
  @param  language  str
  @return  rule.Rule or None
  """
  return RULE_BUILDER.createRule(INPUT_LANGUAGE, language, source, target)

# Analyzer

class _MachineAnalyzer:

  def __init__(self, cabocha):
    from frontend import Lexer
    self.lexer = Lexer(cabocha)

    #from midend import TreeBuilder
    #self.parser = TreeBuilder()

class MachineAnalyzer(object):

  def __init__(self, cabocha):
    """
    @param  cabocha  CaboCha.Parser
    """
    self.__d = _MachineAnalyzer(cabocha)

  def parseToString(self, text):
    """
    @param  text  unicode
    @return  unicode
    """
    ll = self.__d.lexer
    stream = ll.parse(text)
    return ll.dump(stream) if stream else ''

# Translator

class _MachineTranslator:

  def __init__(self, cabocha, language, tr, escape, sep, underline):
    self.language = language # str  language
    self.escape = escape # bool
    self.translateFunction = tr # function or None
    self.sep = sep # bool
    self.underline = underline # bool

    from frontend import Lexer
    self.lexer = Lexer(cabocha)

    from midend import TreeBuilder
    self.parser = TreeBuilder()

    from midend import RuleBasedTranslator
    self.rt = RuleBasedTranslator(fr=INPUT_LANGUAGE, to=language)

    from backend import MachineTranslator
    self.mt = MachineTranslator(tr=tr,
        fr=INPUT_LANGUAGE, frsep=INPUT_SEPARATOR,
        to=language, tosep=sep,
        escape=escape, underline=underline)

  # Translate

  def directTranslate(self, text): # unicode -> unicode
    return self.translateFunction(text, fr=INPUT_LANGUAGE, to=self.language) if self.translateFunction else ""

  def translate(self, source, tr=None): # unicode -> unicode
    if not source:
      return ""
    if not self.rt.rules:
      return self.directTranslate(source)

    stream = self.lexer.parse(source)
    if not stream:
      return self.directTranslate(source)
    #print self.lexer.dump(stream)

    stree = self.parser.parse(stream)
    if not stree:
      return self.directTranslate(source)
    #print stree.dumpTree()

    ttree = self.rt.translate(stree)
    if not ttree:
      stree.clearTree()
      return self.directTranslate(source)
    #print ttree.dumpTree()

    if ttree.language == self.language:
      target = ttree.unparseTree(self.sep)
    else:
      target = self.mt.translate(ttree, tr=tr)

    stree.clearTree()
    ttree.clearTree()

    return target

  def dumpTranslate(self, source): # unicode -> unicode
    ret = ''
    stree = ttree = None
    if source:
      if self.rt.rules:
        stream = self.lexer.parse(source)
        if stream:
          stree = self.parser.parse(stream)
          if stree:
            ttree = self.rt.translate(stree)
            if ttree:
              ret = ttree.dumpTree()
    for it in stree, ttree:
      if it:
        it.clearTree()
    return ret

class MachineTranslator(object):

  def __init__(self, cabocha, language, tr=None, escape=True, sep="", underline=True):
    """
    @param  cabocha  CaboCha.Parser
    @param  language  str  target language
    @param* r  function  (unicode text, str fr, str to) -> unicode
    @param* escape  bool
    @param* sep  str
    @param* underline  bool
    """
    self.__d = _MachineTranslator(cabocha, language, tr, escape, sep, underline)

  # Properties

  def language(self): return self.__d.language # -> str
  def setLanguage(self, v):
    d = self.__d
    if d.language != v:
      d.language = d.mt.to = d.rt.to = v
      for rule in d.rt.rules:
        rule.targetLanguage = v

  def isUnderline(self): return self.__d.underline # -> bool
  def setUnderline(self, t):
    d = self.__d
    if d.underline != t:
      d.underline = d.mt.underline = t

  def isEscape(self): return self.__d.escape # -> bool
  def setEscape(self, t):
    d = self.__d
    if d.escape != t:
      d.escape = d.mt.escape = t

  def separator(self): return self.__d.sep # -> str
  def setSeparator(self, v):
    d = self.__d
    if d.sep != v:
      d.sep = d.mt.tosep = v

  # Rule

  def ruleCount(self): return len(self.__d.rt.rules)
  def setRules(self, v): self.__d.rt.rules = v

  #def clearRules(self): self.__d.rt.rules = [] #.clear() # clear not used for thread-safety

  #def addRule(self, source, target):
  #  """
  #  @param  source  unicode
  #  @param  target  unicode
  #  """
  #  rule = self.__d.createRule(source, target)
  #  if rule:
  #    self.__d.rt.rules.append(rule)
  #  else:
  #    dwarn("failed to parse rule:", source, target)

  # Lexical utilities

  def splitSentences(self, text):
    """
    @param  text  unicode
    @return  [unicode]
    """
    return self.__d.lexer.splitSentences(text)

  # Translate

  def translate(self, text, tr=None):
    """
    @param  text  unicode
    @param* tr  function or None
    @return  unicode
    """
    return self.__d.translate(text, tr=tr)

  def dumpTranslate(self, text):
    """
    @param  text  unicode
    @param* tr  function or None
    @return  unicode
    """
    return self.__d.dumpTranslate(text)

if __name__ == '__main__':
  # Example (link, surface) pairs:
  # 太郎は花子が読んでいる本を次郎に渡した
  # 5 太郎
  # none は
  # 2 花子
  # none が
  # 3 読ん
  # none で
  # none いる
  # 5 本
  # none を
  # 5 次郎
  # none に
  # -1 渡し
  # none た
  #text = u"太郎は花子が読んでいる本を次郎に渡した。"
  #text = u"立派な太郎は、可愛い花子が読んでいる本を立派な次郎に渡した。"
  #text = u"あたしは、日本人です。"
  #text = u"あたしは日本人です。"

  #text = u"【綾波レイ】「ごめんなさい。こう言う時どんな顔すればいいのか分からないの。」"
  #text = u"ごめんなさい。こう言う時どんな顔すればいいのか分からないの。"
  #text = u"こう言う時どんな顔すればいいのか分からないの。"
  #text = u"こう言う時どんな顔すればいいのか分からないのか？"
  #text = u"こう言う時どんな顔すればいいのか分からないのか？"

  #text = u"私のことを好きですか？"
  #text = u"憎しみは憎しみしか生まない"

  #text = u"近未来の日本、多くの都市で大小の犯罪が蔓延。"
  #text = u"近未来の日本は、多くの都市で大小の犯罪が蔓延。"

  # baidu: 未来日本在许多城市，大大小小的犯罪蔓延。警察为主的治安机构功能正在逐渐失去了，晓東市是各种各样的犯罪对策进行的事在国内最高水平的治安，保持着。因此，寻求安全的人们聚积晓东市的物价高涨，其结果是资产家大量居住的街道。在这样的状况，所以资产家的女儿和她们（校长，护卫对象）保护保镖同时培养教育机关存在着。
  #text = u"近未来の日本、多くの都市で大小の犯罪が蔓延。警察を主とした治安機関は機能を失いつつあったが、暁東市は様々な犯罪対策を行なう事で国内でもトップクラスの治安を保っていた。そのため、安全を求める人々が集り暁東市の物価は高騰、その結果資産家が多く住む街となった。そのような状況のため、資産家の令嬢と彼女ら（プリンシパル、護衛対象者）を守るボディーガードを同時に育成する教育機関が存在している。"

  # baidu: 未来日本在许多城市，大大小小的犯罪蔓延。
  # manual: 近未来的日本，大大小小的犯罪在许多城市蔓延。
  #text = u"近未来の日本、多くの都市で大小の犯罪が蔓延。"
  #text = u"警察を主とした治安機関は機能を失いつつあったが、暁東市は様々な犯罪対策を行なう事で国内でもトップクラスの治安を保っていた。"
  #text = u"憎しみは憎しみしか生まない。"
  #text = u"あなたは誰ですか？"

  #text = u"こう言う時どんな顔すればいいのかわからないの。"
  text = u"こう言う"

  #text = u"お前の物は俺の物、俺の物も俺の物"
  #text = u"お前の物は俺の物"

  #self.rules = [rp.createRule(fr, to, *it) for it in (
  #  (u"顔", u"表情"),
  #  (u"(分から ない の 。)", u"不知道的。"),
  #  (u"どんな", u"怎样的"),
  #)]

  #from google import googletrans
  #f = googletrans.translate

  to = 'zhs'

  from sakurakit.skprof import SkProfiler
  from kingsoft import iciba
  tr = iciba.translate
  tr = None

  import CaboCha
  cabocha = CaboCha.Parser()

  ma = MachineAnalyzer(cabocha)

  mt = MachineTranslator(cabocha, language=to, underline=False, escape=True, tr=tr)

  rules = [createrule(k, v, to)
  for k,v in (
    #(u"顔", u"(表情)"),
    #(u"どんな", u"怎样的"),
    (u"(分から ない の 。)", u"(不 知道 的 。)"),
    #(u"(分から ない の 。)", u"不 知道 的 。"),
    #(u"(分から ない の 。)", u"不知道的。"),
    #(u"分から @x 。", u"不知道的。 @x"),
    #(u"(分から @x 。)", u"不知道的。 @x"),
    #(u"顔", u"表情"),
    #(u"(@x すれ ば いい の か)", u"不知道的。"),

    #(u"(顔 すれ ば いい の か)", u"不知道的。"),
    #(u"(@x すれ @y いい @z か)", u"不知道的。 @z"),
    #(u"@x すれ @y いい @z か", u"不知道的。 @z"),
    #(u"(こう $x)", u"这么 $x"),
    #(u"ない の 。", u"(不 知道 的 。)"),
    #(u"ない の 。", u"不知道的。"),

    #(u"((@x の) $y)", u"((@x 的) $y)"),

    #(u"($x どんな)", u"什么样的表情"),
    #(u"(顔 @y)", u"什么样的表情 @y"),
    #(u"($x どんな)(顔 @y)", u"($x 什么样的) (表情 @y)"),

    #(u"($x すれ ば いい の か)", u"($x 才好呢)"),
    #(u"(顔 @y)", u"(表情 @y)"),
    #(u"顔", u"表情"),
    #(u"($x どんな) (顔 @y)", u"($x 什么样的)(表情 @y)"),
    #(u"(わから ない の 。)", u"(不知道的 。)"),
    #(u"((こう 言う) 時)", u"这么说的时候"),

    #(u"($x 言う)", "$x debug"),
    #(u"(こう $y)", "test $y"),
  )]

  # ("($x 言う)", u"($x 说的)"),
  #import rule
  #rules.append(rule.Rule('ja', 'zhs',
  #  rule.PatternList((rule.PatternVariable(u"x"), u"言う")),
  #  rule.PatternList((rule.PatternVariable(u"x"), u"说的")),
  #))

  #rules.append(createrule(u"こう", u"这样", 'zhs'))

  mt.setRules(rules)

  #sys.setrecursionlimit(0x1000)

  #for s in mt.splitSentences(text):
  if True:
    s = text

    print "-- analysis --\n", ma.parseToString(s)

    print "-- sentence --\n", s

    print "-- dump-- \n", mt.dumpTranslate(s)

    with SkProfiler():
      t = mt.translate(s)

    print "-- output-- \n", t

    #stream = lexer.parse(s)
    #t = lexer.unparse(stream)
    #print "-- token stream == text ? %s  --\n" % (s == t), t
    #print "-- token stream --\n", lexer.dump(stream)

    #tree = parser.parse(stream)
    #print "-- parse tree --\n", tree.dumpTree()

    #print "-- unparse tree --\n", tree.unparseTree()

    #newtree = tr.translate(tree)
    #print "-- rule-based translated tree (lang = %s)--\n" % newtree.language, newtree.dumpTree()

    #if newtree.language == 'ja':
    #  ret = newtree.unparseTree()
    #  print "-- unparsed output --\n", ret
    #else:
    #  ret = mt.translate(newtree)
    #  print "-- machine translated output --\n", ret

    #tree.clearTree()
    #newtree.clearTree()

# EOF

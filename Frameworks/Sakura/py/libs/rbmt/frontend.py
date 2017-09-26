# coding: utf8
# frontend.py
# 9/29/2014

__all__ = 'Lexer',

import re
from itertools import imap
from unitraits import jpchars
from defs import ANY_LANGUAGE
from tree import Token

# Text processing

ANY_LANGUAGE_CHARS = r"0-9a-zA-Z０-９ａ-ｚＡ-Ｚ" + jpchars.s_kanji + jpchars.s_punct
ANY_LANGUAGE_RE = re.compile(ur"^[%s]$" % ANY_LANGUAGE_CHARS)
def guess_text_language(text): # unicode -> unicode or None
  if ANY_LANGUAGE_RE.match(text):
    return ANY_LANGUAGE

# Lexer

_SENTENCE_RE = re.compile(ur"([。？！」\n])(?![。！？）」\n]|$)")

__PARAGRAPH_DELIM = u"【】「」♪" # machine translation of sentence deliminator
_PARAGRAPH_SET = frozenset(__PARAGRAPH_DELIM)
_PARAGRAPH_RE = re.compile(r"([%s])" % ''.join(_PARAGRAPH_SET))

class Lexer:

  unparsesep = ''

  def __init__(self, cabochaParser, cabochaEncoding='utf8'):
    self.cabochaParser = cabochaParser # CaboCha.Parser
    self.cabochaEncoding = cabochaEncoding

  def _splitSentences(self, text):
    """
    @param  text  unicode
    @return  [unicode]
    """
    return _SENTENCE_RE.sub(r"\1\n", text).split("\n")

  def _splitParagraphs(self, text):
    """
    @param  text  unicode
    @return  [unicode]
    """
    return _PARAGRAPH_RE.split(text)

  def parse(self, text):
    """
    @param  unicode
    @return  stream
    """
    ret = list(self._iterparse(text))
    return ret[0] if len(ret) == 1 else ret

  def _iterparse(self, text):
    """
    @param  text  unicode
    @yield  stream
    """
    for p in self._splitParagraphs(text):
      if len(p) == 1 and p in _PARAGRAPH_SET:
        yield Token(p)
      else:
        for s in self._splitSentences(p):
          ret = self.parseSentence(s.strip())
          if ret:
            yield ret

  def parseSentence(self, text):
    return self._parse(self._tokenize(text))

  def _tokenize(self, text):
    """Tokenize
    @param  unicode
    @return  [int link, [Token]]]  token stream
    """
    encoding = self.cabochaEncoding
    stream = self.cabochaParser.parse(text.encode(encoding))

    MAX_LINK = 32768 # use this value instead of -1
    link = 0

    phrase = [] # [Token]
    ret = [] # [int link, [Token]]
    for i in xrange(stream.token_size()):
      token = stream.token(i)

      surface = token.surface.decode(encoding, errors='ignore')
      feature = token.feature.decode(encoding, errors='ignore')
      word = Token(surface, feature=feature)

      if token.chunk is not None:
        if phrase:
          ret.append((link, phrase))
          phrase = []
        link = token.chunk.link
        if link == -1:
          link = MAX_LINK
      phrase.append(word)

    if phrase:
      ret.append((link, phrase))
    return ret

  def _parse(self, phrases):
    """This is a recursive function.
    [@param  phrases [int link, [Token]]]  token stream
    @return  stream
    """
    if not phrases: # This should only happen at the first iteration
      return []
    elif len(phrases) == 1:
      return phrases[0][1]
    else: # len(phrases) > 2
      lastlink, lastphrase = phrases[-1]
      if len(lastphrase) == 1:
        ret = [lastphrase[0]]
      else:
        ret = [lastphrase]
      l = []

      for i in xrange(len(phrases) - 2, -1, -1):
        link, phrase = phrases[i]
        if lastlink > link:
          l.insert(0, (link, phrase))
        else:
          if l:
            c = self._parse(l)
            if isinstance(c, list) and len(c) == 1:
              c = c[0]
            ret.insert(0, c)
          l = [(link, phrase)]

      c = self._parse(l)
      if isinstance(c, list) and len(c) == 1:
        c = c[0]
      ret.insert(0, c)
      return ret

  # For cebug usage
  def dump(self, x):
    """
    @param  x  Token or [[Token]...]
    @return  s
    """
    if isinstance(x, Token):
      return x.dump()
    else:
      return "(%s)" % ' '.join(imap(self.dump, x))

  def unparse(self, x):
    """
    @param  x  Token or [[Token]...]
    @return  unicode
    """
    if isinstance(x, Token):
      return x.unparse()
    else:
      return self.unparsesep.join(imap(self.unparse, x))

# EOF

# coding: utf8
# richutil.py
# 6/27/2014 jichi

import re
import pyrich

_RP = pyrich.RichRubyParser()

def containsRuby(text):
  """
  @param  text  unicode
  @return  bool
  """
  return '[ruby=' in text

def renderRubyToHtmlTable(text, width, rbFont, rtFont, cellSpace=1, wordWrap=True):
  """
  @param  text  unicode
  @param  width  int
  @param  rbFont  QFontMetrics
  @param  rtFont  QFontMetrics
  @param  cellSpace  int
  @param  wordWrap  bool
  """
  if not containsRuby(text):
    return text
  return _RP.renderToHtmlTable(text, width, rbFont, rtFont, cellSpace, wordWrap)

def createRuby(rb, rt):
  """
  @param  rb  unicode
  @param  rt  unicode
  @return  unicode
  """
  if rb and rt:
    return '[ruby=%s]%s[/ruby]' % (rt, rb)
  return rb

_rx_ruby1 = re.compile(r'\[ruby=.+?\](.+?)\[/ruby\]')
def removeRuby(text):
  """
  @param  text  unicode
  @return  unicode
  """
  if not containsRuby(text):
    return text
  return _rx_ruby1.sub(r'\1', text)

_rx_ruby2 = re.compile(r'\[ruby=(.+?)\](.+?)\[/ruby\]')
def renderRubyToPlainText(text):
  """
  @param  text  unicode
  @return  unicode
  """
  if not containsRuby(text):
    return text
  return _rx_ruby2.sub(r'\2(\1)', text)

# EOF

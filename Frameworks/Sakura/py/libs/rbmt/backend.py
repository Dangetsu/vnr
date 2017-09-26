# coding: utf8
# backend.py
# 10/4/2014

__all__ = 'MachineTranslator',

from defs import ANY_LANGUAGE

class MachineTranslator:

  def __init__(self, fr, to, tr=None, escape=True, frsep="", tosep="", underline=True):
    self.fr = fr # str
    self.to = to # str
    self.tr = tr # function or None
    self.frsep = frsep # str
    self.tosep = tosep # str
    self.escape = escape # bool
    self.underline = underline # bool

  def translate(self, tree, tr=None):
    """
    @param  tree  Node
    @param* tr  function or None
    @return  unicode
    """
    ret = self._translateTree(tree, tr=tr)
    if not ret:
      return ''
    if self.underline and not self.tosep:
      ret = ret.replace("> ", ">")
      ret = ret.replace(" <", "<")
    return ret

  def _renderText(self, text):
    return self._underlineText(text) if self.underline else text
  def _underlineText(self, text):
    return '<span style="text-decoration:underline">%s</span>' % text

  def _translateText(self, text, tr=None):
    """
    @param  text  unicode
    @param* tr  function or None
    @return  unicode
    """
    tr = tr or self.tr
    return tr(text, fr=self.fr, to=self.to) if tr else text

  def _translateTree(self, x, tr=None):
    """
    @param  x  Node
    @param  tr  function or None
    @return  unicode
    """
    if x.language == self.to or x.language == ANY_LANGUAGE:
      return self._renderText(x.unparseTree(self.tosep))
    elif x.language == self.fr or x.token:
      return self._translateText(x.unparseTree(self.frsep), tr=tr)
    elif not x.language and x.children:
      #return self.unparsesep.join(imap(self._translateTree, x.children))
      if self.escape:
        return self._translateEscape(x, tr=tr)
      else:
        return self._translateText(x.unparseTree(self.frsep), tr=tr)
    else:
      dwarn("unreachable code path")
      return x.unparseTree(self.frsep)

  def _translateEscape(self, x, tr=None):
    """
    @param  x  Node
    @param* tr  function or None
    @return  unicode
    """
    esc = {}
    t = self._prepareEscape(x, esc)
    t = self._translateText(t, tr=tr)
    if not t:
      return ""
    elif not esc:
      return t
    else:
      return self._restoreEscape(t, esc)

  def _restoreEscape(self, t, esc):
    """
    @param  t  unicode
    @param  esc  dict
    @return  unicode
    """
    keys = esc.keys()
    keys.sort(key=len, reverse=True)
    for k in keys:
      t = t.replace(k, self._renderText(esc[k]))
    return t

  ESCAPE_KEY = "9%i.648"
  def _prepareEscape(self, x, esc):
    """
    @param  x  Node
    @param  esc  dict
    @return  unicode
    """
    if x.language == self.to:
      text = x.unparseTree(self.tosep)
      if text:
        return self._escapeText(text, esc)
    elif x.token:
      return x.token.text
    elif x.children:
      return self.frsep.join((self._prepareEscape(it, esc) for it in x.children))
    return ''

  def _escapeText(self, text, esc):
    """
    @param  text  unicode
    @param  esc  dict
    @return  unicode
    """
    key = self.ESCAPE_KEY % len(esc)
    esc[key] = text
    return key + ' '

# EOF

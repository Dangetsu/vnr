# coding: utf8
# rule.py
# 8/10/2014
#
# Rules
# The expression is mostly borrowed from PERL.
#
# - Regular expression requires back-slashed quotes, such as /This is a regex/.
# - String with spaces require quotes, such as "a string with space".
# - $x: single tree node
# - @x: a list of sibling tree nodes
# - $x:n Represent a noun, or use $x:v to represent a verb
#
# Examples:
# (@x の)   => (@x 的)
# (@x で)   => (在 @x)
#
# $x=/regex/:n   the :n means $x is a noun, similarly, $vt, $v
# $x=/regex/:n:v  either .noun or .verb
# It is just like CSS class selector, but the relation is or instead of and.
#
# @x の   => @x 的
# @x で   => 在 @x
#
# (@x=/.+/ の)  => (@x 的)
# (@x=/.+/ で)  => (在 @x)
#
# Parse tree:
# 私のことを好きですか
# (((私 の) (こと を)) (好きですか?))
#
# Non-node group:   (?:A B C)  the "(?:" means it is not groupped??

__all__ = 'Rule', 'RuleBuilder'

import re
from collections import deque
from sakurakit.skdebug import dwarn
from defs import ANY_LANGUAGE
from tree import Node, Token, EMPTY_NODE

# Patterns

class PatternList(list):
  __slots__ = 'exactMatching',
  def __init__(self, *args, **kwargs):
    super(PatternList, self).__init__(*args, **kwargs)
    self.exactMatching = False # bool, whether has outer parenthesis

  @property
  def lengthFixed(self): # -> bool
    for it in self:
      if isinstance(it, PatternVariable) and it.type == PatternVariable.TYPE_LIST:
        return False
    return True

class PatternVariable(object):
  __slots__ = 'name', 'type'

  TYPE_SCALAR = 0   # such as $x
  TYPE_LIST = 1     # such as @x

  SIGN_SCALAR = '$'
  SIGN_LIST = '@'

  def __init__(self, name="", type=TYPE_SCALAR):
    self.name = name # str
    self.type = type # int

  def dump(self):
    """
    @return  str
    """
    return (self.SIGN_LIST if self.type == self.TYPE_LIST else self.SIGN_SCALAR) + self.name

  @classmethod
  def signType(cls, c): # str -> int or None
    if c == cls.SIGN_SCALAR:
      return cls.TYPE_SCALAR
    if c == cls.SIGN_LIST:
      return cls.TYPE_LIST

# Matchers

class MatchedVariables(dict): # {str name, Node or [Node]}

  __slots__ = tuple()

  def clearTree(self):
    if self:
      for it in self.itervalues():
        self._clearValue(it)
      self.clear()

  def addCopy(self, k, v):
    """
    @param  k  str
    @param  v  Node or [Node]
    """
    old = self.get(k)
    if old:
      dwarn("warning: duplicate variable definition: %s" % k)
      self._clearValue(v)
    self[k] = self._copyValue(v)

  @staticmethod
  def _clearValue(v):
    """
    @param  v  Node or [Node]
    """
    if v:
      if isinstance(v, Node):
        v.clearTree()
      else:
        for it in v:
          it.clearTree()

  @staticmethod
  def _copyValue(v):
    """
    @param  v  Node or [Node]
    @return  Node or [Node]
    """
    if isinstance(v, Node):
      return v.copyTree()
    else:
      return [it.copyTree() for it in v]

class MatchedList(object): # for matching PatternList
  __slots__ = (
    'nodes',
    'captureCount', 'captureStarts', 'captureStops', 'captureVariables',
  )
  def __init__(self, nodes):
    self.nodes = nodes # [Node]
    self.captureCount = 0 # int
    self.captureStarts = [] # [int]
    self.captureStops = [] # [int]  excluding
    self.captureVariables = [] # [MatchedVariables]

  def clearTree(self):
    if self.captureVariables:
      for it in self.captureVariables:
        it.clearTree()
      self.captureVariables = []

# Rule

class Rule(object):
  __slots__ = (
    'source', 'target',
    'sourceType', 'targetType',
    'sourceLanguage', 'targetLanguage',
  )

  TYPE_NONE = 0
  TYPE_STRING = 1   # str or unicode, single node, such as: あ
  TYPE_LIST = 2     # PatternList, normal tree, such as: (あ)
  TYPE_VAR = 3      # PatternVariable, scalar or list variable, such as $x or @x

  def __init__(self, sourceLanguage, targetLanguage, source, target):
    self.source = source # list or unicode
    self.target = target # list or unicode
    self.sourceType = self.typeName(source)
    self.targetType = self.typeName(target)
    self.sourceLanguage = sourceLanguage # str
    self.targetLanguage = targetLanguage # str

  def priority(self): # -> int  the larger the higher priority
    return len(self.source) if self.sourceType == self.TYPE_LIST else 0

  @classmethod
  def typeName(cls, x):
    """
    @param  x  list or str or unicode
    @return  str
    """
    if not x:
      return cls.TYPE_NONE
    if isinstance(x, basestring):
      return cls.TYPE_STRING
    if isinstance(x, list):
      return cls.TYPE_LIST
    if isinstance(x, PatternVariable):
      return cls.TYPE_VAR

  def translate(self, x):
    """
    @param  x  Node
    @return  Node
    """
    return self._translate(x)

  def _translate(self, x):
    """
    @param  x  Node
    @return  Node
    """
    if not x or (self.sourceType != self.TYPE_VAR and x.language in (self.targetLanguage, ANY_LANGUAGE)):
      return x
    vars = MatchedVariables()
    m = self.matchSource(x, vars)
    if m:
      x = self.updateTarget(x, m, vars)
      if isinstance(m, MatchedList):
        m.clearTree()
    vars.clearTree()
    return x

  def matchSource(self, x, vars):
    """
    @param  x
    @param  vars  MatchedVariables
    @return  bool or MatchedList or None
    """
    return bool(self.source) and self._matchSource(self.source, x, vars)

  def _matchSource(self, source, x, vars):
    """
    @param  source  list or unicode
    @param  x  Node
    @param  vars  MatchedVariables
    @return  bool or MatchedList or None
    """
    if not x:
      return
    sourceType = self.typeName(source)
    if sourceType != self.TYPE_VAR and x.language in (self.targetLanguage, ANY_LANGUAGE):
      return
    if sourceType == self.TYPE_STRING:
      if x.token:
        return source == x.token.text
    elif sourceType == self.TYPE_LIST:
      if x.children:
        if source.lengthFixed:
          if source.exactMatching or len(source) == len(x.children):
            return self._exactMatchFixedSourceList(source, x.children, vars)
          elif len(source) < len(x.children):
            return self._matchFixedSourceList(source, x.children, vars)
        else:
          if source.exactMatching:
            return self._exactMatchVariantSourceList(source, x.children, vars)
          else:
            return self._matchVariantSourceList(source, x.children, vars)
    elif sourceType == self.TYPE_VAR:
      if source.type == PatternVariable.TYPE_SCALAR:
        if not x.isEmpty():
          vars.addCopy(source.name, x)
          return True
      elif source.type == PatternVariable.TYPE_LIST:
        if x.children:
          vars.addCopy(source.name, x.children)
          return True
        elif x.token:
          vars.addCopy(source.name, [x])
          return True

  def _exactMatchFixedSourceList(self, source, nodes, *args):
    """Exact match list with fixed length.
    @param  source  list
    @param  nodes  list
    @param* vars  MatchedVariables
    @return  bool
    """
    if len(source) == len(nodes):
      for s,c in zip(source, nodes):
        if not self._matchSource(s, c, *args):
          return False
      return True
    return False

  def _matchFixedSourceList(self, source, nodes, *args):
    """Non-exact match list with fixed length.
    @param  source  list
    @param  nodes  list
    @param* vars  MatchedVariables
    @return  MatchedList or None
    """
    starts = []
    sourceIndex = 0
    for i,n in enumerate(nodes):
      if sourceIndex == 0 and i + len(source) > len(nodes):
        break
      s = source[sourceIndex]
      if not self._matchSource(s, n, *args):
        sourceIndex = 0
      elif sourceIndex == len(source) - 1:
        starts.append(i - sourceIndex)
        sourceIndex = 0
      else:
        sourceIndex += 1
    if starts:
      m = MatchedList(nodes)
      m.captureCount = len(starts)
      m.captureStarts = starts
      m.captureStops = [it + len(source) for it in starts]
      return m

  def _exactMatchVariantSourceList(self, source, nodes, vars):
    """Exact match list with variant length.
    @param  source  list
    @param  nodes  list
    @param  vars  MatchedVariables
    @return  bool
    """
    if not nodes or not source or len(source) > len(nodes):
      return False

    nodes = deque(nodes)
    source = deque(source)

    while source and nodes:
      # right to left
      while source and nodes and not (
          isinstance(source[-1], PatternVariable) and source[-1].type == PatternVariable.TYPE_LIST):
        s = source.pop()
        n = nodes.pop()
        if not self._matchSource(s, n, vars):
          return False
      # left to right
      while source and nodes and not (
          isinstance(source[0], PatternVariable) and source[0].type == PatternVariable.TYPE_LIST):
        s = source.popleft()
        n = nodes.popleft()
        if not self._matchSource(s, n, vars):
          return False
      if (source
          and isinstance(source[0], PatternVariable) and source[0].type == PatternVariable.TYPE_LIST
          and isinstance(source[-1], PatternVariable) and source[-1].type == PatternVariable.TYPE_LIST):
        # This branch will always exist
        if not nodes:
          return False
        right = source.pop()
        if not source: # s is the only PatternVariable
          vars.addCopy(right.name, nodes)
          return True
        else:
          if len(nodes) < 2:
            return False
          # Recursive match
          left = source.popleft()
          if not source:
            if len(nodes) == 2:
              vars.addCopy(left.name, [nodes[0]])
              vars.addCopy(right.name, [nodes[-1]])
              return True
            else:
              dwarn("warning: ambiguous list variable capture: %s, %s" % (left.name, right.name))
              vars.addCopy(left.name, [nodes[0]])
              del nodes[0]
              vars.addCopy(right.name, nodes)
              return True
          if len(nodes) < 3:
            return False
          leftnodes = [nodes.popleft()]
          rightnodes = [nodes.pop()]
          m = self._matchFirstSourceList(list(source), list(nodes))
          if m:
            start = m.captureStarts[0]
            stop = m.captureStops[0]

            newvars = m.captureVariables[0]
            vars.update(newvars) # memory might leak here if multiple vars having the same name
            #m.clearTree() # tree is not cleared as new vars takes the ownership of the copied nodes

            if start:
              for i in range(start):
                leftnodes.append(nodes[i])
            if stop < len(nodes):
              for i in range(len(nodes) - 1, stop - 1, -1):
                rightnodes.insert(0, nodes[i])
            vars.addCopy(left.name, leftnodes)
            vars.addCopy(right.name, rightnodes)
            return True
          return False
    return not source and not nodes

  def _matchFirstSourceList(self, source, nodes, *args):
    """Non-exact match list with fixed or variant length.
    @param  source  list
    @param  nodes  list
    @param* vars  MatchedVariables  ignored
    @return  MatchedList or None
    """
    if not nodes or not source or len(source) > len(nodes):
      return
    matchedStart = 0
    matchedStop = -1
    sourceIndex = 0
    vars = MatchedVariables()
    for i,n in enumerate(nodes):
      if sourceIndex == 0 and i + len(source) > len(nodes):
        break
      s = source[sourceIndex]
      # List
      if self.typeName(s) == self.TYPE_VAR and s.type == PatternVariable.TYPE_LIST:
        if sourceIndex == len(source) - 1: # the list variable is at the end
          if i < len(nodes) - 1: # more nodes
            vars.addCopy(s.name, nodes[i:])
            matchedStop = len(nodes)
          break
        # Look ahead
        snext = source[sourceIndex+1]
        if self.typeName(snext) == self.TYPE_VAR and snext.type == PatternVariable.TYPE_LIST:
          dwarn("warning: adjacent list variables is not supported")
          break
        m = self._matchFirstSourceList(source[sourceIndex+1:], nodes[i+1:], *args) # recursion
        if m: # successful
          matchedStop = i + m.captureStops[0] + 1
          vars.update(m.captureVariables[0])
          vars.addCopy(s.name, nodes[i:i + m.captureStarts[0] + 1])
          break
        # reset search
        sourceIndex = 0
        matchedStart = i + 1
        vars.clearTree()
      # Scalar
      elif not self._matchSource(s, n, vars): # reset search
        sourceIndex = 0
        matchedStart = i + 1
        vars.clearTree()
      elif sourceIndex == len(source) - 1: # successful
        matchedStop = i + 1
        break
      else:
        sourceIndex += 1
    if matchedStop >= 0:
      m = MatchedList(nodes)
      m.captureCount = 1
      m.captureStarts = matchedStart,
      m.captureStops = matchedStop,
      m.captureVariables = vars,
      return m

    vars.clearTree()

  def _matchVariantSourceList(self, source, nodes, *args):
    """Non-exact match list with variant length.
    @param  source  list
    @param  nodes  list
    @param* vars  MatchedVariables
    @return  MatchedList or None
    """
    ret = MatchedList(nodes)
    nodeIndex = 0
    while nodes and source and len(source) <= len(nodes):
      m = self._matchFirstSourceList(source, nodes, *args)
      if not m:
        break
      start = m.captureStarts[0]
      stop = m.captureStops[0]
      vars = m.captureVariables[0]
      ret.captureCount += 1
      ret.captureStarts.append(nodeIndex + start)
      ret.captureStops.append(nodeIndex + stop)
      ret.captureVariables.append(vars)
      nodeIndex += stop
      nodes = nodes[stop:]

    if ret.captureCount:
      return ret

  def updateTarget(self, x, m, vars):
    """
    @param  x  Node
    @param* m  bool or MatchedList or None
    @param* vars  MatchedVariables
    @return  Node
    """
    if m is not None:
      if isinstance(m, MatchedList):
        if m.captureCount:
          fragment = (self.sourceType == self.TYPE_LIST and self.targetType == self.TYPE_LIST
              and self.source.exactMatching)
          for i in range(m.captureCount - 1, -1, -1):
            start = m.captureStarts[i]
            stop = m.captureStops[i]
            x.removeChildren(start, stop)
            if self.target:
              v = m.captureVariables[i] if m.captureVariables else vars
              if fragment:
                x.insertChildren(start, self.createTargetList(v))
              else:
                x.insertChild(start, self.createTarget(v))
          return x

    y = self.createTarget(vars)
    x.assign(y, skip='parent')
    return x

  def createTarget(self, vars):
    """
    @param  vars  MatchedVariables
    @return  Node
    """
    ret = self._createTarget(self.target, vars)
    ret.fragment = bool(self.targetType == self.TYPE_LIST) and not self.target.exactMatching
    return ret

  def createTargetList(self, vars):
    """
    @param  vars  MatchedVariables
    @return  [Node]
    """
    if self.target:
      islist = self.targetType == self.TYPE_LIST
      if islist:
        return self._createTargetList(self.target, vars)
      isscalar = (
          self.targetType == self.TYPE_STRING
          or self.targetType == self.TYPE_VAR and self.target.type == PatternVariable.TYPE_SCALAR)
      if isscalar:
        return [self._createTarget(self.target, vars)]
    return []

  def _createTargetList(self, target, vars):
    """
    @param  target  list
    @param  vars  MatchedVariables
    @return  [Node]
    """
    #return [self._createTarget(it, vars) for it in target]
    ret = []
    for it in target:
      node = self._createTarget(it, vars)
      if not node.isEmpty():
        if node.children and self.typeName(it) == self.TYPE_VAR and it.type == PatternVariable.TYPE_LIST:
          ret.extend(node.children)
        else:
          ret.append(node)
    return ret

  def _createTarget(self, target, vars):
    """
    @param  target  list or unicode
    @param  vars  MatchedVariables
    @return  Node
    """
    if target:
      targetType = self.typeName(target)
      if targetType == self.TYPE_STRING:
        return Node(Token(target),
            language=self.targetLanguage)
      if targetType == self.TYPE_LIST:
        return Node(children=self._createTargetList(target, vars),
            language='' if vars else self.targetLanguage)
      if targetType == self.TYPE_VAR:
        value = vars.get(target.name)
        if value is None:
          text = target.dump()
          return Node(Token(text), language=self.sourceLanguage)
        if target.type == PatternVariable.TYPE_SCALAR:
          if isinstance(value, Node):
            return value.copyTree()
        elif target.type == PatternVariable.TYPE_LIST:
          if isinstance(value, list):
            return Node(children=[it.copyTree() for it in value],
                language=self.sourceLanguage)
    return EMPTY_NODE

# Rule parser

class RuleBuilder:

  def createRule(self, sourceLanguage, targetLanguage, source, target):
    s = self.parse(source)
    if s:
      t = self.parse(target)
      return Rule(sourceLanguage, targetLanguage, s, t)

  def parse(self, text):
    """
    @param  text
    @return  list or unicode
    """
    if not text:
      return None

    if not self._containsSpecialCharacter(text):
      if ' ' not in text:
        return text
      l = text.split()
      return l[0] if len(l) == 1 else PatternList(l)

    return self._parse(self._tokenize(text))

  SPECIAL_CHARS = '()$@'

  def _containsSpecialCharacter(self, text):
    """
    @param  text  unicode
    @return  bool
    """
    for c in text:
      if c in self.SPECIAL_CHARS:
        return True
    return False

  re_split = re.compile(r'([%s])|\s' % SPECIAL_CHARS)
  def _tokenize(self, text):
    """
    @param  text
    @return  list
    """
    return filter(bool, self.re_split.split(text))

  def _parse(self, l):
    """
    @param  l  list
    @return  list or unicode or None
    """
    if not l:
      return
    l = deque(l)
    s = [] # stack
    while l:
      x = l.popleft()
      if x in ('$', '@'):
        if not l:
          dwarn("error: dangle character: %s" % x)
          return
        y = l.popleft()
        if y in self.SPECIAL_CHARS:
          dwarn("error: using special characters as variable name is not allowed: %s" % y)
          return
        s.append(PatternVariable(y,
            PatternVariable.signType(x)))
      elif x != ')':
        s.append(x)
      else:
        # reduce until '('
        p = PatternList()
        p.exactMatching = True
        while s:
          x = s.pop()
          if x == '(':
            break
          p.insert(0, x)
        if x != '(':
          dwarn("error: unbalanced parenthesis")
          return
        if p:
          s.append(p)
    if not s:
      return
    # reduce until bol
    if '(' in s:
      dwarn("error: unbalanced parenthesis")
      return
    return s[0] if len(s) == 1 else PatternList(s)

# EOF

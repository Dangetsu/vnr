# coding: utf8
# tree.py
# 8/10/2014

__all__ = 'Token', 'Node'

# Tree

class Token:
  def __init__(self, text='', feature=''):
    self.text = text # unicode
    self.feature = feature # unicode

  def unparse(self): return self.text
  def dump(self): return self.text

class Node(object): # tree node
  __slots__ = (
    'children',
    'parent',
    'token',
    'language',
    'fragment',
  )

  def __init__(self, token=None, children=None, parent=None, language='', fragment=False):
    self.children = children # [Node] or None
    self.parent = parent # Node
    self.token = token # token
    self.language = language # str
    self.fragment = fragment # bool # inncomplete node

    if children:
      for it in children:
        it.parent = self

  def isEmpty(self): return not self.token and not self.children

  # Delete

  def clear(self):
    self.children = None
    self.parent = None
    self.token = None
    self.fragment = False
    self.language = ''

  def clearTree(self): # recursively clear all children
    if self.children:
      for it in self.children:
        it.clearTree()
    self.clear()

  # Update

  def update(self, **kwargs):
    for k,v in kwargs.iteritems():
      setattr(self, k, v)
      if k == 'children' and v:
        for it in v:
          it.parent = self

  def assign(self, that, skip=[]):
    """
    @param  that  Node
    """
    for k in self.__slots__:
      if not skip or k not in skip:
        v = getattr(that, k)
        setattr(self, k, v)
        if k == 'children' and v:
          for it in v:
            it.parent = self

  # Copy

  def copy(self, **kwargs):
    kw = {it:getattr(self, it) for it in self.__slots__}
    if kwargs:
      kw.update(kwargs)
    return Node(**kw)

  def copyTree(self):
    return self.copy(children=[it.copyTree() for it in self.children]) if self.children else self.copy()

  # Children

  def clearChildren(self):
    if self.children:
      for it in self.children:
        if it.parent is self:
          it.parent = None
    self.children = None

  def setChildren(self, l):
    self.clearChildren()
    self.children = l
    if l:
      for it in l:
        it.parent = self

  def appendChild(self, node):
    """
    @param  node  Node
    """
    self.children.append(node)
    node.parent = self

  def prependChild(self, node):
    """
    @param  node  Node
    """
    self.children.insert(0, node)
    node.parent = self

  def appendChildren(self, l):
    """
    @param  l  [Node]
    """
    for it in l:
      self.appendChild(it)

  def prependChildren(self, l):
    """
    @param  l  [Node]
    """
    for it in l:
      self.prependChild(it)

  def insertChild(self, i, node):
    """
    @param  i  int
    @param  node  Node
    """
    self.children.insert(i, node)
    node.parent = self

  def insertChildren(self, i, l):
    """
    @param  i  int
    @param  node  Node
    """
    for it in reversed(l):
      self.insertChild(i, it)

  def removeChild(self, i):
    """
    @param  i  int
    """
    node = self.children.pop(i)
    if node.parent is self:
      node.parent = None

  def removeChildren(self, start, stop):
    """
    @param  start  int
    @param  stop  int
    """
    for i in range(start, stop):
      self.removeChild(start)

  #def compactAppend(self, x):
  #  """
  #  @param  node  Node or list
  #  """
  #  if isinstance(x, Node):
  #    if not x.isEmpty():
  #      self.appendChild(x)
  #  elif x:
  #    if len(x) == 1:
  #      self.appendChild(x[0])
  #    else:
  #      self.appendChildren(x)

  # Output

  def dumpTree(self): # recursively clear all children
    """
    @return  unicode
    """
    if self.token:
      return self.token.dump()
    elif self.children:
      return "(%s)" % ' '.join((it.dumpTree() for it in self.children))
    else:
      return ''

  def unparseTree(self, sep=''): # recursively clear all children
    """
    @param  sep  unicode
    @return  unicode
    """
    if self.token:
      return self.token.unparse()
    elif self.children:
      return sep.join((it.unparseTree(sep) for it in self.children))
    else:
      return ''

EMPTY_NODE = Node()

# EOF

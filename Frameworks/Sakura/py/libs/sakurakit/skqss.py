# coding: utf8
# skqss.py
# 3/29/2013 jichi

import re

# Style sheets -

def qss(q, value=None):
  """
  @param  q  QObject
  @param  value  unicode or None
  @return  unicode or None
  """
  if value is None:
    return q.styleSheet()
  else:
    q.setStyleSheet(value)

## Style ID ##

def id_(q, value=None):
  """
  @param  q  QObject
  @param  value  unicode or None
  @return  unicode or None
  """
  if value is None:
    return q.objectName()
  else:
    q.setObjectName(value)

## Style classes ##

def class_(q, value=None):
  """
  @param  q  QObject
  @param  value  unicode or None
  @return  unicode or None
  """
  c = q.property('class')
  if value is None:
    return c
  elif value != c:
    q.setProperty('class', value)
    q.setStyleSheet(q.styleSheet()) # invalidate style sheet

def hasclass(q, value):
  """
  @param  q  QObject
  @param  value  unicode
  @return  bool
  """
  if not value:
    return False
  c = q.property('class')
  if not c:
    return False
  if c == value:
    return True
  for it in c.split():
    if it == value:
      return True
  return False

def removeclass(q, value=None):
  """
  @param  q  QObject
  @param* value  unicode or None
  @return  QObject  q
  """
  c = class_(q)
  if c:
    if value is None:
      class_(q, '')
    else:
      # value is not escaped to improve performance
      c = re.sub(r'\b%s\b\s*' % value, '', c)
      class_(q, c)
  return q

def addclass(q, value):
  """
  @param  q  QObject
  @param  value  unicode
  @return  QObject  q
  """
  c = class_(q)
  if not c:
    class_(q, value)
  else:
    class_(q, ' '.join((c, value)))
  return q

def addclasses(q, values):
  """
  @param  q  QObject
  @param  values  [unicode]
  @return  QObject  q
  """
  return addclass(q, ' '.join(values))

def toggleclass(q, value, t=None):
  """
  @param  q  QObject
  @param  value  unicode
  @param  t  bool
  @return  QObject  q
  """
  if t is None:
    t = not hasclass(value)
  return addclass(q, value) if t else removeclass(q, value)

# EOF

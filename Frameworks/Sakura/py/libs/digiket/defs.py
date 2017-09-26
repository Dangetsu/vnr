# coding: utf8
# defs.py
# 6/18/2014 jichi

def toitemkey(id):
  """
  @param  id  int or str
  @return  str
  """
  try: return 'ITM%07d' % long(id)
  except: return ''

def fromitemkey(key):
  """
  @param  key  str
  @return  int
  """
  if isinstance(key, (int, long)):
    return key
  elif isinstance(key, basestring):
    if key.startswith('ITM'):
      key = key[3:]
    key = key.lstrip('0')
  try: return long(key)
  except: return 0

# EOF

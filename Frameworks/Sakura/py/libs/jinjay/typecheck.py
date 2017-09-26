# coding: utf8
# 12/16/2014
# jinjay/typecheck.py

def parseint(s): # str -> int or None
  try: return int(s)
  except: pass

def parsefloat(s): # str -> float or None
  try: return float(s)
  except: pass

def parsenumber(s): # sr -> float or int or None
  r = parsefloat(s)
  if r is None:
    r = parseint(s)
  return r

def isint(s): return parseint(s) is not None
def isfloat(s): return parsefloat(s) is not None
def isnumber(s): return parsenumber(s) is not None

# EOF

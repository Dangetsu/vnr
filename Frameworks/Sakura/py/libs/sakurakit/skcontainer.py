# coding: utf8
# skcontainer.py
# 8/27/2013 jichi

# http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order
def uniquelist(seq):
  """
  @param[in]  seq  iterable
  @return  list
  """
  seen = set()
  seen_add = seen.add
  return [it for it in seq if it not in seen and not seen_add(it)]

def mergedicts(x, y):
  """Items in x are preferred
  @param[in]  x  dict
  @param[in]  y  dict
  @return  dict
  """
  r = x.copy()
  r.update(y)
  return r

if __name__ == '__main__':
  print mergedict({1:2},{1:3})

# EOF

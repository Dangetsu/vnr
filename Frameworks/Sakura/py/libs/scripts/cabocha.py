# coding: utf8
# jmdict.py
# 2/14/2014 jichi
if __name__ == '__main__':
  import sys
  sys.path.append('..')

def get(dic):
  """
  @param  dic  str  such as ipadic or unidic
  @return  bool
  """
  import rc
  return rc.runscript('getcabocha.py', (dic,))

if __name__ == "__main__":
  get('unidic')

# EOF

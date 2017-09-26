# coding: utf8
# stardict.py
# 2/14/2014 jichi
if __name__ == '__main__':
  import sys
  sys.path.append('..')

def get(lang):
  """
  @param  lang  str  such as ja-en
  @return  bool
  """
  import rc
  if 'vi' in lang:
    s = 'getovdp.py'
  else:
    s = 'getstardict.py'
  return rc.runscript(s, (lang,))

if __name__ == "__main__":
  get('ja-vi')

# EOF

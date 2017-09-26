# coding: utf8
# font.py
# 2/14/2014 jichi
if __name__ == '__main__':
  import sys
  sys.path.append('..')

def get(family):
  """
  @param  family  str  such as hanazono
  @return  bool
  """
  import rc
  return rc.runscript('getfont.py', (family,))

if __name__ == "__main__":
  get('hanazono')

# EOF

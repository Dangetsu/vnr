# coding: utf8
# unidic.py
# 2/14/2014 jichi
if __name__ == '__main__':
  import sys
  sys.path.append('..')

def get():
  """
  @return  bool
  """
  import rc
  return rc.runscript('getunidic.py')

if __name__ == "__main__":
  get()

# EOF

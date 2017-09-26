# coding: utf8
# apploc.py
# 2/10/2013 jichi
if __name__ == '__main__':
  import sys
  sys.path.append('..')

#from sakurakit.skdebug import dprint

def get():
  """
  @return  bool
  """
  import rc
  return rc.runscript('getapploc.py')

remove = get

if __name__ == "__main__":
  get()

# EOF

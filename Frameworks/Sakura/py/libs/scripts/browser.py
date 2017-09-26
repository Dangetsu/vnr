# coding: utf8
# browser.py
# 3/22/2014 jichi
if __name__ == '__main__':
  import sys
  sys.path.append('..')

def open(urls=[], debug=False):
  """
  @param  vids  [str]  youtube video ID
  @param* path  unicode or None  default is on the Desktop
  @return  bool

  Example: python . -o "C:\Users\jichi\Desktop\%(title)s.%(ext)s" C9mjluSx40s
  """
  if isinstance(urls, basestring):
    urls = [urls]
  import rc
  return rc.runapp('browser', urls, debug=debug)

if __name__ == "__main__":
  open('http://www.goole.com')

# EOF

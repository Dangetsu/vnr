# coding: utf8
# youtube.py
# 8/15/2013 jichi
# See: http://rg3.github.io/youtube-dl/documentation.html
if __name__ == '__main__':
  import sys
  sys.path.append('..')

#from sakurakit.skdebug import dprint

def get(vid, path=None, debug=True):
  """
  @param  vid  str  youtube video ID
  @param* path  unicode or None  default is on the Desktop
  @return  bool

  Example: python . -o "C:\Users\jichi\Desktop\%(title)s.%(ext)s" C9mjluSx40s
  """
  import os
  from sakurakit import skpaths, skproc
  python = skpaths.get_python_executable(gui=not debug) # enforce command line
  site = skpaths.get_python_site()
  main = os.path.join(site, 'youtube_dl')
  if not path:
    path = skpaths.DESKTOP
  oname = os.path.join(path, '%(title)s.%(ext)s')
  args = [
    python,
    '-B', # do not generate byte code
    main,
    '-o', oname,
    vid,
    #'--restrict-filenames',
  ]
  #dprint(args)
  return skproc.detach(args)

def getlist(vids, path=None, debug=True):
  """
  @param  vids  [str]  youtube video ID
  @param* path  unicode or None  default is on the Desktop
  @return  bool

  Example: python . -o "C:\Users\jichi\Desktop\%(title)s.%(ext)s" C9mjluSx40s
  """
  if not path:
    from sakurakit import skpaths
    path = skpaths.DESKTOP
  args = [path]
  args.extend(vids)
  import rc
  return rc.runscript('getyoutube.py', args, debug=debug)

def getlist_sina(vids, path=None, debug=False):
  """
  @param  vids  [str]  youtube video ID
  @param* path  unicode or None  default is on the Desktop
  @return  bool

  Example: python . -o "C:\Users\jichi\Desktop\%(title)s.%(ext)s" C9mjluSx40s
  """
  if not path:
    from sakurakit import skpaths
    path = skpaths.DESKTOP
  args = [path]
  args.extend(vids)
  import rc
  return rc.runapp('downloader', args, debug=debug)

if __name__ == "__main__":
  get('C9mjluSx40s')

# EOF

# coding: utf8
# getyoutube.py
# 10/27/2013 jichi

if __name__ == '__main__':
  import initrc
  #initrc.chcwd()
  initrc.initenv()

  import os
  title = os.path.basename(__file__)
  initrc.settitle(title)

import os
from sakurakit.skdebug import dprint, dwarn

USAGE = "dir vid ..."

def dispatch(path, videos):
  """
  @param  path  unicode
  @param  videos  [str]
  @return  bool
  """
  dprint("enter")
  import youtube_dl
  oname = os.path.join(path, '%(title)s.%(ext)s')
  argv = [
    '-o', oname,
    None, # vid
    #'--restrict-filenames',
  ]
  ret = []
  for vid in videos:
    argv[-1] = vid
    try: youtube_dl.main(argv)
    except SystemExit, e:
      dprint("exit code = %s" % e.code)
      ret.append(e.code)
  ok = not any(ret)
  dprint("leave: ret = %s" % ok)
  return ok

def writelog(path, videos):
  """
  @param  path  unicode
  @param  videos  [str]
  """
  dprint("enter")
  from datetime import datetime
  log = os.path.join(path, 'URL.txt')
  now = datetime.now()
  ts = now.strftime("%Y-%m-%d %H:%M")
  lines = ["Created by by VNR at %s" % ts]
  lines.extend(videos)
  with open(log, 'w') as f:
    f.write('\n'.join(lines))
  dprint("leave")

def main(argv):
  """
  @param  argv  [unicode]
  @return  int
  """
  dprint("enter")
  ret = 0
  try:
    if len(argv) < 2:
      dwarn("usage: %s" % USAGE)
    else:
      path = argv[0]
      videos = argv[1:]
      if not os.path.exists(path):
        os.makedirs(path) # recursively create dir
      writelog(path, videos)
      ok = dispatch(path, videos)
      from sakurakit import skos
      skos.open_location(os.path.abspath(path))
      ret = 0 if ok else 1
  except Exception, e:
    dwarn(e)
    ret = 1
  dprint("leave: ret = %s" % ret)
  return ret

if __name__ == '__main__':
  import sys
  ret = main(sys.argv[1:])
  sys.exit(ret)

# EOF

# coding: utf8
# tahcompile.py
# Generate TAH script from macros.
# 1/6/2015 jichi

if __name__ == '__main__':
  import initrc
  #initrc.chcwd()
  initrc.initenv()

  import os
  title = os.path.basename(__file__)
  initrc.settitle(title)

import os, sys
from sakurakit.skdebug import dwarn
import initdefs

DEFAULT_OUTPUT_FILE = 'output.tahcompile.txt'

def process(infiles, outfile):
  """
  @param  infiles  [unicode]
  @param  outfile  unicode
  @return  bool
  """
  from tah import tah
  lines = tah.readfiles(infiles)
  if not lines:
    dwarn("failed to parse input files")
    return False
  ok = tah.writefile(outfile, lines)
  if not ok:
    dwarn("failed to write output file")
  return ok

def parseoutfile(argv):
  """
  @param  argv  [unicode]
  @return  unicode or None
  """
  OUT_FLAG = '-o'
  ret = DEFAULT_OUTPUT_FILE
  while OUT_FLAG in argv:
    index = argv.index(OUT_FLAG)
    del argv[index]
    if len(argv) == index:
      dwarn("missing output file after %s" % OUT_FLAG)
      return
    ret = argv[index]
    del argv[index]
  return ret

def parseinfiles(argv):
  """
  @param  argv  [unicode]
  @return  [unicode] or None
  """
  try:
    ret = []
    for path in argv:
      if '*' not in path:
        ret.append(path)
      else:
        from glob import glob
        for it in glob(path):
          if not os.path.isdir(it):
            ret.append(it)
    return ret
  except Exception, e:
    dwarn(e)

## Main ##

def usage():
  cmd = os.path.basename(sys.argv[0])
  VERSION = 1420540738
  print """\
usage: %s infile1 [infile2] ... [-o outfile]
version: %s
Generate TAH script from multiple files with macros.""" % (cmd, VERSION)

def main(argv):
  """
  @param  argv  [unicode]
  @return  int  error file count
  """
  if len(argv) == 0 or argv[0] in initdefs.HELP_FLAGS:
    usage()
    return 0

  outfile = parseoutfile(argv)
  infiles = parseinfiles(argv)

  if not infiles or not outfile:
    usage()
    return 0

  ok = process(infiles, outfile)
  if ok:
    print "tahcompile: success"
  return 0 if ok else -1

if __name__ == '__main__':
  ret = main(sys.argv[1:])
  sys.exit(ret)

# EOF

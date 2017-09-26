# coding: utf8
# sublint.py
# Verify the integrity of subtitles.
# 12/16/2014 jichi

if __name__ == '__main__':
  import initrc
  #initrc.chcwd()
  initrc.initenv()

  import os
  title = os.path.basename(__file__)
  initrc.settitle(title)

import os, sys
import yaml
#from sakurakit.skdebug import dprint, dwarn
#from sakurakit.skprof import SkProfiler
import initdefs

KEY_TYPES = {
  'id': int,
  'gameId': int,
  'userId': int,
  'userName': basestring,
  'sub': basestring,
  'subName': basestring,
  'subLang': basestring,
  'subTime': int,
  'text': basestring,
  'textName': basestring,
  'textLang': basestring,
  'textTime': int,
  'comment': basestring,
  'revision': int,
  'timestamp': int,
}

def lint(path): # unicode -> bool
  print "process:", path
  ok = False
  try:
    lines = yaml.load(file(path, 'r'))
    if not lines or not isinstance(lines, list):
      raise ValueError("yaml root is not a valid list")
    for i,l in enumerate(lines):
      if not isinstance(l, dict):
        raise ValueError("#%s: record is not a dict: %s" % (i, l))
      for k,v in l.iteritems():
        t = KEY_TYPES.get(k)
        if not t:
          raise ValueError("#%s: unrecognized dict key: %s: %s" % (i, k, l))
        elif not isinstance(v, t):
          raise ValueError("#%s: invalid value type: %s: %s" % (i, k, l))
      if i:
        if not l.get('text'):
          raise ValueError("#%s: missing text: %s" % (i, l))
        if not l.get('sub'):
          raise ValueError("#%s: missing sub: %s" % (i, l))
    options = lines[0]
    if not options.get('textLang'):
      print "missing global textLang, assume 'ja'"
    if not options.get('subLang'):
      print "missing global subLang, use selected language when submit"
    ok = True
  except Exception, e:
    print e
  if ok:
    print "pass"
  else:
    print "failed"
  return ok

## Main ##

def usage():
  cmd = os.path.basename(sys.argv[0])
  VERSION = 1418779573
  print """\
usage: %s yamlfile1 [yamlfile2] ...
version: %s
Check syntax errors in yaml subtitles.""" % (cmd, VERSION)

def main(argv):
  """
  @param  argv  [unicode]
  @return  int  error file count
  """
  if len(argv) == 0 or argv[0] in initdefs.HELP_FLAGS:
    usage()
    return 0
  #dprint("enter")

  errorCount = 0
  for i,path in enumerate(argv):
    if i:
      print
    ok = lint(path)
    if not ok:
      errorCount += 1
  return errorCount

if __name__ == '__main__':
  ret = main(sys.argv[1:])
  sys.exit(ret)

# EOF

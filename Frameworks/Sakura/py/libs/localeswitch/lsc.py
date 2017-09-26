# coding: utf8
# applocale.py
# 4/9/2013
#
# See: https://github.com/av233max/NTLEA

#from sakurakit import skos
#from sakurakit.skdebug import dwarn

#if skos.WIN:
#  import win32api

# Example: LSC.exe  "D:\Games\propeller\あやかしびと\ayakasi.EXE" -c -p932 -s128 -l1041
def params(
    path=None,      # unicode, process path
    args=None,      # [unicode], process parameters
    codepage=932,   # int, -p
    locale=0x411,   # int, -l
    charset=128,    # int, -s
  ):
  """
  @return  [unicode]
  """
  ret = []
  if path is not None:
    #try: path = win32api.GetShortPathName(path)
    #except Exception, e: dwarn(e) # path does not exist
    ret.append(path)
  if args is not None:
    ret.extend(args)
  ret.append('-c')
  if codepage is not None:  ret.append("-p%i" % codepage)
  if locale is not None:    ret.append("-l%i" % locale)
  if charset is not None:   ret.append("-s%i" % charset)
  return ret

# EOF

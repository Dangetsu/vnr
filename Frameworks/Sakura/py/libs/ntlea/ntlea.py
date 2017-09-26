# coding: utf8
# applocale.py
# 4/9/2013
#
# See: https://github.com/av233max/NTLEA

#from sakurakit import skos
#from sakurakit.skdebug import dwarn

#if skos.WIN:
#  import win32api

# Example: ntleac.exe "d:\test\game.exe" "A-G 123 -B 456" "P0" "C932" "L1041" "T-540" "FMS Gothic" "S200"
def params(
    path=None,      # unicode, process path
    args=None,      # [unicode], process parameters
    compat=None,    # int, P parameter, windows compatibility level
    codepage=932,   # int, C parameter
    locale=0x411,   # int, L parameter, locale (0x411 = 1041)
    timezone=-540,  # int, T parameter
    font="MS Gothic",   # unicode, F parameter, font family
    size=None,      # int, S parameter, resize percentage
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
    ret.append('A"%s"' % '" "'.join(args)) # quoted
  if compat is not None:    ret.append("P%i" % compat)
  if codepage is not None:  ret.append("C%i" % codepage)
  if locale is not None:    ret.append("L%i" % locale)
  if timezone is not None:  ret.append("T%i" % timezone)
  if font is not None:      ret.append("F%s" % font)
  if size is not None:      ret.append("S%i" % size)
  return ret

# EOF

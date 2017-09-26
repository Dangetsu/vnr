# coding: utf8
# leproc.py
# 5/3/2013

# Example: LEProc.exe -run "d:\test\game.exe" parameters
def params(
    path=None,      # unicode, process path
    args=None,      # [unicode], process parameters
  ):
  """
  @return  [unicode]
  """
  ret = ['-run']
  if path is not None:
    #try: path = win32api.GetShortPathName(path)
    #except Exception, e: dwarn(e) # path does not exist
    ret.append(path)
  if args is not None:
    ret.extend(args)
  return ret

# EOF

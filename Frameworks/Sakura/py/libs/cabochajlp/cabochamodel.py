# coding: utf8
# cabochamodel.py
# 6/15/2014 jichi
#
# See: cabocha-model-index --help
#
# Example:
# cabocha-model-index -f SHIFT-JIS -t UTF-8 dep.ipa.txt dep.ipa.model

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import os
from sakurakit.skdebug import dwarn

def modelindex(model, txt, exe='cabocha-dict-index', async=False):
  """Note: this process would take at least 10 seconds
  @param  model  unicode  output path
  @param  txt  unicode  input path
  @param* exe  unicode
  @param* async  bool
  @return  bool
  """
  if not os.path.exists(txt):
    dwarn("input txt does not exist", txt)
    return False
  args = [
    exe,
    '-f', 'utf8', # from utf8
    '-t', 'utf8', # to utf8
    txt,
    model,
  ]
  from sakurakit import skproc
  run = skproc.detachgui if async else skproc.attachgui
  return bool(run(args)) and os.path.exists(model)

if __name__ == '__main__':
  exe = '/opt/local/libexec/cabocha/cabocha-model-index'
  print modelindex('chunk.ipa.model', 'chunk.ipa.txt', exe=exe)

# EOF

# coding: utf8
# 10/6/2014 jichi

import os
from sakurakit import skpaths, skos

if skos.WIN:
  from pywmp import WindowsMediaPlayer

WMP_DLL_PATH = os.path.join(skpaths.SYSTEM32, "wmp.dll")

# EOF

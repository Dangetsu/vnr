# coding: utf8
# osutil.py
# 10/14/2012 jichi

import os, subprocess
from sakurakit.skclass import memoized
from sakurakit.skdebug import dprint, derror

def run_batch(path, cwd=None):
  """
  @param  path  str  path to local file
  @return  if succeed
  """
  dprint("path = %s" % path)
  if not path or not os.path.exists(path):
    derror("batch script does not exist: %s" % path)
    return
  cwd = cwd or os.path.dirname(path)
  subprocess.Popen(path, cwd=cwd).communicate()

@memoized
def qncm():
  from PySide.QtNetwork import QNetworkConfigurationManager
  return QNetworkConfigurationManager()

def is_online():
  return qncm().isOnline()

# EOF

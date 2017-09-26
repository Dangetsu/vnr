# coding: utf8
# osutil.py
# 10/14/2012 jichi

from PySide import QtCore

def path_url(path):
  """
  @param  path  unicode
  @return  unicode
  """
  return QtCore.QUrl.fromLocalFile(path).toString()

def url_path(url):
  """
  @param  url  unicode
  @return  unicode
  """
  ret = QtCore.QUrl(url).toLocalFile()
  ret = QtCore.QDir.toNativeSeparators(ret)
  return ret

# EOF

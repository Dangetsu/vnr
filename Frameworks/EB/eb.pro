# eb.pro
# 3/28/2013 jichi

TEMPLATE = subdirs
SUBDIRS = src

INSTALLS += py
py.path = site-packages
py.files = site-packages

OTHER_FILES = \
  config.pri \
  COPYING

#OTHER_FILES =
#  ChangeLog
#  Doxyfile
#  README
#  TODO

# EOF

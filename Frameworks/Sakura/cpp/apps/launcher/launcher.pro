# launcher.pro
# 3/29/2012 jichi

TEMPLATE = subdirs
SUBDIRS = \
  pybrowser browser \
  pyreader reader
  #pyinstaller
  #installer
  #updater

OTHER_FILES += \
  include/main.tcc

# EOF

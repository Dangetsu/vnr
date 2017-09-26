# cpp.pro
# 7/31/2011 jichi
TEMPLATE = subdirs
SUBDIRS += \
  confs \
  libs \
  plugins \
  apps \
  tests
  #services

win32: SUBDIRS += coms

# EOF

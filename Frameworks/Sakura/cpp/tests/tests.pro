# tests.pro
# 12/15/2013 jichi

TEMPLATE = subdirs

SUBDIRS += test

SUBDIRS += \
  avtest \
  cctest \
  dyncodectest \
  hanjatest \
  hanviettest \
  hashtest \
  jsontest \
  pinyintest \
  pytest \
  qttest \
  rubytest \
  socktest \
  tahtest \
  trcodectest \
  troscripttest \
  trscripttest \
  uitest

win32: SUBDIRS += \
  ceviotest \
  fastaittest \
  imetest \
  ocrtest \
  parstest \
  sehtest \
  srtest \
  ttstest \
  vertest \
  wmptest \
  zunkotest

# EOF

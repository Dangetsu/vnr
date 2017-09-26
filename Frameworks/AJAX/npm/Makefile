# Makefile
# 8/8/2013 jichi
include ../env.mk

all: compress

compress: $(wildcard *.min.js)
download: $(wildcard *.js)

%.min.js: %.js
	$(MAKE) .closure OUT=$@ IN=$^

bbcode.js:
	$(MAKE) .wget OUT=$@ IN=http://rawgithub.com/ncb000gt/node-bbcode/master/lib/bbcode.js
	sed -i.sed.bak 's/exports/window.bbcode={};window.bbcode/' $@

# EOF

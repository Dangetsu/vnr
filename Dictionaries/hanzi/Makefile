# Makefile
# 5/10/2015 jichi
include ../../Frameworks/AJAX/env.mk

TARGETS = radicalListWithMeaning.js

all: download

download: $(TARGETS)

# https://github.com/nieldlr/hanzi
radicalListWithMeaning.js:
	$(MAKE) .wget OUT=$@ IN=http://rawgithub.com/nieldlr/Hanzi/master/lib/dicts/radicalListWithMeaning.js

# EOF

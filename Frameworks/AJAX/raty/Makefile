# Makefile
# 3/19/2014
# https://github.com/wbotelhos/raty
# http://wbotelhos.com/raty
include ../env.mk

#REPO = http://raw.githubusercontent.com/wbotelhos/raty/master/lib
REPO = http://rawgithub.com/wbotelhos/raty/master/lib

all: $(wildcard *.min.js) $(wildcard images/*.png)

%.min.js: %.js
	$(MAKE) .closure OUT=$@ IN=$^

jquery.raty.js:
	$(MAKE) .wget OUT=$@ IN=$(REPO)/$@

images/%.png:
	$(MAKE) .wget OUT=$@ IN=$(REPO)/$@

#fonts/raty.%:
#	$(MAKE) .wget OUT=$@ IN=$(REPO)/$@

# EOF

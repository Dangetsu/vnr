# Makefile
# 8/8/2013 jichi
include ../env.mk

all: compress

compress: $(wildcard *.min.js)
download: $(wildcard *.js)

%.min.js: %.js
	$(MAKE) .yui OUT=$@ IN=$^

haml.js:
	$(MAKE) .wget OUT=$@ IN=https://raw.github.com/creationix/haml-js/master/lib/haml.js

# EOF

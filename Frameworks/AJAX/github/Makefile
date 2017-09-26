# Makefile
# 8/8/2013 jichi
include ../env.mk

all: compress

compress: $(wildcard *.min.*)
download: $(wildcard *.js *.css)

%.min.js: %.js
	$(MAKE) .closure OUT=$@ IN=$^
%.min.css: %.css
	$(MAKE) .yui OUT=$@ IN=$^

# http://www.bootstrap-switch.org
# https://github.com/nostalgiaz/bootstrap-switch
bootstrap-switch.js:
	$(MAKE) .wget OUT=$@ IN=http://rawgithub.com/nostalgiaz/bootstrap-switch/master/dist/js/bootstrap-switch.min.js
bootstrap-switch.css:
	$(MAKE) .wget OUT=$@ IN=http://rawgithub.com/nostalgiaz/bootstrap-switch/master/dist/css/bootstrap3/bootstrap-switch.min.css

# http://bootstrap-growl.remabledesigns.com
# https://github.com/mouse0270/bootstrap-growl
bootstrap-growl.js:
	$(MAKE) .wget OUT=$@ IN=http://rawgithub.com/mouse0270/bootstrap-growl/master/bootstrap-growl.min.js

sprintf.js:
	$(MAKE) .wget OUT=$@ IN=http://rawgithub.com/alexei/sprintf.js/master/dist/sprintf.min.js
sprintf.map:
	$(MAKE) .wget OUT=$@ IN=http://rawgithub.com/alexei/sprintf.js/master/dist/sprintf.min.map

# EOF

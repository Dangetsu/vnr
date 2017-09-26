# Makefile
# 8/8/2013 jichi
include ../../qmljs.mk

all: $(wildcard *.min.js)

# Closure will remove the var variable and hence break the code
%.min.js: %.js
	> $@.1 sed 's/^exports\./var /' $^
	$(MAKE) .yui TYPE=js OUT=$@.2 IN=$@.1
	> $@ echo '.pragma library'
	>> $@ cat $@.2
	dos2unix $@
	rm $@.1 $@.2

clean: .clean

# https://npmjs.org/package/bbcode
bbcode.js:
	$(MAKE) .wget OUT=$@ IN=http://rawgithub.com/ncb000gt/node-bbcode/master/lib/bbcode.js

# EOF

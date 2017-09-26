# Makefile
# 8/8/2013 jichi
include ../qmljs.mk

all: Makefile compress

clean: .clean

compress: $(wildcard *.min.js)

%.min.js: %.js
	$(MAKE) .pragma OUT=$@ IN=$^

# EOF

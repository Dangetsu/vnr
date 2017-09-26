# Makefile
# 8/8/2013 jichi
include ../coffee.mk

SUBDIRS = forum
.PHONY: all compile compress clean $(SUBDIRS)

all: Makefile $(SUBDIRS) compress

$(SUBDIRS):
	$(MAKE) -C $@

#SOURCE = $(shell find . -name '*.coffee')
SOURCE = $(wildcard *.coffee)

compress: $(SOURCE:.coffee=.min.js)
compile: $(SOURCE:.coffee=.js)
clean:
	rm -f $(SOURCE:.coffee=.js)

# EOF

# Makefile
# 8/8/2013 jichi
include ../coffee.mk

all: Makefile compress

#SOURCE = $(shell find . -name '*.coffee')
SOURCE = $(wildcard *.coffee)

compress: $(SOURCE:.coffee=.min.js)
compile: $(SOURCE:.coffee=.js)
clean:
	rm -f $(SOURCE:.coffee=.js)

# EOF

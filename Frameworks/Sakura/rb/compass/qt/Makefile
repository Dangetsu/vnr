# Makefile
# 8/8/2013 jichi
include ../compass.mk

all: compress

$(COMPASS_COMMANDS):
	$(COMPASS) $@

compress: compile $(wildcard css/*.min.css)

# EOF

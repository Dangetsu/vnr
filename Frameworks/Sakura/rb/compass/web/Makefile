# Makefile
# 8/8/2013 jichi
include ../compass.mk

all: compress

$(COMPASS_COMMANDS):
	$(COMPASS) $@

SOURCE = $(wildcard css/*.min.css css/*/*.min.css)

compress: compile $(SOURCE)

# EOF

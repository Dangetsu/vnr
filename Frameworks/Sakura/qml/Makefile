# Makefile
# 8/8/2013 jichi

# http://lackof.org/taggart/hacking/make-example/
SUBDIRS = \
    apps/reader/tr \
    components/bootstrap2 \
    components/bootstrap3 \
    components/buttongroup \
    components/qt5 \
    js

.PHONY: all clean $(SUBDIRS)

all: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

clean:
	@for it in $(SUBDIRS); do \
	  $(MAKE) -C $$it $@; \
	done

# EOF

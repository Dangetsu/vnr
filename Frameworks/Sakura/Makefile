# Makefile
# 8/8/2013 jichi

# http://lackof.org/taggart/hacking/make-example/
SUBDIRS = \
    coffee \
    qml \
    rb/compass \
	py/apps/reader/mytr \
	py/apps/reader/tr
    #py/libs/sakurakit/tr # too slow to make

.PHONY: all clean $(SUBDIRS)

all: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

clean:
	@for it in $(SUBDIRS); do \
	  $(MAKE) -C $$it $@; \
	done

# EOF

# Makefile
# 8/8/2013 jichi

# http://lackof.org/taggart/hacking/make-example/
SUBDIRS = dmm libs share browser reader

.PHONY: all clean $(SUBDIRS)

all: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

clean:
	@for it in $(SUBDIRS); do \
	  $(MAKE) -C $$it $@; \
	done

# EOF

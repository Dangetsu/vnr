# Makefile
# 8/8/2013 jichi

# http://lackof.org/taggart/hacking/make-example/
SUBDIRS = qt web

.PHONY: all clean $(SUBDIRS)

all: $(SUBDIRS)

$(SUBDIRS):
	$(MAKE) -C $@

clean:
	@for it in $(SUBDIRS); do \
	  $(MAKE) -C $$it $@; \
	done

# EOF

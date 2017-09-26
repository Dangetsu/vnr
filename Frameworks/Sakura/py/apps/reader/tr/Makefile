# Makefile
# 8/8/2013 jichi

#ZHSZHT = opencc -c s2twp.json -i

.PHONY: all release clean

all: Makefile release

release: $(wildcard *.qm)

#zh_TW.ts: zh_CN.ts
#	zhs2zht $^ | sed 's/zh_CN/zh_TW/g' > $@

%.qm: %.ts
	dos2unix $^
	lrelease $^

clean:

# EOF

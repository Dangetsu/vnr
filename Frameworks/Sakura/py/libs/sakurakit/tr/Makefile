# Makefile
# 8/8/2013 jichi

ZHSZHT = opencc -c s2twp.json -i

.PHONY: all release clean

all: Makefile release zh_TW.ts

# Language short name in Japanese
# http://ja.wikipedia.org/wiki/国名の漢字表記一覧

LOCALES = \
	ko_KR \
	th_TH \
	vi_VN \
	tl_TL \
	id_ID \
	ms_MY \
	ar_SA \
	be_BE \
	bg_BG \
	cs_CS \
	da_DA \
	de_DE \
	el_EL \
	et_EE \
	fi_FI \
	fr_FR \
	es_ES \
	he_IL \
	hu_HU \
	it_IT \
	lt_LT \
	lv_LV \
	no_NO \
	nl_NL \
	pl_PL \
	pt_PT \
	ro_RO \
	ru_RU \
	sk_SK \
	sl_SL \
	sv_SV \
	tr_TR \
	uk_UA
	#ja_JP
	#en_US
	#zh_TW
	#zh_CN

release: $(wildcard *.qm)

zh_TW.ts: zh_CN.ts
	$(ZHSZHT) $^ | sed 's/zh_CN/zh_TW/g' | sed 's/指令碼/脚本/g' > $@

$(addsuffix .ts,$(LOCALES)): ja_JP.ts
	python ../../../scripts/tsupdate.py $@ $^

%.qm: %.ts
	dos2unix $^
	lrelease $^

clean:

# EOF

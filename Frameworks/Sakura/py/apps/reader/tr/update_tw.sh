#!/bin/bash
# update_tw.sh
# 2/17/2013 jichi
set +x

s=zh_CN.ts
t=zh_TW.ts

ZHSZHT="opencc -c s2twp.json -i"

echo "$ZHSZHT '$s' > '$t'"
$ZHSZHT "$s" | sed 's/zh_CN/zh_TW/g' >"$t"

#s/戀と選挙/恋と選挙/g;
#s/広辭苑/広辞苑/g;

dos2unix "$t"

# EOF

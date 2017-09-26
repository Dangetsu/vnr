#!/bin/bash
# update.sh
# 11/5/2012 jichi
cd "$(dirname "$0")"

TRANSLATIONS="ja_JP.ts zh_CN.ts zh_TW.ts"

tr_dir=$(basename "$PWD")
proj_dir=$(dirname "$PWD")
proj_name=$(basename "$proj_dir")

proj_file="$proj_name.pro"
pro="$proj_dir/$proj_name.pro"

die()
{
  >&2 echo "$*"
  exit -1
}

require()
{
  local i
  for i in "$@"; do
    >/dev/null which "$i" || {
    die "$ME: ERROR: cannot find '$i' in PATH, ABORT"
  }
  done
}
require pyside-lupdate lrelease

>"$pro" echo "# $proj_file"
>>"$pro" echo "# AUTOMATICALLY GENERATED"
>>"$pro" echo "# $(date)"
>>"$pro" echo

>>"$pro" echo "CODECFORTR = UTF-8"
>>"$pro" echo -n "SOURCES ="

for src_path in "$proj_dir"/*.py; do
  src_file=$(basename "$src_path")
  >>"$pro" echo -n " $src_file"
done
>>"$pro" echo

>>"$pro" echo -n "TRANSLATIONS ="
for tr_file in $TRANSLATIONS; do
  tr_path="$tr_dir/$tr_file"
  >>"$pro" echo -n " $tr_path"
done
>>"$pro" echo

>>"$pro" echo
>>"$pro" echo "# EOF"

cat "$pro"
echo

echo "pyside-lupdate '$pro'"
pyside-lupdate "$pro"
lrelease *.ts

# EOF

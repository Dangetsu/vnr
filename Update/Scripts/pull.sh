#!/bin/bash
# 12/17/2012 jichi
cd "$(dirname "$0")"/../..
HG_OPT="-v --debug"

REPOS="\
. \
Frameworks/Python \
Frameworks/EB \
Frameworks/Sakura \
"

die()
{
  >&2 echo "$@"
  exit 1
}

require()
{
  local i
  for i; do
    which "$i" >/dev/null 2>&1 || \
      die "$ME: cannot find '$i' in PATH, ABORT"
  done
}
require hg

test -e .hgignore || die "unknown hg repository"

for f in `echo $REPOS`; do
  if [ -x "$f" ]; then
    pushd "$f"
    echo hg pullup: `pwd`
    hg $HG_OPT pull && \
      hg $HG_OPT up
    popd
  fi
done

# EOF

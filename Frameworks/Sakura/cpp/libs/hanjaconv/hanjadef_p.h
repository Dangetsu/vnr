#ifndef HANJADEF_P_H
#define HANJADEF_P_H

// hanjadef_p.h
// 1/6/2015 jichi
#include <locale>

#define HANJA_MIN_SIZE  2  // each word contains at least 2 kanji

enum : char {
  CH_COMMENT = '#'  // beginning of a comment
  , CH_DELIM = '\t' // deliminator
};

extern const std::locale HANJA_UTF8_LOCALE;

#endif // HANJADEF_P_H

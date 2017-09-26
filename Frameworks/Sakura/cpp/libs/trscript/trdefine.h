#ifndef TRDEFINE_H
#define TRDEFINE_H

// trdefine.h
// 3/5/2015 jichi

// Translation script special characters
enum : wchar_t {
  TRSCRIPT_CH_COMMENT = L'#'    // indicate the beginning of a line comment
  , TRSCRIPT_CH_DELIM = L'\t'   // deliminator of fields in a line
  , TRSCRIPT_CH_REGEX = L'r'    // a regex rule
  , TRSCRIPT_CH_ICASE = L'i'    // case insensitive
};

#endif // TRDEFINE_H

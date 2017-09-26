#ifndef TRDEFINE_H
#define TRDEFINE_H

// trdefine.h
// 3/5/2015 jichi

#define TRSCRIPT_COLUMNSEP L" ||| "   // deliminator of fields in a line, wrapped with spaces

// Translation script special characters
enum : wchar_t {
  TRSCRIPT_CH_COMMENT = L'#'        // indicate the beginning of a line comment
  // TRSCRIPT_CH_COLUMNSEP = L'\t'  // deliminator of fields in a line
  , TRSCRIPT_CH_FEATURESEP = L' '   // deliminator of features
  , TRSCRIPT_CH_REGEX = L'r'        // a regex rule
  , TRSCRIPT_CH_ICASE = L'i'        // case insensitive
};

enum TRSCRIPT_COLUMN {
  TRSCRIPT_COLUMN_TOKEN = 0 // the first column is lhs token
  , TRSCRIPT_COLUMN_SOURCE // the second column is rhs source
  , TRSCRIPT_COLUMN_TARGET // the third column is rhs target
  , TRSCRIPT_COLUMN_FEATURE // the fourth column is rule feature
  , TRSCRIPT_COLUMN_COUNT // totally 4 columns
};

enum TRSCRIPT_FEATURE {
  TRSCRIPT_FEATURE_ID = 0 // the first feature is the rule ID
  , TRSCRIPT_FEATURE_CATEGORY // the second feature is the
  , TRSCRIPT_FEATURE_FLAGS // the third feature is a set of flags
  , TRSCRIPT_FEATURE_COUNT // totally 3 features
};

#endif // TRDEFINE_H

//enum TranslationScriptType {
//  TranslationScript = 0
//  , NameScript
//  , NamePrefixScript
//  , NameSuffixScript
//};

#pragma once

// winime.h
// 4/1/2013 jichi

#include <functional>

// - Constants -

#define WINIME_CLASS_CN L"MSIME.China"  // = szImeChina
#define WINIME_CLASS_JA L"MSIME.Japan"  // = szImeJapan
#define WINIME_CLASS_KO L"MSIME.Korea"  // = szImeKorea
#define WINIME_CLASS_TW L"MSIME.Taiwan" // = szImeTaiwan
//#define WINIME_CLASS_TW_BBO    L"IME.Taiwan.ImeBbo"

enum {
  WINIME_MAX_SIZE = 100 // maximum size of string that can be processed
};

// See: msime.h, http://www.microsoft.com/en-us/download/details.aspx?id=9739
// See: http://msdn.microsoft.com/ja-jp/library/windows/desktop/hh851782%28v=vs.85%29.aspx
enum {
  WINIME_REQ_CONV = 0x00010000      // = FELANG_REQ_CONV, convert
  , WINIME_REQ_REV = 0x00030000     // = FELANG_REQ_REV, revert
  , WINIME_REQ_RECONV = 0x00020000  // = FELANG_REQ_RECONV, convert after revert
};

// See: http://www7a.biglobe.ne.jp/~tsuneoka/win32tech/7.html
// See: http://tokovalue.jp/ImmSetConversionStatus_U.htm
enum {
  WINIME_MODE_HIRAGANA = 0x00000000     // = FELANG_CMODE_HIRAGANAOUT hiragana output
  , WINIME_MODE_KATAGANA = 0x00000008   // = FELANG_CMODE_KATAKANAOUT katakana output
  , WINIME_MODE_HANGUL = 0x00000080     // = FELANG_CMODE_HANGUL hangul output
  , WINIME_MODE_PINYIN = 0x00000100     // = FELANG_CMODE_PINYIN pinyin output
  , WINIME_MODE_ROMAN = 0x00002000      // = FELANG_CMODE_ROMAN romaji output

  , WINIME_MODE_NAME = 0x10000000       // = FELANG_CMODE_NAME = FELANG_CMODE_PHRASEPREDICT name mode (MSKKIME)
  , WINIME_MODE_PRECONV = 0x00000200    // = FELANG_CMODE_PRECONV convert romaji to kana and western punctuation to Japanese

  , WINIME_MODE_NONE = 0x01000000           // = FELANG_CMODE_NONE = IME_SMODE_NONE no information about the sentence
  , WINIME_MODE_AUTOMATIC = 0x08000000      // = FELANG_CMODE_AUTOMATIC = IME_SMODE_AUTOMATIC
  , WINIME_MODE_SINGLECONVERT = 0x04000000  // = FELANG_CMODE_SINGLECONVERT = IME_SMODE_SINGLECONVERT convert single kanji
  , WINIME_MODE_PLAURALCLAUSE = 0x02000000  // = FELANG_CMODE_PLAURALCLAUSE = IME_SMODE_PLAURALCLAUSE plural sensitive
  , WINIME_MODE_PHRASEPREDICT = 0x10000000  // = FELANG_CMODE_PHRASEPREDICT = IME_SMODE_PHRASEPREDICT, predict phrase

  , WINIME_MODE_NOINVISIBLECHAR = 0x40000000 // = FELANG_CMODE_NOINVISIBLECHAR  remove invisible chars (e.g. tone mark)

};

// - Functions and types -

struct IFELanguage;
typedef IFELanguage winime_t; // opaque handle

winime_t *winime_create(const wchar_t *cls); ///< create an im engine of given class
void winime_destroy(winime_t *ife);            ///< destroy the im engine

// Get the entire result. Return if succeed.
typedef std::function<void (const wchar_t *, size_t)> winime_apply_fun_t;
bool winime_apply(winime_t *ife, unsigned long req, unsigned long mode,
                  const wchar_t *src, size_t len, const winime_apply_fun_t &fun);

// Get each result, similar to list.collect in groovy. Return if succeed.
typedef std::function<void (const wchar_t *, size_t, const wchar_t *, size_t)> winime_collect_fun_t;
bool winime_collect(winime_t *ife, unsigned long req, unsigned long mode,
                    const wchar_t *src, size_t len, const winime_collect_fun_t &fun);

// EOF

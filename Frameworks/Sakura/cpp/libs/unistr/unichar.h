#ifndef UNICHAR_H
#define UNICHAR_H

// unichar.h
// 1/6/2015 jichi

#include <cstring>

#ifdef __clang__
# pragma clang diagnostic ignored "-Wlogical-op-parentheses"
#endif // __clang__

namespace unistr {

// Orders of wide and thin characters

enum { thin_wide_dist = 65248 };
enum : char { thin_min = 33, thin_max = 126 };
enum : wchar_t { wide_min = thin_min + thin_wide_dist, wide_max = thin_max + thin_wide_dist };

inline bool isthin(int ch) { return thin_min <= ch && ch <= thin_max; }
inline bool iswide(int ch) { return wide_min <= ch && ch <= wide_max; }

inline int thin2wide(int ch) { return isthin(ch) ? ch + thin_wide_dist : ch; }
inline int wide2thin(int ch) { return iswide(ch) ? ch - thin_wide_dist : ch; }

// Japanese

// Some of the kana characters are skipped
// See: http://stackoverflow.com/questions/3826918/how-to-classify-japanese-characters-as-either-kanji-or-kana
// Here's the range used by Google Guava
// - Hiragana: \u3040-\u309f
// - Katagana: \u30a0-\u30ff
enum { hira_kata_dist = 96 };
enum : wchar_t { hira_min = 12353, hira_max = 12438 }; // xa-xge
enum : wchar_t { kata_min = 12449, kata_max = 12538 }; // xa-vo

inline bool ishira(int ch) { return hira_min <= ch && ch <= hira_max; }
inline bool iskata(int ch) { return kata_min <= ch && ch <= kata_max; }

inline bool iskana(int ch) { return ishira(ch) || iskata(ch); }

inline int hira2kata(int ch) { return ishira(ch) ? ch + hira_kata_dist : ch; }

inline int kata2hira(int ch) // because katagana has a larger range
{ return kata_min <= ch && ch <= hira_max + hira_kata_dist ? ch - hira_kata_dist : ch; }

// Chinese

// The same range as Google Guava
// See: http://stackoverflow.com/questions/3826918/how-to-classify-japanese-characters-as-either-kanji-or-kana
enum : wchar_t { kanji_min = 0x4e00, kanji_max = 0x9faf }; // 一-龯
inline bool iskanji(int ch) { return kanji_min <= ch && ch <= kanji_max; }

// Korean

inline bool ishangul(int ch)
{
  return 0xac00 <= ch && ch <= 0xd7a3   // Hangul Syllables (AC00-D7A3) which corresponds to (가-힣)
      || 0x1100 <= ch && ch <= 0x11ff   // Hangul Jamo (1100–11FF)
      || 0x3130 <= ch && ch <= 0x318f   // Hangul Compatibility Jamo (3130-318F)
      || 0xa960 <= ch && ch <= 0xa97f   // Hangul Jamo Extended-A (A960-A97F)
      || 0xd7b0 <= ch && ch <= 0xd7ff;  // Hangul Jamo Extended-B (D7B0-D7FF)
}

// Punctuations

inline bool isspace(int ch) { return ::wcschr(L" \t\n\x3000", ch); }

/**
 *  TODO: The punctuation string is incomplete
 *  、。〈〉《》「」『』【】
 *  …
 *  ★☆♡♥
 *  ！（），＜＞？
 */
inline bool ispunct(int ch)
{
  return ::wcschr(
    L"\x3001\x3002\x3008\x3009\x300a\x300b\x300c\x300d\x300e\x300f\x3010\x3011"
    L"\x2026"
    L"\x2605\x2606\x2661\x2665"
    L"\xff01\xff08\xff09\xff0c\xff1c\xff1d\xff1f"
  , ch);
}

} // namespace unistr

#endif // UNICHAR_H

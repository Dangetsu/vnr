// uniiter.cc
// 9/12/2015 jichi
#include "unistr/uniiter.h"
#include <cwctype> // for iswxxx

void uniiter::iter_words(const wchar_t *text, size_t size,
                       const std::function<void (size_t start, size_t length, bool isword)> &fun)
{
  size_t pos = 0; // beginning of a word
  for (size_t i = 0; i < size; i++) {
    wchar_t ch = text[i];
    if (::iswspace(ch) || ::iswpunct(ch)) {
      if (pos < i)
        fun(pos, i - pos, true); // isword = true
      fun(i, 1, false); // isword = false
      pos = i + 1;
    }
  }
  if (pos < size)
    fun(pos, size - pos, true); // isword = true
}

// EOF

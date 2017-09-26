#ifndef QHANGULHANJACONV_P_H
#define QHANGULHANJACONV_P_H

// hangulparse.h
// 1/6/2015 jichi

#include <functional>

void hangul_iter_words(const wchar_t *text, size_t size,
                       const std::function<void (size_t start, size_t length)> &fun);

#endif // QHANGULHANJACONV_P_H

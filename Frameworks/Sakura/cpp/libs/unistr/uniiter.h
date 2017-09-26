#ifndef UNIITER_H
#define UNIITER_H

// uniiter.h
// 9/12/2015 jichi

#include <functional>

namespace uniiter {

void iter_words(const wchar_t *text, size_t size,
                const std::function<void (size_t start, size_t length, bool isword)> &fun);

} // namespace uniiter

#endif // UNIITER_H

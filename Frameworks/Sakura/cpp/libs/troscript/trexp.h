#ifndef TREXP_H
#define TREXP_H

// trexp.h
// 5/17/2015 jichi

#include <string>

namespace trexp {

// Compile term source
std::wstring compile_pattern(const std::wstring &source, bool escape);
// Compile term target
std::wstring compile_format(const std::wstring &target, const std::wstring &source);

} // namespace trexp

#endif // TREXP_H

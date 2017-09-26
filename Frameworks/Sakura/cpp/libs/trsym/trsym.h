#ifndef TRSYM_H
#define TRSYM_H

// trsym.h
// 9/20/2014 jichi

#include <functional>
#include <string>
#include <vector>

namespace trsym {

typedef std::function<void (const std::string &)> collect_string_f; // string ->
typedef std::function<void (const std::wstring &)> collect_wstring_f; // wstring ->

/// Return rendered target for specified rule id given arguments
typedef std::function<std::wstring (int, const std::vector<std::wstring> &)> decode_f; // id, args -> result

///  Return if source text contains [[symbol]]
bool contains_raw_symbol(const std::wstring &source);

///  Return if source text contains {{symbol}}
bool contains_encoded_symbol(const std::wstring &source);

/** Return {{x:id}} for [[x]]
 *  @param  token
 *  @param  id
 *  @param  argc  number of tokens in the target
 */
std::string create_symbol_target(const std::string &token, int id, int argc);

///  Return number of [[x]] in the target
size_t count_raw_symbols(const std::wstring &target);

///  Collect raw symbols
void iter_raw_symbols(const std::wstring &target, const collect_string_f &fun);

///  Replace [[x]] by regular expression for {{x}}. Escape specifies whether escape regex special chars.
std::wstring encode_symbol(const std::wstring &text, bool escape = false);

///  Replace [[x]] by regular expression for {{x}}. Escape specifies whether escape regex special chars.
std::wstring encode_output_symbol(const std::wstring &text, bool escape = false);

///  Replace {{x}} by something else
std::wstring decode_symbol(const std::wstring &text, const decode_f &fun);

} // namespace trsym

#endif // TRSYM_H

// trdeccde.cc
// 3/5/2015 jichi

#include "trcodec/trdecode.h"
#include "trcodec/trdecoderule.h"
#include "trsym/trsym.h"
#include <boost/algorithm/string.hpp>
#include <boost/foreach.hpp>
//#include <QDebug>

#ifdef __clang__
# define USE_BOOST_CXX11
#endif // __clang__

#ifdef USE_BOOST_CXX11
# include <boost/unordered_map.hpp>
  using boost::unordered_map;
#else
# include <unordered_map>
  using std::unordered_map;
#endif // USE_BOOST_CXX11

/** Private class */

class TranslationDecoderPrivate
{
public:
  typedef unordered_map<int, TranslationDecodeRule> map_type; // {id:rule}
  map_type map;
};

/** Public class */

// Construction

TranslationDecoder::TranslationDecoder() : d_(new D) {}
TranslationDecoder::~TranslationDecoder() { delete d_; }

int TranslationDecoder::size() const { return d_->map.size(); }
bool TranslationDecoder::isEmpty() const { return d_->map.empty(); }

void TranslationDecoder::clear() { d_->map.clear(); }

// Initialization
void TranslationDecoder::addRules(const TranslationRuleList &rules)
{
  BOOST_FOREACH (const auto &it, rules)
    d_->map[it.id].init(it);
}

// Translation
void TranslationDecoder::decode(std::wstring &text, int category, bool mark) const
{
  if (d_->map.empty())
    return;
  if (!trsym::contains_encoded_symbol(text))
    return;
  text = trsym::decode_symbol(text,
    [this, category, mark](int id, const std::vector<std::wstring> &args) -> std::wstring {
      auto p = d_->map.find(id);
      if (p != d_->map.end()) {
        const auto &rule = p->second;
        if (rule.is_valid() && rule.match_category(category))
          return rule.render_target(args, mark);
      }
      return std::wstring();
    }
  );
}

// EOF

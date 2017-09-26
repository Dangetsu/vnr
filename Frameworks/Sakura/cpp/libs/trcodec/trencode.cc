// trenccde.cc
// 3/5/2015 jichi

#include "trcodec/trencode.h"
#include "trcodec/trencoderule.h"
#include <boost/algorithm/string.hpp>
#include <boost/foreach.hpp>
//#include <QDebug>

/** Private class */

class TranslationEncoderPrivate
{
public:
  //QReadWriteLock lock;

  TranslationEncodeRule *rules; // use array for performance reason
  size_t ruleCount;

  TranslationEncoderPrivate() : rules(nullptr), ruleCount(0) {}
  ~TranslationEncoderPrivate() { if (rules) delete[] rules; }

  void clear()
  {
    ruleCount = 0;
    if (rules) {
      delete[] rules;
      rules = nullptr;
    }
  }

  void reset(size_t size)
  {
    clear(); // clear first for thread-safety
    rules = new TranslationEncodeRule[size];
    ruleCount = size;
  }
};

/** Public class */

// Construction

TranslationEncoder::TranslationEncoder() : d_(new D) {}
TranslationEncoder::~TranslationEncoder() { delete d_; }

int TranslationEncoder::size() const { return d_->ruleCount; }
bool TranslationEncoder::isEmpty() const { return !d_->ruleCount; }

void TranslationEncoder::clear() { d_->clear(); }

// Initialization
void TranslationEncoder::setRules(const TranslationRuleList &rules)
{
  if (rules.empty())
    d_->clear();
  else {
    d_->reset(rules.size());
    size_t i = 0;
    BOOST_FOREACH (const auto &it, rules)
      d_->rules[i++].init(it);
  }
}

// Translation
void TranslationEncoder::encode(std::wstring &result, int category, int limit) const
{
  if (!d_->ruleCount || !d_->rules)
    return;
  std::wstring lastResult;
  for (int count = 0; lastResult != result && (!limit || count < limit); count++) {
    //qDebug() << count;
    lastResult = result;
    for (size_t i = 0; i < d_->ruleCount; i++) {
      const auto &rule = d_->rules[i];
      if (rule.is_valid()
          && rule.match_category(category)
          && (!count || rule.is_symbolic()))
        rule.replace(result);
    }
  }
}

// EOF

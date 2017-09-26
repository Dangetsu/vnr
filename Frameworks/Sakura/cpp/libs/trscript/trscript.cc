// trscript.cc
// 9/20/2014 jichi

#include "trscript/trscript.h"
#include "trscript/trdefine.h"
#include "trscript/trrule.h"
#include "cpputil/cpplocale.h"
#include <boost/foreach.hpp>
#include <fstream>
#include <list>

#define SK_NO_QT
#define DEBUG "trscript.cc"
#include "sakurakit/skdebug.h"

//#define DEBUG_RULE // output the rule that is applied
//#include <QDebug>

/** Helpers */

namespace { // unnamed

const std::locale UTF8_LOCALE = ::cpp_utf8_locale<wchar_t>();

} // unnamed namespace

/** Private class */

class TranslationScriptPerformerPrivate
{

public:
  //QReadWriteLock lock;

  TranslationScriptRule *rules; // use array for performance reason
  size_t ruleCount;

  TranslationScriptPerformerPrivate() : rules(nullptr), ruleCount(0) {}
  ~TranslationScriptPerformerPrivate() { if (rules) delete[] rules; }

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
    rules = new TranslationScriptRule[size];
    ruleCount = size;
  }

  static bool loadRules(const std::wstring &path, std::list<TranslationScriptBaseRule> &rules);
};

bool TranslationScriptPerformerPrivate::loadRules(const std::wstring &path, std::list<TranslationScriptBaseRule> &rules)
{
#ifdef _MSC_VER
  std::wifstream fin(path);
#else
  std::string spath(path.begin(), path.end());
  std::wifstream fin(spath.c_str());
#endif // _MSC_VER
  if (!fin.is_open()) {
    DERR("unable to open file");
    return false;
  }
  fin.imbue(UTF8_LOCALE);

  int missing_id = 0; // assign negative id for missing id
  for (std::wstring line; std::getline(fin, line);)
    if (!line.empty() && line[0] != TRSCRIPT_CH_COMMENT) {
      TranslationScriptBaseRule rule;
      size_t pos = 0;
      for (; pos < line.size() && line[pos] != TRSCRIPT_CH_DELIM; pos++)
        switch (line[pos]) {
        case TRSCRIPT_CH_REGEX: rule.set_regex(); break;
        case TRSCRIPT_CH_ICASE: rule.set_icase(); break;
        }
      if (pos == line.size())
        continue;
      //line.pop_back(); // remove trailing '\n'
      const wchar_t *cur = line.c_str() + pos;
      int id = ::wcstol(cur, const_cast<wchar_t **>(&cur), 10); // base 10
      if (cur && *cur++) { // skip first delim
        rule.category = ::wcstol(cur, const_cast<wchar_t **>(&cur), 10); // base 10
        if (cur && *cur++) {
          rule.id = id;
          if (const wchar_t *delim = ::wcschr(cur, TRSCRIPT_CH_DELIM)) {
            rule.source.assign(cur, delim - cur);
            rule.target.assign(delim + 1);
          } else
            rule.source.assign(cur);
          if (!rule.source.empty()) {
            if (!rule.id)
              rule.id = --missing_id;
            if (!rule.category) // always enable category if not specified
              rule.category = -1;
            rules.push_back(rule);
          }
        }
      }
    }

  fin.close();
  return true;
}

/** Public class */

// Construction

TranslationScriptPerformer::TranslationScriptPerformer() : d_(new D) {}
TranslationScriptPerformer::~TranslationScriptPerformer() { delete d_; }

int TranslationScriptPerformer::size() const { return d_->ruleCount; }
bool TranslationScriptPerformer::isEmpty() const { return !d_->ruleCount; }

//bool TranslationScriptPerformer::isLinkEnabled() const { return d_->link; }
//void TranslationScriptPerformer::setLinkEnabled(bool t) { d_->link = t; }

//std::wstring TranslationScriptPerformer::linkStyle() const { return d_->linkStyle; }
//void TranslationScriptPerformer::setLinkStyle(const std::wstring &css) { d_->linkStyle = css; }

void TranslationScriptPerformer::clear() { d_->clear(); }

// Initialization
bool TranslationScriptPerformer::loadScript(const std::wstring &path)
{
  d_->clear();

  std::list<TranslationScriptBaseRule> rules;
  try {
    D::loadRules(path, rules);
  } catch (...) {
    DERR("failed to parse script");
  }
  if (rules.empty())
    return false;

  //QWriteLocker locker(&d_->lock);
  d_->reset(rules.size());

  size_t i = 0;
  BOOST_FOREACH (const auto &it, rules)
    d_->rules[i++].init(it);

  return true;
}

// Translation
std::wstring TranslationScriptPerformer::transform(const std::wstring &text, int category, bool mark) const
{
  //QReadLocker locker(&d_->lock);
  std::wstring ret = text;
#ifdef DEBUG_RULE
  std::wstring previous = text;
#endif // DEBUG_RULE
  if (d_->ruleCount && d_->rules)
    for (size_t i = 0; i < d_->ruleCount; i++) {
      const auto &rule = d_->rules[i];
      if (rule.is_valid() && rule.match_category(category))
        rule.replace(ret, mark);

#ifdef DEBUG_RULE
     TranslationScriptBaseRule *r = (TranslationScriptBaseRule *)&rule;
      if (previous != ret)
        qDebug() << QString::fromStdWString(r->source) << QString::fromStdWString(r->target) << QString::fromStdWString(ret);
      previous = ret;
#endif // DEBUG_RULE
    }
  return ret;
}

// EOF

// trcodec.cc
// 3/5/2015 jichi

#include "trcodec/trcodec.h"
#include "trcodec/trdefine.h"
#include "trcodec/trdecode.h"
#include "trcodec/trencode.h"
#include "trcodec/trrule.h"
#include "cpputil/cpplocale.h"
#include "cpputil/cppstring.h"
#include <boost/algorithm/string.hpp>
#include <boost/lambda/lambda.hpp>
#include <fstream>
#include <vector>
//#include <QDebug>

#define SK_NO_QT
#define DEBUG "trcodec.cc"
#include "sakurakit/skdebug.h"

//#define DEBUG_RULE // output the rule that is applied

/** Helpers */

namespace { // unnamed

const std::locale UTF8_LOCALE = ::cpp_utf8_locale<wchar_t>();

} // unnamed namespace

/** Private class */

class TranslationCoderPrivate
{

public:
  //QReadWriteLock lock;

  TranslationEncoder *encoder;
  TranslationDecoder *decoder;

  TranslationCoderPrivate() : encoder(new TranslationEncoder), decoder(new TranslationDecoder) {}
  ~TranslationCoderPrivate() {  delete encoder; delete decoder; }

  void clear()
  {
    encoder->clear();
    decoder->clear();
  }

  static bool loadRules(const std::wstring &path, TranslationRuleList &rules);

};

bool TranslationCoderPrivate::loadRules(const std::wstring &path, TranslationRuleList &rules)
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

  const auto column_sep = boost::first_finder(TRSCRIPT_COLUMNSEP);
  const auto feature_sep = boost::lambda::_1 == TRSCRIPT_CH_FEATURESEP;

  std::vector<std::wstring> cols;
  cols.reserve(TRSCRIPT_COLUMN_COUNT);

  std::vector<std::string> features;
  features.reserve(TRSCRIPT_FEATURE_COUNT);

  int missing_id = 0; // assign negative id for missing id
  for (std::wstring line; std::getline(fin, line);)
    if (!line.empty() && line[0] != TRSCRIPT_CH_COMMENT) {
      boost::iter_split(cols, line, column_sep);
      if (!cols.empty()) {
        TranslationRule rule;
        if (cols.size() > TRSCRIPT_COLUMN_TOKEN)
          rule.token = ::cpp_string_of(cols[TRSCRIPT_COLUMN_TOKEN]);
        if (cols.size() > TRSCRIPT_COLUMN_TOKEN)
          rule.source = cols[TRSCRIPT_COLUMN_SOURCE];
        if (cols.size() > TRSCRIPT_COLUMN_TARGET)
          rule.target = cols[TRSCRIPT_COLUMN_TARGET];
        if (cols.size() > TRSCRIPT_COLUMN_FEATURE) {
          std::string feature = ::cpp_string_of(cols[TRSCRIPT_COLUMN_FEATURE]);
          if (!feature.empty()) {
            boost::split(features, feature, feature_sep);
            if (!features.empty()) {
              if (features.size() > TRSCRIPT_FEATURE_ID)
                rule.id = std::stoi(features[TRSCRIPT_FEATURE_ID].c_str());
              if (features.size() > TRSCRIPT_FEATURE_CATEGORY)
                rule.category = std::stoi(features[TRSCRIPT_FEATURE_CATEGORY].c_str());
              if (features.size() > TRSCRIPT_FEATURE_FLAGS) {
                const std::string &flags = features[TRSCRIPT_FEATURE_FLAGS];
                for (size_t pos = 0; pos < flags.size(); pos++)
                  switch (flags[pos]) {
                  case TRSCRIPT_CH_REGEX: rule.set_regex(); break;
                  case TRSCRIPT_CH_ICASE: rule.set_icase(); break;
                  }
              }
            }
          }
        }

        if (!rule.source.empty()) { // an unique ID must be given, or I will use a negative value as a random id
          if (!rule.id)
            rule.id = --missing_id;
          if (!rule.category) // always enable category if not specified
            rule.category = -1;
          rules.push_back(rule);
        }
      }
    }

  fin.close();
  return true;
}

/** Public class */

// Construction

TranslationCoder::TranslationCoder() : d_(new D) {}
TranslationCoder::~TranslationCoder() { delete d_; }

// Use encoder which is initialized latter
int TranslationCoder::size() const { return d_->encoder->size(); }
bool TranslationCoder::isEmpty() const { return d_->encoder->isEmpty(); }

//bool TranslationCoder::isLinkEnabled() const { return d_->link; }
//void TranslationCoder::setLinkEnabled(bool t) { d_->link = t; }

//std::wstring TranslationCoder::linkStyle() const { return d_->linkStyle; }
//void TranslationCoder::setLinkStyle(const std::wstring &css) { d_->linkStyle = css; }

void TranslationCoder::clear() { d_->clear(); }

// Initialization
bool TranslationCoder::loadScript(const std::wstring &path)
{
  TranslationRuleList rules; // id, pattern, text, regex
  try {
    D::loadRules(path, rules);
  } catch (...) {
    DERR("failed to parse script");
  }

  if (rules.empty()) {
    d_->clear();
    return false;
  }

  //QWriteLocker locker(&d_->lock);

  // Initialize decoder first
  d_->decoder->setRules(rules);
  d_->encoder->setRules(rules);
  return true;
}

// Transformation

std::wstring TranslationCoder::encode(const std::wstring &text, int category, int limit) const
{
  if (text.empty() || d_->encoder->isEmpty())
    return text;
  std::wstring ret = text;
  d_->encoder->encode(ret, category, limit);
  return ret;
}

std::wstring TranslationCoder::decode(const std::wstring &text, int category, bool mark) const
{
  if (text.empty() || d_->decoder->isEmpty())
    return text;
  std::wstring ret = text;
  d_->decoder->decode(ret, category, mark);
  return ret;
}

// EOF

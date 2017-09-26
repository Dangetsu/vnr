// hanviettrans.cc
// 2/2/2015 jichi

#include "pyhanviet/hanviettrans.h"
#include "hanviet/hanvietconv.h"

#define qw(...) QString::fromStdWString(__VA_ARGS__)

/** Private class */

class HanVietTranslatorPrivate
{
public:
  HanVietConverter *conv;

  HanVietTranslatorPrivate() : conv(new HanVietConverter) {}
  ~HanVietTranslatorPrivate() { delete conv; }
};

/** Public class */

// Construction

HanVietTranslator::HanVietTranslator() : d_(new D) {}
HanVietTranslator::~HanVietTranslator() { delete d_; }

void HanVietTranslator::clear()
{
  d_->conv->clear();
}

bool HanVietTranslator::addWordFile(const QString &path)
{ return d_->conv->addWordFile(path.toStdWString()); }

bool HanVietTranslator::addPhraseFile(const QString &path)
{ return d_->conv->addPhraseFile(path.toStdWString()); }

// Conversion

QString HanVietTranslator::lookupWord(int ch) const
{ return qw(d_->conv->lookupWord(ch)); }

QString HanVietTranslator::lookupPhrase(const QString &text) const
{ return qw(d_->conv->lookupPhrase(text.toStdWString())); }

QString HanVietTranslator::toReading(const QString &text) const
{ return qw(d_->conv->toReading(text.toStdWString())); }

QString HanVietTranslator::translate(const QString &text, bool mark) const
{ return qw(d_->conv->translate(text.toStdWString(), mark)); }

QPair<QString, QList<QPair<QString, QString> > > // align ment
HanVietTranslator::analyze(const QString &text, bool mark) const
{
  QList<QPair<QString, QString> > align;
  QString trans = qw(d_->conv->analyze(text.toStdWString(), mark,
    [&align](const std::wstring &s, const std::wstring &t) {
      align.push_back(qMakePair(qw(s), qw(t)));
    }
  ));
  return qMakePair(trans, align);
}

// EOF

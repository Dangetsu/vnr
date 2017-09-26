// qhanjahangulconv.cc
// 1/6/2015
#include "pyhanja/qhanjahangulconv.h"
#include "hanjaconv/hanja2hangul.h"

//#define DEBUG "QHanjaHangulConverter.cc"
//#include "sakurakit/skdebug.h"

/** Private class */

class QHanjaHangulConverter_p
{
public:
  HanjaHangulConverter conv;
  QHanjaHangulConverter_p() {}
};

/** Public class */

// - Construction -

QHanjaHangulConverter::QHanjaHangulConverter() : d_(new D) {}
QHanjaHangulConverter::~QHanjaHangulConverter() { delete d_; }

bool QHanjaHangulConverter::isEmpty() const { return d_->conv.isEmpty(); }

void QHanjaHangulConverter::clear() { d_->conv.clear(); }

bool QHanjaHangulConverter::addWordDictionary(const QString &path)
{ return d_->conv.addWordDictionary((const wchar_t *)path.utf16()); }

bool QHanjaHangulConverter::addCharacterDictionary(const QString &path)
{ return d_->conv.addCharacterDictionary((const wchar_t *)path.utf16()); }

QString QHanjaHangulConverter::convert(const QString &text) const
{
  std::wstring s = text.toStdWString();
  d_->conv.replace(&*s.begin());
  return QString::fromStdWString(s);
}

QString QHanjaHangulConverter::lookup(const QString &text) const
{
  std::wstring s = d_->conv.lookup((const wchar_t *)text.utf16());
  return QString::fromStdWString(s);
}

int QHanjaHangulConverter::lookupCharacter(int ch) const
{ return d_->conv.lookupCharacter(ch); }

// EOF

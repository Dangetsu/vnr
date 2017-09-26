// qhangulhanjaconv.cc
// 1/6/2015
#include "pyhanja/qhangulhanjaconv.h"
#include "pyhanja/qhangulhanjaconv_p.h"
#include "hanjaconv/hangul2hanja.h"

//#define DEBUG "QHangulHanjaConverter.cc"
//#include "sakurakit/skdebug.h"

/** Private class */

class QHangulHanjaConverter_p
{
public:
  HangulHanjaConverter conv;
  QHangulHanjaConverter_p() {}
};

/** Public class */

// - Construction -

QHangulHanjaConverter::QHangulHanjaConverter() : d_(new D) {}
QHangulHanjaConverter::~QHangulHanjaConverter() { delete d_; }

int QHangulHanjaConverter::size() const { return d_->conv.size(); }
bool QHangulHanjaConverter::isEmpty() const { return d_->conv.isEmpty(); }

void QHangulHanjaConverter::clear() { d_->conv.clear(); }

bool QHangulHanjaConverter::loadFile(const QString &path)
{ return d_->conv.loadFile((const wchar_t *)path.utf16()); }

QString QHangulHanjaConverter::convert(const QString &text) const
{ return QString::fromStdWString(d_->conv.convert((const wchar_t *)text.utf16())); }

QList<QList<QPair<QString, QString> > >
QHangulHanjaConverter::parse(const QString &text) const
{
  typedef QPair<QString, QString> Pair;
  typedef QList<Pair> PairList;
  typedef QList<PairList> PairListList;

  PairListList ret;
  const wchar_t *sentence = (const wchar_t *)text.utf16();
  ::hangul_iter_words(sentence, text.size(), [&ret, sentence, this](size_t start, size_t length) {
    ret.append(PairList());
    auto &l = ret.last();

    //std::wstring word = sentence.substr(start, length);
    const wchar_t *word = sentence + start;
    this->d_->conv.collect(word, length, [&l, word](size_t start, size_t length, const wchar_t *hanja) {
      l.append(qMakePair(
        QString::fromWCharArray(word + start, length)
        , hanja ? QString::fromWCharArray(hanja) : QString()
      ));
    });
  });
  return ret;
}

// EOF

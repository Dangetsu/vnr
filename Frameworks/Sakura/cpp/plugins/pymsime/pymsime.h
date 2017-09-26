#ifndef PYMSIME_H
#define PYMSIME_H

// pymsime.h
// 4/1/2013 jichi
// Qt is used instead of pure C++ to reduce memory copy of the returned containers.

#include "sakurakit/skglobal.h"
#include <QtCore/QList>
#include <QtCore/QPair>
#include <QtCore/QString>

class Msime_p;
class Msime
{
  SK_CLASS(Msime)
  SK_DISABLE_COPY(Msime)
  SK_DECLARE_PRIVATE(Msime_p)

public:
  // - Types -

  enum Language { NoLanguage = 0, SimplifiedChinese, TraditionalChinese, Japanese, Korean };

  enum Ruby { NoRuby = 0, Pinyin, Roman, Hiragana, Katagana, Hangul };

  enum ConvertionFlag {
    NoFlag = 0
    , Autocorrect // First convert kanji to kana, and then convert back
  };

  // - Construction -

  explicit Msime(int lang);
  ~Msime();

  bool isValid() const;

  // - Actions -

  QString toKanji(const QString &text, ulong flags = 0) const;
  QList<QPair<QString, QString> > toKanjiList(const QString &text, ulong flags = 0) const;

  QString toRuby(const QString &text, int ruby) const;
  QList<QPair<QString, QString> > toRubyList(const QString &text, int ruby) const;
};

#endif // PYMSIME_H

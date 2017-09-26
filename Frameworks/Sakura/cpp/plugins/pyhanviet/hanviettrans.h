#ifndef HANVIETTRANS_H
#define HANVIETTRANS_H

// hanviettrans.h
// 2/2/2015 jichi

#include "sakurakit/skglobal.h"
#include <QtCore/QString>
#include <QtCore/QPair>
#include <QtCore/QList>

class HanVietTranslatorPrivate;
class HanVietTranslator
{
  SK_CLASS(HanVietTranslator)
  SK_DISABLE_COPY(HanVietTranslator)
  SK_DECLARE_PRIVATE(HanVietTranslatorPrivate)

  // - Construction -
public:
  explicit HanVietTranslator();
  ~HanVietTranslator();

  ///  Clear the loaded script
  void clear();

  size_t wordSize() const;
  size_t phraseSize() const;

  bool addWordFile(const QString &path);
  bool addPhraseFile(const QString &path);

  // Query

  QString lookupWord(int ch) const;
  QString lookupPhrase(const QString &text) const;

  // Replacement

  QString toReading(const QString &text) const;

  QString translate(const QString &text, bool mark = false) const;

  QPair<QString, QList<QPair<QString, QString> > > // alignment
  analyze(const QString &text, bool mark = false) const;
};

#endif // HANVIETTRANS_H

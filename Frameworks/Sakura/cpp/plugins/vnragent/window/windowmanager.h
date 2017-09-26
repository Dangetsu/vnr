#pragma once

// windowmanager.h
// 2/1/2013 jichi
// Window text manager.

#include "sakurakit/skglobal.h"
#include <QtCore/QList>
#include <QtCore/QObject>

class WindowManagerPrivate;
class WindowManager : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(WindowManager)
  SK_EXTEND_CLASS(WindowManager, QObject)
  SK_DECLARE_PRIVATE(WindowManagerPrivate)

public:
  struct TextEntry { // Window text entry QString text;
    QByteArray data; // raw text data in wchar_t format
    QString text; //  text after transcoding
    qint64 hash;  // data hash
    ulong anchor; // window hash
    uint role; // TextRole

    TextEntry() : hash(0), anchor(0) {}
    TextEntry(const QByteArray &data, const QString &text, qint64 hash, ulong anchor, uint role)
      : data(data), text(text), hash(hash), anchor(anchor), role(role) {}

    bool isEmpty() const { return !hash; }
  };
  typedef QList<TextEntry> TextEntryList;

  explicit WindowManager(QObject *parent = nullptr);
  ~WindowManager();

signals:
  //void translationChanged(); // send to main object
  void textDataChanged(QString json); // send to server

public:
  // Properties:

  void setTranslationEnabled(bool t);

  void setEncoding(const QString &v);
  void setEncodingEnabled(bool t);

  // Queries:

  QString decodeText(const QByteArray &data) const;

  const TextEntry &findEntryWithAnchor(ulong anchor) const;
  QString findTranslationWithHash(qint64 hash) const;

  // Update:
  void addEntry(const QByteArray &data, const QString &text, qint64 hash, ulong anchor, uint role);

  //void updateText(const QString &text, qint64 hash, ulong anchor);
  //void updateTextTranslation(const QString &tr, qint64 hash, qint64 trhash = 0);

  void updateTranslationData(const QString &json); // received from the server
  void clearTranslation();

  //void invalidateTexts(); // invoked when encoding changed
private slots:
  void sendDirtyTexts(); // invoked by refresh timer
};

// EOF

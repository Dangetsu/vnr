#ifndef _TEXSCRIPT_TEXHTML_H
#define _TEXSCRIPT_TEXHTML_H

// texhtml.h
// 8/19/2011 jichi

#include "sakurakit/skglobal.h"
//#include <QtCore/QMetaType>
#include <QtCore/QPair>
#include <QtCore/QString>
#include <QtCore/QStringList>
#include <QtGui/QColor>
#include <QtWebKit/QWebElement>

class TexHtmlSettingsPrivate;
class TexHtmlSettings : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(TexHtmlSettings)
  Q_PROPERTY(QString tinySize READ tinySize WRITE setTinySize NOTIFY tinySizeChanged)
  Q_PROPERTY(QString smallSize READ smallSize WRITE setSmallSize NOTIFY smallSizeChanged)
  Q_PROPERTY(QString normalSize READ normalSize WRITE setNormalSize NOTIFY normalSizeChanged)
  Q_PROPERTY(QString largeSize READ largeSize WRITE setLargeSize NOTIFY largeSizeChanged)
  Q_PROPERTY(QString hugeSize READ hugeSize WRITE setHugeSize NOTIFY hugeSizeChanged)
  Q_PROPERTY(QString urlStyle READ urlStyle WRITE setUrlStyle NOTIFY urlStyleChanged)
  Q_PROPERTY(QString hrefStyle READ hrefStyle WRITE setHrefStyle NOTIFY hrefStyleChanged)
  Q_PROPERTY(int maximumRepeat READ maximumRepeat WRITE setMaximumRepeat NOTIFY maximumRepeatChanged)
  SK_EXTEND_CLASS(TexHtmlSettings, QObject)
  SK_DECLARE_PRIVATE(TexHtmlSettingsPrivate)

  // - Constructions -
public:
  explicit TexHtmlSettings(QObject *parent = nullptr);
  ~TexHtmlSettings();

signals:
  void tinySizeChanged(QString px);
  void smallSizeChanged(QString px);
  void normalSizeChanged(QString px);
  void largeSizeChanged(QString px);
  void hugeSizeChanged(QString px);
  void urlStyleChanged(QString ss);
  void hrefStyleChanged(QString ss);
  void maximumRepeatChanged(int count);

  // - Properties -
public:
  QString tinySize() const;
  void setTinySize(const QString &px);

  QString smallSize() const;
  void setSmallSize(const QString &px);

  QString normalSize() const;
  void setNormalSize(const QString &px);

  QString largeSize() const;
  void setLargeSize(const QString &px);

  QString hugeSize() const;
  void setHugeSize(const QString &px);

  int maximumRepeat() const;
  void setMaximumRepeat(int count);

  QString urlStyle() const;
  void setUrlStyle(const QString &ss);

  QString hrefStyle() const;
  void setHrefStyle(const QString &ss);
};
//Q_DECLARE_METATYPE(TexHtmlSettings)

class TexHtmlParserPrivate;
class TexHtmlParser : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(TexHtmlParser)
  Q_PROPERTY(TexHtmlSettings* settings READ settings WRITE setSettings NOTIFY settingsChanged)
  SK_EXTEND_CLASS(TexHtmlParser, QObject)
  SK_DECLARE_PRIVATE(TexHtmlParserPrivate)

public:
  explicit TexHtmlParser(QObject *parent = nullptr);
  ~TexHtmlParser();

  TexHtmlSettings *settings() const;
public slots:
  void setSettings(TexHtmlSettings *settings);
signals:
  void settingsChanged(TexHtmlSettings *settings);

public:
  ///  Return pair of rendered HTML and cmd tags.
  Q_INVOKABLE QPair<QString, QStringList> parse(const QString &tex) const;

  ///  Return rendered HTML
  Q_INVOKABLE QString toHtml(const QString &tex) const;
};

#endif // _TEXSCRIPT_TEXHTML_H

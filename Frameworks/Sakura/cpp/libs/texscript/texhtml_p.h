#ifndef _TEXSCRIPT_TEXHTML_P_H
#define _TEXSCRIPT_TEXHTML_P_H

// texhtml_p.h
// 8/19/2011 jichi

#include <QtCore/QString>
#include <utility> // for pair

#define DEFAULT_TINY_SIZE       "10px"
#define DEFAULT_SMALL_SIZE      "18px"
#define DEFAULT_NORMAL_SIZE     "25px"
#define DEFAULT_LARGE_SIZE      "36px"
#define DEFAULT_HUGE_SIZE       "50px"
enum { DEFAULT_MAXIMUM_REPEAT = 10 };

// - Construction -

class TexHtmlSettingsPrivate
{
public:
  QString tinySize, smallSize, normalSize, largeSize, hugeSize;
  QString urlStyle, hrefStyle;
  int maximumRepeat;

  TexHtmlSettingsPrivate()
    : tinySize(DEFAULT_TINY_SIZE),
      smallSize(DEFAULT_SMALL_SIZE),
      normalSize(DEFAULT_NORMAL_SIZE),
      largeSize(DEFAULT_LARGE_SIZE),
      hugeSize(DEFAULT_HUGE_SIZE),
      maximumRepeat(DEFAULT_MAXIMUM_REPEAT) {}
};

class TexHtmlSettings;
class TexHtmlParserPrivate
{
public:
  TexHtmlSettings *settings;
  TexHtmlParserPrivate() : settings(nullptr) {}

  ///  Return pair of parsed HTML and cmd tags.
  std::pair<QString, QStringList> parse(const QString &annot) const;

private:
  ///  Translate something like \tag[attr1]{param1}{param2}[attr2]{param3}[attr3]
  QString toHtml(const QString &tag,
                 const QStringList &params = QStringList(),
                 const QStringList &attrs = QStringList()) const;

  /**
   *  Parse cmd in the beging of the text starting with '\\'.
   *  Assume \param text has been trimmed.
   *  Return parsed tag and left string if succeed, or 0 as has if failed.
   */
  static std::pair<QString, QString> parseLeadingTag(const QString &text);

  /**
   *  Return the first leading token, and the left string.
   */
  static std::pair<QString, QString> parseNextToken(const QString &text);

  static bool isSeparator(QChar c)
  {
    switch (c.unicode()) {
    case ' ': case '\n': case '\t': return true;
    default: return false;
    } Q_ASSERT(0);
  }
};

#endif // _TEXSCRIPT_TEXHTML_P_H

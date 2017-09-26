#ifndef RICHRUBYPARSER_H
#define RICHRUBYPARSER_H

// richrubyparser.h
// 6/25/2015 jichi

#include "sakurakit/skglobal.h"
#include "qtrichruby/richrubyconfig.h"
#include <QtCore/QString>
#include <functional>

QT_FORWARD_DECLARE_CLASS(QFontMetrics)
class RichRubyParserPrivate;
class RichRubyParser
{
  SK_CLASS(RichRubyParser)
  SK_DISABLE_COPY(RichRubyParser)
  SK_DECLARE_PRIVATE(RichRubyParserPrivate)

  // - Construction -
public:
  RichRubyParser();
  ~RichRubyParser();

  void setOpenMark(const QString &v);
  QString openMark() const;

  void setCloseMark(const QString &v);
  QString closeMark() const;

  void setSplitMark(const QString &v);
  QString splitMark() const;

  bool containsRuby(const QString &text) const; // return if it contains ruby tag
  QString createRuby(const QString &rb, const QString &rt) const; // create one ruby tag
  QString removeRuby(const QString &text) const; // remove all ruby tags

  typedef std::function<QString (const QString &rb, const QString &rt)> ruby_fun_t;
  QString renderRuby(const QString &text, const ruby_fun_t &fun) const;

  QString renderToPlainText(const QString &text) const;

#ifdef RICHRUBY_GUI_LIB
  // render to html-like rich text
  QString renderToHtmlTable(const QString &text, int width, const QFontMetrics &rbFont, const QFontMetrics &rtFont, int cellSpace = 1, bool wordWrap = true) const;
#endif // RICHRUBY_GUI_LIB
};

#endif // RICHRUBYPARSER_H

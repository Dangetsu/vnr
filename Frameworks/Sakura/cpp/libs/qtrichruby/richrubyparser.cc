// richrubyparser.cc
// 6/25/2015 jichi
#include "qtrichruby/richrubyparser.h"
#include <QtCore/QRegExp>
#include <QtCore/QStringList>
#include <functional>

#ifdef RICHRUBY_GUI_LIB
# include <QtGui/QFont>
# include <QtGui/QFontMetrics>
#endif // RICHRUBY_GUI_LIB

/** Private class */

class RichRubyParserPrivate
{
  typedef RichRubyParser Q;
public:
  QString openMark, closeMark, splitMark;

  RichRubyParserPrivate()
    : openMark(RICHRUBY_OPEN_MARK), closeMark(RICHRUBY_CLOSE_MARK), splitMark(RICHRUBY_SPLIT_MARK) {}

  bool containsRuby(const QString &text) const
  {
    int pos = text.indexOf(openMark);
    return pos != -1
        && (pos = text.indexOf(splitMark, pos + 1)) != -1
        && (pos = text.indexOf(closeMark, pos + 1)) != -1;
  }

  QString createRuby(const QString &rb, const QString &rt) const
  { return QString(openMark).append(rt).append(splitMark).append(rb).append(closeMark); }

  void removeRuby(QString &text) const;
  void renderRuby(QString &text, const Q::ruby_fun_t &fun) const;

private:
  /**
   *  @param  rb
   *  @param  rt
   *  @param  pos  the postion in the original text directly after ruby
   *  //@param  prefix  html prefix tag
   *  //@param  suffix  html suffix tag
   *  @return  if stop iteration. pos it the parsed offset
   */
  typedef std::function<bool (const QString &rb, const QString &rt, int pos)> ruby_fun_t;
  void iterRuby(const QString &text, const ruby_fun_t &fun) const;

  // Get html close tag at position. For example, given "</a>", it will return "a"
  static QString get_html_close_tag(const QString &text, int startPos = 0, int *stopPos = nullptr)
  {
    if (text.size() < 4 || text[startPos] != '<' || text[startPos + 1] != '/')
      return QString();
    startPos += 2;
    for (int i = startPos; i < text.size(); i++) {
      const QChar &ch = text[i];
      wchar_t w = ch.unicode();
      if (w > 127)
        break;
      if (w == '>') {
        QString ret = text.mid(startPos, i - startPos);
        if (stopPos)
          *stopPos = i + 1;
        return ret.trimmed();
      }
    }
    return QString();
  }

#ifdef RICHRUBY_GUI_LIB
public:
  QString renderTable(const QString &text, int width, const QFontMetrics &rbFont, const QFontMetrics &rtFont, int cellSpace, bool wordWrap) const;
private:
  static int textWidth(const QString &text, const QFontMetrics &font);
  static QString partition(const QString &text, int width, const QFontMetrics &font, bool wordWrap, int maximumWordSize);
#endif // RICHRUBY_GUI_LIB
};

void RichRubyParserPrivate::iterRuby(const QString &text,  const ruby_fun_t &fun) const
{
  const bool html = text.contains("</");
  QString plainText;
  int pos = 0;
  for (int openPos = text.indexOf(openMark); openPos != -1; openPos = text.indexOf(openMark, pos)) {
    int splitPos = text.indexOf(splitMark, openPos + 1);
    if (splitPos == -1)
      break;
    int closePos = text.indexOf(closeMark, splitPos + 1);
    if (closePos == -1)
      break;
    if (pos != openPos)
      plainText = text.mid(pos, openPos - pos);
    QString rt = text.mid(openPos + openMark.size(), splitPos - openPos - openMark.size()),
            rb = text.mid(splitPos + splitMark.size(), closePos - splitPos - splitMark.size());
    pos = closePos + closeMark.size();
    // Move the most enclosing links into that for rb
    if (html && openPos > 0 && text[openPos-1] == '>' && pos != text.size() && text[pos] == '<' && !plainText.isEmpty()) {
      int stopPos;
      QString tag = get_html_close_tag(text, pos, &stopPos);
      if (!tag.isEmpty())  {
        tag.push_front('<');
        int startPos = plainText.lastIndexOf(tag);
        if (startPos != -1) {
          QString leftTag = plainText.mid(startPos),
                  rightTag = text.mid(pos, stopPos - pos);
          rb.prepend(leftTag)
            .append(rightTag);
          plainText = plainText.left(startPos);
          pos = stopPos;
        }
      }
    }
    if (!plainText.isEmpty()) {
      if (!fun(plainText, QString(), openPos))
        return;
      plainText.clear();
    }
    if (!fun(rb, rt, pos))
      return;
  }

  if (pos < text.size()) {
    plainText = text.mid(pos);
    fun(plainText, QString(), text.size());
  }
}

void RichRubyParserPrivate::removeRuby(QString &ret) const
{
  for (int pos = ret.indexOf(openMark); pos != -1; pos = ret.indexOf(openMark, pos)) {
    int splitPos = ret.indexOf(splitMark, pos + 1);
    if (splitPos == -1)
      return;
    int closePos = ret.indexOf(closeMark, splitPos + 1);
    if (closePos == -1)
      return;
    ret.remove(closePos, closeMark.size());
    ret.remove(pos, splitPos - pos + splitMark.size());
    pos += closePos - splitPos - splitMark.size();
  }
}

void RichRubyParserPrivate::renderRuby(QString &ret, const Q::ruby_fun_t &fun) const
{
  for (int pos = ret.indexOf(openMark); pos != -1; pos = ret.indexOf(openMark, pos)) {
    int splitPos = ret.indexOf(splitMark, pos + 1);
    if (splitPos == -1)
      return;
    int closePos = ret.indexOf(closeMark, splitPos + 1);
    if (closePos == -1)
      return;
    QString rt = ret.mid(pos + openMark.size(), splitPos - pos - openMark.size()),
            rb = ret.mid(splitPos + splitMark.size(), closePos - splitPos - splitMark.size()),
            repl = fun(rb, rt);
    ret.remove(pos, closePos + closeMark.size() - pos);
    ret.insert(pos, repl);
    pos += repl.size();
  }
}

#ifdef RICHRUBY_GUI_LIB

int RichRubyParserPrivate::textWidth(const QString &text, const QFontMetrics &font)
{
  if (text.isEmpty())
    return 0;
  if (!text.contains('<') || !text.contains('>'))
    return font.width(text);

  static QRegExp rx("<.+>");
  if (!rx.isMinimal())
    rx.setMinimal(true);

  QString t = QString(text).remove(rx);
  return font.width(t);
}

QString RichRubyParserPrivate::partition(const QString &text, int width, const QFontMetrics &font, bool wordWrap, int maximumWordSize)
{
  QString ret;
  if (width <= 0 || text.isEmpty())
    return ret;
  int retWidth = 0;
  int spacePos = -1;
  QString suffix;
  for (int pos = 0; pos < text.size(); pos++) {
    const QChar &ch = text[pos];
    if (ch.unicode() == '<') { // skip
      int closePos = text.indexOf('>', pos);
      if (closePos != -1) {
        // TODO: Avoid HTML tags from being broken in the middle
        //if (text[pos + 1] != '/' && text[closePos - 1] != '/') {
        //  // do nothing
        //}
        QString tag = text.mid(pos, closePos - pos + 1);
        ret.append(tag);
        pos = closePos;
        continue;
      }
    }
    if (wordWrap && ch.isSpace())
      spacePos = pos;
    retWidth += font.width(ch);
    if (retWidth > width) {
      if (wordWrap && spacePos >= 0 && spacePos < pos && pos - spacePos < maximumWordSize)
        ret = ret.left(spacePos + 1);
      break;
    }
    ret.push_back(ch);
  }
  if (!suffix.isEmpty())
    ret.append(suffix);
  return ret;
}

QString RichRubyParserPrivate::renderTable(const QString &text, int width, const QFontMetrics &rbFont, const QFontMetrics &rtFont, int cellSpace, bool wordWrap) const
{
  QString ret;
  QStringList rbList,
              rtList;
  int maximumWordSize = width / 4 + 1;
  int tableWidth = 0;

  const int rbMinCharWidth = rbFont.width(' ') / 4;
            //rtMinCharWidth = rtFont.width(' ') / 4;

  width -= rbMinCharWidth + cellSpace;
  if (width < 0)
    width = 0;

  auto reduce = [&]() {
    bool rbEmpty = true,
         rtEmpty = true;
    if (!rbList.isEmpty())
      foreach (const QString &it, rbList)
        if (!it.isEmpty()) {
          rbEmpty = false;
          break;
        }
    if (!rtList.isEmpty())
      foreach (const QString &it, rtList)
        if (!it.isEmpty()) {
          rtEmpty = false;
          break;
        }
    if (!rbEmpty || !rtEmpty) {
      if (rbEmpty)
        ret.append("<div class='rt'>")
           .append(rtList.join(QString()))
           .append("</div>");
      else if (rtEmpty)
        ret.append("<div class='rb'>")
           .append(rbList.join(QString()))
           .append("</div>");
      else {
        QString rbtd,
                rttd;
        foreach (const QString &it, rbList)
          if (it.isEmpty())
            rbtd.append("<td/>");
          else
            rbtd.append("<td align='center'>")
                .append(it)
                .append("</td>");
        foreach (const QString &it, rtList)
          if (it.isEmpty())
            rttd.append("<td/>");
          else
            rttd.append("<td align='center'>")
                .append(it)
                .append("</td>");
        ret.append("<table>")
           .append("<tr class='rt' valigh='bottom'>").append(rttd).append("</tr>")
           .append("<tr class='rb'>").append(rbtd).append("</tr>")
           .append("</table>");
      }
    }

    rbList.clear();
    rtList.clear();
    tableWidth = 0;
  };
  auto iter = [&](const QString &_rb, const QString &rt, int pos) -> bool {
    QString rb = _rb;
    const bool atLast = pos == text.size();
    if (rt.isEmpty() && ret.isEmpty() && atLast && rb == text) {
      ret = text;
      return false;
    }
    int cellWidth =  qMax(textWidth(rb, rbFont), textWidth(rt, rtFont));
    if (rt.isEmpty() && rb.size() > 1
        && width && tableWidth < width && tableWidth + cellWidth > width) { // split very long text
      QString left = partition(rb, width + rbMinCharWidth - tableWidth, rbFont, wordWrap, maximumWordSize);
      if (!left.isEmpty()) {
        tableWidth += textWidth(left, rbFont);
        rb = rb.mid(left.size());
        cellWidth = rb.isEmpty() ? 0 : textWidth(rb, rbFont);
        rbList.append(left);
        rtList.append(QString());
        reduce();
      }
    }
    if (tableWidth > 0 && width && tableWidth + cellWidth > width // reduce table here
        && (!rbList.isEmpty() || !rtList.isEmpty()))
      reduce();
    if (rt.isEmpty() && width && !tableWidth) {
      if (atLast) {
        rbList.append(rb);
        rtList.append(QString());
        return false;
      }

      while (rb.size() > 1 && cellWidth > width) { // split very long text
        QString left = partition(rb, width + rbMinCharWidth - tableWidth, rbFont, wordWrap, maximumWordSize);
        if (left.isEmpty())
          break;
        else {
          tableWidth += textWidth(left, rbFont);
          rb = rb.mid(left.size());
          cellWidth = textWidth(rb, rbFont);
          rbList.append(left);
          rtList.append(QString());
          reduce();
        }
      }
    }
    tableWidth += cellWidth + cellSpace;
    rbList.append(rb);
    rtList.append(rt);
    return true;
  };
  iterRuby(text, iter);
  if (!rbList.isEmpty() || !rtList.isEmpty())
    reduce();
  return ret;
}

#endif // RICHRUBY_GUI_LIB

/** Public class */

RichRubyParser::RichRubyParser() : d_(new D) {}
RichRubyParser::~RichRubyParser() { delete d_; }

QString RichRubyParser::openMark() const { return d_->openMark; }
void RichRubyParser::setOpenMark(const QString &v) { d_->openMark = v; }

QString RichRubyParser::closeMark() const { return d_->closeMark; }
void RichRubyParser::setCloseMark(const QString &v) { d_->closeMark = v; }

QString RichRubyParser::splitMark() const { return d_->splitMark; }
void RichRubyParser::setSplitMark(const QString &v) { d_->splitMark = v; }

bool RichRubyParser::containsRuby(const QString &text) const
{ return d_->containsRuby(text); }

QString RichRubyParser::createRuby(const QString &rb, const QString &rt) const
{ return d_->createRuby(rb, rt); }

QString RichRubyParser::removeRuby(const QString &text) const
{
  if (!containsRuby((text)))
    return text;
  QString ret = text;
  d_->removeRuby(ret);
  return ret;
}

QString RichRubyParser::renderRuby(const QString &text, const ruby_fun_t &fun) const
{
  if (!containsRuby((text)))
    return text;
  QString ret = text;
  d_->renderRuby(ret, fun);
  return ret;
}

QString RichRubyParser::renderToPlainText(const QString &text) const
{
  return renderRuby(text, [](const QString &rb, const QString &rt) -> QString {
    static QString fmt = RICHRUBY_PLAINTEXT_FORMAT;
    return fmt.arg(rb, rt);
  });
}

#ifdef RICHRUBY_GUI_LIB

QString RichRubyParser::renderToHtmlTable(const QString &text, int width, const QFontMetrics &rbFont, const QFontMetrics &rtFont, int cellSpace, bool wordWrap) const
{
  if (!containsRuby((text)))
    return text;
  QString t = text;
  if (t.contains("  ")) {
    static QRegExp rx(" +(\\s)"); // remove spaces before any other space
    t.replace(rx, "\\1");
  }
  return d_->renderTable(t, width, rbFont, rtFont, cellSpace, wordWrap);
}

#endif // RICHRUBY_GUI_LIB

// EOF

/*
void RichRubyParserPrivate::iterRuby(const QString &text,  const ruby_fun_t &fun) const
{
  QString rb, rt, plainText;
  bool rubyOpenFound = false,
       rubySplitFound = false;

  auto cancel = [&]() {
    if (rubyOpenFound) {
      rubyOpenFound = false;
      plainText.push_back(openChar);
    } if (!rb.isEmpty()) {
      plainText.append(rb);
      rb.clear();
    }
    if (rubySplitFound) {
      rubySplitFound = false;
      plainText.push_back(splitChar);
    }
    if (!rt.isEmpty()) {
      //plainText.push_back(closeChar);
      plainText.append(rt);
      rt.clear();
    }
  };

  int pos = 0;
  for (; pos < text.size(); pos++) {
    const QChar &ch = text[pos];
    auto u = ch.unicode();
    if (u == '<') {
      int closePos = text.indexOf('>', pos);
      if (closePos != -1) {
        // TODO: Avoid HTML tags from being broken in the middle
        //if (text[pos + 1] != '/' && text[closePos - 1] != '/') {
        //  // do nothing
        //}
        QString tag = text.mid(pos, closePos - pos + 1);
        (!rubyOpenFound ? plainText : rubySplitFound ? rt : rb).append(tag);
        pos = closePos;
        continue;
      }
    }
    if (u == openChar) {
      if (rubyOpenFound) // error
        cancel();
      if (!plainText.isEmpty()) {
        if (!fun(plainText, QString(), pos))
          return;
        plainText.clear();
      }
      rubyOpenFound = true;
    } else if (u == splitChar) {
      if (!rubyOpenFound) // error
        plainText.push_back(ch);
      else if (rb.isEmpty()) { // error, do not allow having only rt
        cancel();
        plainText.push_back(ch);
      } else if (rubySplitFound) // error
        rt.push_back(ch);
      else
        rubySplitFound = true;
    } else if (u == closeChar) {
      if (!rubyOpenFound) // error
        plainText.push_back(ch);
      else if (rt.isEmpty() || rb.isEmpty()) { // error, do not allow having only rb or rt
        cancel();
        plainText.push_back(ch);
      } else {
        if (!fun(rb, rt, pos + 1))
          return;
        rubySplitFound = rubyOpenFound = false;
        rb.clear();
        rt.clear();
      }
    } else
      (!rubyOpenFound ? plainText : rubySplitFound ? rt : rb).push_back(ch);
  }
  if (!rb.isEmpty() && !rt.isEmpty())
    fun(rb, rt, pos);
  else
    cancel();
  if (!plainText.isEmpty())
    fun(plainText, QString(), pos);
}
*/

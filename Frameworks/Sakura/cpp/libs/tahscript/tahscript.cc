// tahscript.cc
// 8/14/2014 jichi

#include "tahscript/tahscript.h"
#include <QtCore/QString>
#include <QtCore/QFile>
#include <QtCore/QTextStream>
#include <QtCore/QRegExp>

//#include <QtCore/QReadWriteLock> // thread-safety
//#include <QtCore/QReadLocker>
//#include <QtCore/QWriteLocker>

#include <list> // instead of QList which is slow that stores pointers instead of elements
#include <utility> // for pair which is faster than QPair
#include <boost/foreach.hpp>

#define DEBUG "tahscript.cc"
#include "sakurakit/skdebug.h"

//#define DEBUG_RULE // output the rule that is applied

#define TAHSCRIPT_COMMENT_CHAR1     '#' // indicate the beginning of a line comment
#define TAHSCRIPT_COMMENT_CHAR2     '*' // original comment
#define TAHSCRIPT_COMMENT_CHAR3     '=' // wiki section
//#define TAHSCRIPT_COMMENT_CHAR_LEN  1 // not used
#define TAHSCRIPT_RULE_DELIM        '\t' // deliminator of the rule pair
enum { TAHSCRIPT_RULE_DELIM_LEN = 1 };
//enum { TAHSCRIPT_RULE_DELIM_LEN = (sizeof(TAHSCRIPT_RULE_DELIM)  - 1) }; // strlen

/** Helpers */

namespace { // unnamed

struct TahScriptRule
{
  QString source;
  QString target;
  QRegExp *sourceRe; // cached compiled regex

  TahScriptRule() : sourceRe(nullptr) {}
  ~TahScriptRule() { if (sourceRe) delete sourceRe; }

  bool init(const QString &s, const QString &t)
  {
    if (isRegExp(s)) {
      QRegExp *re = new QRegExp(s, Qt::CaseSensitive, QRegExp::RegExp2); // use Perl-compatible syntax, default in Qt5
      if (re->isEmpty()) {
        DERR("invalid regexp:" << s);
        delete re;
        return false;
      }
      sourceRe = re;
      target = t;
      target.replace('$', '\\'); // convert Javascript RegExp to Perl
    } else {
      source = s;
      target = t;
    }
    return true;
  }

private:
  static bool isRegExp(const QString &s)
  {
    foreach (const QChar &c, s)
      switch (c.unicode()) {
      case '(': case ')': case '[': case ']': case '^': case '$':
      case '|': case '\\': case '?': case '!': case '+': case '*': case '.':
      //case ':': case '{': case '}':
        return true;
      }
    return false;
  }
};

} // unnamed namespace

/** Private class */

class TahScriptManagerPrivate
{
public:
  //QReadWriteLock lock;

  TahScriptRule *rules; // use array for performance reason
  size_t ruleCount;

  TahScriptManagerPrivate() : rules(nullptr), ruleCount(0) {}
  ~TahScriptManagerPrivate() { if (rules) delete[] rules; }

  void clear()
  {
    ruleCount = 0;
    if (rules) {
      delete[] rules;
      rules = nullptr;
    }
  }

  void reset(size_t size)
  {
    DOUT(size);
    Q_ASSERT(size > 0);
    //if (ruleCount != size) {
    ruleCount = size;
    if (rules)
      delete[] rules;
    rules = new TahScriptRule[size];
    //}
  }
};

/** Public class */

// Construction

TahScriptManager::TahScriptManager() : d_(new D) {}
TahScriptManager::~TahScriptManager() { delete d_; }


int TahScriptManager::size() const { return d_->ruleCount; }
bool TahScriptManager::isEmpty() const { return !d_->ruleCount; }

void TahScriptManager::clear()
{
  //QWriteLocker locker(&d_->lock);
  d_->clear();
}

// Initialization
bool TahScriptManager::loadFile(const QString &path)
{
  // File IO
  // http://stackoverflow.com/questions/2612103/qt-reading-from-a-text-file
  QFile file(path);
  if (!file.open(QIODevice::ReadOnly)) {
    DERR("failed to open file at path:" << path);
    return false;
  }

  std::list<std::pair<QString, QString> > lines;

  QTextStream in(&file);
  in.setCodec("UTF-8"); // enforce UTF-8
  while (!in.atEnd()) {
    QString line = in.readLine(); // including the trailing \n
    if (!line.isEmpty())
      switch (line[0].unicode()) {
      case TAHSCRIPT_COMMENT_CHAR1:
      case TAHSCRIPT_COMMENT_CHAR2:
      case TAHSCRIPT_COMMENT_CHAR3:
        break;
      default:
        int index = line.indexOf(TAHSCRIPT_RULE_DELIM);
        QString left, right;
        if (index == -1)
          left = line;
        else {
          left = line.left(index); //.trimmed()
          right = line.mid(index + TAHSCRIPT_RULE_DELIM_LEN);
        }
        lines.push_back(std::make_pair(left, right));
      }
  }
  file.close();

  if (lines.empty()) {
    d_->clear();
    return false;
  }

  //QWriteLocker locker(&d_->lock);
  d_->reset(lines.size());

  size_t i = 0;
  BOOST_FOREACH (const auto &it, lines)
    d_->rules[i++].init(it.first, it.second);

  return true;
}

// Translation
QString TahScriptManager::translate(const QString &text) const
{
  //QReadLocker locker(&d_->lock);
  QString ret = text;
#ifdef DEBUG_RULE
  QString previous = text;
#endif // DEBUG_RULE
  if (d_->ruleCount && d_->rules)
    for (size_t i = 0; i < d_->ruleCount; i++) {
      const auto &rule = d_->rules[i];
      if (rule.sourceRe) {
        if (rule.target.isEmpty())
          ret.remove(*rule.sourceRe);
        else
          ret.replace(*rule.sourceRe, rule.target);
      } else if (!rule.source.isEmpty()) {
        if (rule.target.isEmpty())
          ret.remove(rule.source);
        else
          ret.replace(rule.source, rule.target);
      }

#ifdef DEBUG_RULE
      if (previous != ret) {
        if (rule.sourceRe)
          DOUT(rule.sourceRe->pattern() << rule.target << ret);
        else
          DOUT(rule.source << rule.target << ret);
      }
      previous = ret;
#endif // DEBUG_RULE
    }
  return ret;
}

// EOF

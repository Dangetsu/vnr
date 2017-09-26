// texhtml.cc
// 8/19/2011 jichi

#include "texscript/texhtml.h"
#include "texscript/texhtml_p.h"

//#define DEBUG "texhtml"
#include "sakurakit/skdebug.h"

//namespace { // unnamed
//struct init_ { init_() {
//  qRegisterMetaType<TexHtmlSettings>("TexHtmlSettings");
//} };
//init_ init_;
//} // unnamed namespace

// - Settings -

TexHtmlSettings::TexHtmlSettings(QObject *parent) : Base(parent), d_(new D) {}
TexHtmlSettings::~TexHtmlSettings() { delete d_; }

#define SYNTHESIZE(_ret_type, _ref_type, _getter, _setter) \
  _ret_type TexHtmlSettings::_getter() const \
  { return d_->_getter; } \
  void TexHtmlSettings::_setter(_ref_type px) \
  {  if (d_->_getter != px) emit _getter##Changed(d_->_getter = px); }

  SYNTHESIZE(QString, const QString &, tinySize, setTinySize)
  SYNTHESIZE(QString, const QString &, smallSize, setSmallSize)
  SYNTHESIZE(QString, const QString &, normalSize, setNormalSize)
  SYNTHESIZE(QString, const QString &, largeSize, setLargeSize)
  SYNTHESIZE(QString, const QString &, hugeSize, setHugeSize)
  SYNTHESIZE(QString, const QString &, urlStyle, setUrlStyle)
  SYNTHESIZE(QString, const QString &, hrefStyle, setHrefStyle)
  SYNTHESIZE(int, int, maximumRepeat, setMaximumRepeat)
#undef SYNTHESIZE

// - Parser -

TexHtmlParser::TexHtmlParser(QObject *parent)
  : Base(parent), d_(new D)
{ DOUT("pass"); }

TexHtmlParser::~TexHtmlParser()
{
  delete d_;
  DOUT("pass");
}

TexHtmlSettings *TexHtmlParser::settings() const
{
  if (Q_UNLIKELY(!d_->settings))
    d_->settings = new TexHtmlSettings(self());
  return d_->settings;
}

void TexHtmlParser::setSettings(TexHtmlSettings *settings)
{
  if (Q_LIKELY(settings != d_->settings)) {
    if (d_->settings && d_->settings->parent() == this)
      d_->settings->deleteLater();
    d_->settings = settings;
    if (settings)
      settings->setParent(this);

    emit settingsChanged(settings);
  }
}

QPair<QString, QStringList> TexHtmlParser::parse(const QString &text) const
{
  auto ret = d_->parse(text);
  return qMakePair(ret.first, ret.second);
}

QString TexHtmlParser::toHtml(const QString &tex) const
{ return parse(tex).first; }

// EOF

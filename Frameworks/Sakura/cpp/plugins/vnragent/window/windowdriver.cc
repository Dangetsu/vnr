// windowdriver.cc
// 2/1/2013 jichi

#include "window/windowdriver.h"
#include "window/windowdriver_p.h"
#include "window/windowmanager.h"
#include "util/codepage.h"

WindowDriver::WindowDriver(QObject *parent)
  : Base(parent), d_(new D(this))
{
  connect(d_->manager, SIGNAL(textDataChanged(QString)), SIGNAL(translationRequested(QString)));
}

void WindowDriver::updateTranslation(const QString &json) { d_->manager->updateTranslationData(json); }
void WindowDriver::clearTranslation() { d_->manager->clearTranslation(); }

void WindowDriver::setEnabled(bool t)
{
  if (d_->enabled != t) {
    d_->enabled = t;
    d_->manager->setTranslationEnabled(d_->translationEnabled && t);
  }
}

void WindowDriver::setTextVisible(bool t) { d_->textVisible = t; }

void WindowDriver::setTranslationEnabled(bool t)
{
  if (d_->translationEnabled != t) {
    d_->translationEnabled = t;
    d_->manager->setTranslationEnabled(d_->enabled && t);
  }
}

void WindowDriver::setTranscodingEnabled(bool t) { d_->manager->setEncodingEnabled(t); }
void WindowDriver::setEncoding(const QString &v)
{
  if (v.toLower() == ENC_UTF16)
    d_->manager->setEncoding(ENC_SJIS);
  else
    d_->manager->setEncoding(v);
}

// EOF

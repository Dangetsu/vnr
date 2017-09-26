// qthelper_p.cc
// 12/9/2012 jichi

#include "qmlhelperplugin/qthelper_p.h"
#include <QtCore/QObject>

QtHelper::QtHelper(QObject *parent): Base(parent) {}

void QtHelper::deleteObject(QObject *q)
{
  if (q) {
    q->setParent(nullptr);
    delete q;
  }
}

// EOF

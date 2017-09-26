// qmlhelperplugin.cc
// 11/12/2012 jichi
#include "qmlhelperplugin/qmlhelperplugin.h"
#include "qmlhelperplugin/qmlhelper_p.h"
#include "qmlhelperplugin/qthelper_p.h"
#include <QtDeclarative/qdeclarative.h>

QmlHelperPlugin::QmlHelperPlugin(QObject *parent)
  : Base(parent) {}

void QmlHelperPlugin::registerTypes(const char *uri)
{
  qmlRegisterType<QmlHelper>(uri, 1, 0, "QmlHelper");
  qmlRegisterType<QtHelper>(uri, 1, 0, "QtHelper");
}

Q_EXPORT_PLUGIN2(qmlhelperplugin, QmlHelperPlugin);

// EOF

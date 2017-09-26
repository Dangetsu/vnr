// qmlgradientplugin.cc
// 9/14/2014 jichi
#include "qmlgradientplugin/qmlgradientplugin.h"
#include "qmlgradient/lineargradient.h"
#include <QtDeclarative/qdeclarative.h>

QmlGradientPlugin::QmlGradientPlugin(QObject *parent)
  : Base(parent) {}

void QmlGradientPlugin::registerTypes(const char *uri)
{
  qmlRegisterType<DeclarativeLinearGradient>(uri, 1, 0, "LinearGradient");
}

Q_EXPORT_PLUGIN2(qmlgradientplugin, QmlGradientPlugin);

// EOF

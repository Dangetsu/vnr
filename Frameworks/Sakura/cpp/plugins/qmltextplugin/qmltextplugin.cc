// qmltextplugin.cc
// 4/5/2014 jichi
#include "qmltextplugin/qmltextplugin.h"
#include "qmltext/contouredtextedit.h"
#include <QtDeclarative/qdeclarative.h>

QmlTextPlugin::QmlTextPlugin(QObject *parent)
  : Base(parent) {}

void QmlTextPlugin::registerTypes(const char *uri)
{
  //qmlRegisterType<DeclarativeContouredText>(uri, 1, 0, "ContouredText");
  qmlRegisterType<DeclarativeContouredTextEdit>(uri, 1, 0, "ContouredTextEdit");
}

Q_EXPORT_PLUGIN2(qmltextplugin, QmlTextPlugin);

// EOF

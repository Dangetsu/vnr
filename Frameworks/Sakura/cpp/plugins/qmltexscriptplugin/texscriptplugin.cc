// texscriptplugin.cc
// 11/12/2012 jichi
#include "qmltexscriptplugin/texscriptplugin.h"
#include "texscript/texhtml.h"
#include <QtDeclarative/qdeclarative.h>

TexScriptPlugin::TexScriptPlugin(QObject *parent)
  : Base(parent) {}

void TexScriptPlugin::registerTypes(const char *uri)
{
  qmlRegisterType<TexHtmlParser>(uri, 1, 0, "TexHtmlParser");
  qmlRegisterType<TexHtmlSettings>(uri, 1, 0, "TexHtmlSettings");
}

Q_EXPORT_PLUGIN2(texscriptplugin, TexScriptPlugin);

// EOF

#ifndef TEXSCRIPTPLUGIN_H
#define TEXSCRIPTPLUGIN_H

// texscriptplugin.h
// 11/12/2012 jichi

#include <QtDeclarative/QDeclarativeExtensionPlugin>

class TexScriptPlugin : public QDeclarativeExtensionPlugin
{
  Q_OBJECT
  typedef QDeclarativeExtensionPlugin Base;
public:
  explicit TexScriptPlugin(QObject *parent = nullptr);
  void registerTypes(const char *uri) override;
};

#endif // TEXSCRIPTPLUGIN_H

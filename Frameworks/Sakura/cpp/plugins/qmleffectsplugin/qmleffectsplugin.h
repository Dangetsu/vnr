#ifndef QMLEFFECTSPLUGIN_H
#define QMLEFFECTSPLUGIN_H

// qmleffectsplugin.h
// 11/12/2012 jichi

 #include <QtDeclarative/QDeclarativeExtensionPlugin>

class QmlEffectsPlugin : public QDeclarativeExtensionPlugin
{
  Q_OBJECT
  typedef QDeclarativeExtensionPlugin Base;
public:
  explicit QmlEffectsPlugin(QObject *parent = nullptr);
  void registerTypes(const char *uri) override;
};

#endif // QMLEFFECTSPLUGIN_H

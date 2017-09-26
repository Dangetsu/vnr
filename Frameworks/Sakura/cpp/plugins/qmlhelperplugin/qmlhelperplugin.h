#ifndef QMLHELPERPLUGIN_H
#define QMLHELPERPLUGIN_H

// qmlhelperplugin.h
// 11/12/2012 jichi

#include <QtDeclarative/QDeclarativeExtensionPlugin>

class QmlHelperPlugin : public QDeclarativeExtensionPlugin
{
  Q_OBJECT
  typedef QDeclarativeExtensionPlugin Base;
public:
  explicit QmlHelperPlugin(QObject *parent = nullptr);
  void registerTypes(const char *uri) override;
};

#endif // QMLHELPERPLUGIN_H

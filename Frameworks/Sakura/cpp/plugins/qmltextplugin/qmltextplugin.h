#ifndef QMLTEXT_H
#define QMLTEXT_H

// qmltext.h
// 4/5/2014 jichi

#include <QtDeclarative/QDeclarativeExtensionPlugin>

class QmlTextPlugin : public QDeclarativeExtensionPlugin
{
  Q_OBJECT
  typedef QDeclarativeExtensionPlugin Base;
public:
  explicit QmlTextPlugin(QObject *parent = nullptr);
  void registerTypes(const char *uri) override;
};

#endif // QMLTEXT_H

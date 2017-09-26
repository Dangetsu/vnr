#ifndef QMLGRADIENT_H
#define QMLGRADIENT_H

// qmlgradient.h
// 9/14/2014 jichi

#include <QtDeclarative/QDeclarativeExtensionPlugin>

class QmlGradientPlugin : public QDeclarativeExtensionPlugin
{
  Q_OBJECT
  typedef QDeclarativeExtensionPlugin Base;
public:
  explicit QmlGradientPlugin(QObject *parent = nullptr);
  void registerTypes(const char *uri) override;
};

#endif // QMLGRADIENT_H

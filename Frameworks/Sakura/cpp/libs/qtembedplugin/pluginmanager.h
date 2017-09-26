#ifndef _QTEMBEDPLUGIN_PLUGINMANAGER_H
#define _QTEMBEDPLUGIN_PLUGINMANAGER_H

// pluginmanager.h
// 5/21/2015 jichi

#include "qtembedplugin/qtembedplugin.h"
#include "sakurakit/skglobal.h"
#include <QtCore/QString>

QT_FORWARD_DECLARE_CLASS(QObject)

QTEMBEDPLUGIN_BEGIN_NAMESPACE

class PluginManagerPrivate;
class PluginManager
{
  SK_CLASS(PluginManager)
  SK_DISABLE_COPY(PluginManager)
  SK_DECLARE_PRIVATE(PluginManagerPrivate)

public:
  PluginManager();
  ~PluginManager();

  static Self *globalInstance(); // not null

  void setPrefix(const QString &value); // qt.rc prefix, must be set before everything else
  QString prefix() const;

  QObject *loadPlugin(const QString &path);
};

QTEMBEDPLUGIN_END_NAMESPACE

#endif // _QTEMBEDPLUGIN_PLUGINMANAGER_H

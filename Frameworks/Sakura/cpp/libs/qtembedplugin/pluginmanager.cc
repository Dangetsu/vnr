// pluginmanager.cc
// 5/21/2015 jichi
// See: http://labplot.sourceforge.net/developer/plugins/
#include "qtembedplugin/pluginmanager.h"
#include <QtCore/QPluginLoader>
#include <QtCore/QHash>

#define DEBUG "embedplugin::pluginmanager"
#include "sakurakit/skdebug.h"

QTEMBEDPLUGIN_BEGIN_NAMESPACE

/** Private class */

class PluginManagerPrivate
{
public:
  QString prefix;
  QHash<QString, QPluginLoader *> plugins;

  ~PluginManagerPrivate()
  {
    if (!plugins.isEmpty())
      for (auto p = plugins.begin(); p != plugins.end(); ++p)
        delete p.value();
  }
};

/** Public class */

// - Construction -

PluginManager::PluginManager() : d_(new D) {}
PluginManager::~PluginManager() { delete d_; }

PluginManager *PluginManager::globalInstance()
{
  static Self g;
  return &g;
}

QString PluginManager::prefix() const { return d_->prefix; }
void PluginManager::setPrefix(const QString &value) { d_->prefix = value; }
QObject *PluginManager::loadPlugin(const QString &path)
{
  QString fileName = path;
  if (!d_->prefix.isEmpty())
    fileName.prepend('/')
            .prepend(d_->prefix);
  QPluginLoader *loader = d_->plugins.value(fileName);
  if (!loader) {
    loader = d_->plugins[fileName] = new QPluginLoader(fileName);
    DOUT("ok =" << loader->instance() << ", path =" << fileName);
  }
  return loader->instance();
}

QTEMBEDPLUGIN_END_NAMESPACE

// EOF

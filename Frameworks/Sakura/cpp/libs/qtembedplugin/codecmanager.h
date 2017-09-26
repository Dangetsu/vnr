#ifndef _QTEMBEDPLUGIN_CODECMANAGER_H
#define _QTEMBEDPLUGIN_CODECMANAGER_H

// codecmanager.h
// 5/21/2015 jichi

#include "qtembedplugin/qtembedplugin.h"
#include "sakurakit/skglobal.h"
#include <QtCore/QString>

QT_FORWARD_DECLARE_CLASS(QTextCodec)

QTEMBEDPLUGIN_BEGIN_NAMESPACE

class PluginManager;
class CodecManagerPrivate;
class CodecManager
{
  SK_CLASS(CodecManager)
  SK_DISABLE_COPY(CodecManager)
  SK_DECLARE_PRIVATE(CodecManagerPrivate)

public:
  explicit CodecManager(PluginManager *plugin = nullptr);
  ~CodecManager();

  static Self *globalInstance(); // not null

  QTextCodec *codecForName(const char *name);
};

QTEMBEDPLUGIN_END_NAMESPACE

#endif // _QTEMBEDPLUGIN_PLUGINMANAGER_H

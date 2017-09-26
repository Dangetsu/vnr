// codecmanager.cc
// 5/21/2015 jichi
#include "qtembedplugin/codecmanager.h"
#include "qtembedplugin/pluginmanager.h"
#include <QtCore/QTextCodecPlugin>
#include <boost/assign/list_of.hpp>
#include <boost/foreach.hpp>
#include <vector>
#include <unordered_map>

//#define DEBUG "embedplugin::codecmanager"
//#include "sakurakit/skdebug.h"
//#include <QDebug>

using namespace boost::assign;

// Helper functions
namespace { // unnamed

// Return if two code names are equal. Normalize to lowercase and replace '_' by '-'.
inline char _normalize_codec_char(char ch)
{
  if (ch == '_')
    ch = '-';
  else if ('A' <= ch && ch <= 'Z')
    ch += 'a' - 'A';
  return ch;
}

inline bool eqcodec(const char *x, const char *y)
{
  if (x == y)
    return true;
  if (!x || !y)
    return false;
  for (;; x++, y++) {
    if (_normalize_codec_char(*x) != _normalize_codec_char(*y))
      return false;
    if (*x == 0)
      return true;
  }
}
} // unnamed namespace

QTEMBEDPLUGIN_BEGIN_NAMESPACE

/** Private class */

class CodecManagerPrivate
{
  enum CodecPlugin {
    JP = 0, KO, CN, TW,
    CodecPluginCount
  };
public:
  typedef std::vector<const char *> CodecNameList;
  static CodecNameList pluginNames[];
  static const char *pluginFiles[];

  PluginManager *plugin;
  std::unordered_map<const char *, QTextCodec *> codecs;

  QTextCodec *createForName(const char *name)
  {
    if (plugin)
      for (int pluginIndex = 0; pluginIndex < CodecPluginCount; pluginIndex++)
        BOOST_FOREACH (const char *key, pluginNames[pluginIndex])
          if (eqcodec(name, key)) // case-insensitive
            if (QObject *p = plugin->loadPlugin(pluginFiles[pluginIndex]))
              return static_cast<QTextCodecPlugin *>(p)->createForName(key);
    return nullptr;
  }
};

const char *CodecManagerPrivate::pluginFiles[] = {
  "plugins/codecs/qjpcodecs4.dll", // JP
  "plugins/codecs/qkrcodecs4.dll", // KR
  "plugins/codecs/qcncodecs4.dll", // CN
  "plugins/codecs/qtwcodecs4.dll", // TW
};

CodecManagerPrivate::CodecNameList CodecManagerPrivate::pluginNames[] = {
  list_of("EUC-JP")("ISO-2022-JP")("Shift_JIS"), // JP
  list_of("EUC-KR")("cp949"), // KO
  list_of("GB18030")("GBK")("GB2312"), // CN
  list_of("Big5")("Big5-HKSCS"), // TW
};

/** Public class */

// - Construction -

CodecManager::CodecManager(PluginManager *plugin)
  : d_(new D)
{
  d_->plugin = plugin ? plugin : PluginManager::globalInstance();
}

CodecManager::~CodecManager() { delete d_; }

CodecManager *CodecManager::globalInstance()
{
  static Self g;
  return &g;
}

QTextCodec *CodecManager::codecForName(const char *name)
{
  auto it = d_->codecs.find(name);
  if (it != d_->codecs.end())
    return it->second;
  return (
    d_->codecs[name] = d_->createForName(name)
  );
}

QTEMBEDPLUGIN_END_NAMESPACE

// EOF

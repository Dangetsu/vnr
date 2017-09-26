// i18n.cc
// 6/29/2015 jichi
#include "util/i18n.h"
#include <QtCore/QString>

bool Util::languageNeedsWordWrap(const QString &lang)
{ return lang != "ja" && !lang.startsWith("zh"); }

// EOF

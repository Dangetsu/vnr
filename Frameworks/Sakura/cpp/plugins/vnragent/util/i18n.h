#pragma once

// i18n.h
// 6/29/2015 jichi

#include <QtCore/QtGlobal>

QT_FORWARD_DECLARE_CLASS(QString)

namespace Util {

bool languageNeedsWordWrap(const QString &lang);

} // namespace Util

// EOF

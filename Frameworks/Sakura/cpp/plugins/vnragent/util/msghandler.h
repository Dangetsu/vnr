#pragma once

// msghandler.h
// 4/27/2014 jichi

#include <QtCore/QString>

namespace Util {

QString debugFileLocation();
void debugMsgHandler(QtMsgType type, const char *msg);
void installDebugMsgHandler();
void uninstallDebugMsgHandler();

} // namespace Util

// EOF

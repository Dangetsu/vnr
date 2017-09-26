#pragma once

// location.h
// 5/3/2014 jichi

#include <QtCore/QString>

// Be careful that the functions here are not thread-safe on the startup
namespace Util {

// Location of ~/Desktop
QString desktopLocation();

// Directory of QtCore4.dll
QString qtLocation();

// Parent directory of QtCore4.dll
QString qtPrefix();

// VNR root directory
QString vnrLocation();

} // namespace Util

// EOF

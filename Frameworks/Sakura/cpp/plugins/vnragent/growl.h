#pragma once

// growl.h
// 2/1/2013 jichi

class QString;

namespace growl {

void msg(const QString &msg);
void warn(const QString &msg);
void error(const QString &msg);
void notify(const QString &msg);

} // namespace growl

// EOF

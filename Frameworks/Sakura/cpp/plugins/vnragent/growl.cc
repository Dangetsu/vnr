// growl.h
// 2/1/2013 jichi

#include "growl.h"
#include "driver/rpcclient.h"

void growl::msg(const QString &msg) { if (auto p = RpcClient::instance()) p->growlMessage(msg); }
void growl::warn(const QString &msg) { if (auto p = RpcClient::instance()) p->growlWarning(msg); }
void growl::error(const QString &msg) { if (auto p = RpcClient::instance()) p->growlError(msg); }
void growl::notify(const QString &msg) { if (auto p = RpcClient::instance()) p->growlNotification(msg); }

// EOF

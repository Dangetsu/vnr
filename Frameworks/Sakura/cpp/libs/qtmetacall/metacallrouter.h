#ifndef METACALLROUTER_H
#define METACALLROUTER_H

// metacallrouter.h
// 2/1/2013 jichi

#include "qtmetacall/qtmetacall.h"

QTMETACALL_BEGIN_NAMESPACE

// Interface
class MetaCallRouter
{
public:
  virtual ~MetaCallRouter() {}

  virtual int convertReceiveMethodId(int value) { return value; }
  virtual int convertSendMethodId(int value) { return value; }
};

QTMETACALL_END_NAMESPACE

#endif // METACALLROUTER_H

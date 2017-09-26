#pragma once

// dyncodec.h
// 6/3/2015 jichi

#include "sakurakit/skglobal.h"
#include <QtCore/QString>

class DynamicCodecPrivate;
class DynamicCodec
{
  SK_CLASS(DynamicCodec)
  SK_DECLARE_PRIVATE(DynamicCodecPrivate)
  SK_DISABLE_COPY(DynamicCodec)
public:
  static Self *instance();
  DynamicCodec();
  ~DynamicCodec();

  void setMinimumByte(int v);

  QByteArray encode(const QString &text, bool *dynamic = nullptr) const;
  QString decode(const QByteArray &data, bool *dynamic = nullptr) const;
  uint decodeChar(uint ch, bool *dynamic = nullptr) const;
};

// EOF

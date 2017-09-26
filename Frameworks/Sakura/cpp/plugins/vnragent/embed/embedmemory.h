#pragma once

// embedmemory.h
// 5/8/2014 jichi
// Shared memory reader.

#include "vnrsharedmemory/vnrsharedmemory.h"

class EmbedMemory : public VnrSharedMemory
{
  Q_OBJECT
  Q_DISABLE_COPY(EmbedMemory)
  SK_EXTEND_CLASS(EmbedMemory, VnrSharedMemory)
public:
  explicit EmbedMemory(QObject *parent = nullptr);
  ~EmbedMemory();

  bool create();

  enum DataStatus {
    EmptyStatus = 0 // There is no data
    , ReadyStatus   // The data is ready to read
    , BusyStatus    // The producer is busy writing the data
    , CancelStatus  // The data requires is cancelled
  };

  bool isDataEmpty(int i) const { return dataStatus(i) == EmptyStatus; }
  bool isDataReady(int i) const { return dataStatus(i) == ReadyStatus; }
  bool isDataBusy(int i) const { return dataStatus(i) == BusyStatus; }
  bool isDataCanceled(int i) const { return dataStatus(i) == CancelStatus; }
};

// EOF

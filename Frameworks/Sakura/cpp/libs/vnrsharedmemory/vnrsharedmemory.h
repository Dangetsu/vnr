#ifndef VNRSHAREDMEMORY_H
#define VNRSHAREDMEMORY_H

// contour.h
// 4/5/2014 jichi

#include "sakurakit/skglobal.h"
#include <QtCore/QObject>

class VnrSharedMemoryPrivate;
class VnrSharedMemory : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(VnrSharedMemory)
  SK_EXTEND_CLASS(VnrSharedMemory, QObject)
  SK_DECLARE_PRIVATE(VnrSharedMemoryPrivate)
public:
  explicit VnrSharedMemory(const QString &key, QObject *parent = nullptr);
  explicit VnrSharedMemory(QObject *parent = nullptr);
  ~VnrSharedMemory();

  // Attach

  QString key() const;
  void setKey(const QString &v);

  int cellCount() const; // total number of cells
  int cellSize() const; // size for each cell

  ///  The initial size must be larger than 20.
  bool create(int cellSize, int cellCount = 1, bool readOnly = false);
  bool attach(bool readOnly = false);
  bool isAttached() const;

  bool detach();
  bool detach_() { return detach(); } // escape keyword for Shiboken

  bool lock();
  bool unlock();

  bool hasError() const;
  QString errorString() const;

  // Contents

  const char *constData(int i) const; // for debuggong purpose only

  qint8 dataStatus(int i) const;
  void setDataStatus(int i, qint8 v);

  qint64 dataHash(int i) const;
  void setDataHash(int i, qint64 v);

  //qint32 dataSignature() const;
  //void setDataSignature(qint32 v);

  qint8 dataRole(int i) const;
  void setDataRole(int i, qint8 v);

  QString dataLanguage(int i) const;
  void setDataLanguage(int i, const QString &v);

  QString dataText(int i) const;
  void setDataText(int i, const QString &v);
  int dataTextCapacity() const; // number of characters allowed in text
};

#endif // VNRSHAREDMEMORY_H

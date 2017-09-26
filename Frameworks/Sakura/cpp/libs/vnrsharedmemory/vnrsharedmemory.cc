// vnrsharedmemory.cc
// 5/7/2014 jichi
#include "vnrsharedmemory/vnrsharedmemory.h"
#include <QtCore/QSharedMemory>

/** Private class */

class VnrSharedMemoryPrivate
{
public:
  enum { LanguageCapacity = 4 };

  struct Cell {
    qint8 status;
    qint64 hash;
    //qint32 signature;
    qint8 role;
    char language[LanguageCapacity];
    qint32 textSize;
    wchar_t text[1];
  private:
    Cell() {} // disable constructor
  };

  int cellCount;
  int cellSize; // cell size, instead of total size

  QSharedMemory *memory;

  explicit VnrSharedMemoryPrivate(QObject *parent)
    : cellCount(0), cellSize(0), memory(new QSharedMemory(parent)) {}
  VnrSharedMemoryPrivate(const QString &key, QObject *parent)
    : memory(new QSharedMemory(key, parent)) {}

  int textCapacity() const { return qMax<int>(0, (cellSize - sizeof(Cell)) / 2); }

  quint8 *data(int i) { return static_cast<quint8 *>(memory->data()) + cellSize * i; }
  const quint8 *constData(int i) const { return static_cast<const quint8 *>(memory->constData()) + cellSize * i; }

  Cell *cell(int i) { return reinterpret_cast<Cell *>(data(i)); }
  const Cell *constCell(int i) const { return reinterpret_cast<const Cell *>(constData(i)); }
};

/** Public class */

VnrSharedMemory::VnrSharedMemory(QObject *parent)
  : Base(parent), d_(new D(this)) {}

VnrSharedMemory::VnrSharedMemory(const QString &key, QObject *parent)
  : Base(parent), d_(new D(key, this)) {}

VnrSharedMemory::~VnrSharedMemory() { delete d_; }

// Shared Memory
QString VnrSharedMemory::key() const { return d_->memory->key(); }
void VnrSharedMemory::setKey(const QString &v) { d_->memory->setKey(v); }

int VnrSharedMemory::cellCount() const { return d_->cellCount; }
int VnrSharedMemory::cellSize() const { return d_->cellSize; }

bool VnrSharedMemory::create(int size, int count, bool readOnly)
{
  d_->cellSize = size;
  d_->cellCount = count;
  return d_->memory->create(size * count, readOnly ? QSharedMemory::ReadOnly : QSharedMemory::ReadWrite);
}

bool VnrSharedMemory::attach(bool readOnly)
{ return d_->memory->attach(readOnly ? QSharedMemory::ReadOnly : QSharedMemory::ReadWrite); }

bool VnrSharedMemory::detach() { return d_->memory->detach(); }
bool VnrSharedMemory::isAttached() const { return d_->memory->isAttached(); }

bool VnrSharedMemory::lock() { return d_->memory->lock(); }
bool VnrSharedMemory::unlock() { return d_->memory->unlock(); }

QString VnrSharedMemory::errorString() const { return d_->memory->errorString(); }
bool VnrSharedMemory::hasError() const { return d_->memory->error() != QSharedMemory::NoError; }

int VnrSharedMemory::dataTextCapacity() const
{ return d_->textCapacity(); }

// Contents

const char *VnrSharedMemory::constData(int i) const
{ return reinterpret_cast<const char *>(d_->constData(i)); }

qint64 VnrSharedMemory::dataHash(int i) const
{
  if (auto p = d_->constCell(i))
    return p->hash;
  else
    return 0;
}

void VnrSharedMemory::setDataHash(int i, qint64 v)
{
  if (auto p = d_->cell(i))
    p->hash = v;
}

qint8 VnrSharedMemory::dataStatus(int i) const
{
  if (auto p = d_->constCell(i))
    return p->status;
  else
    return 0;
}

void VnrSharedMemory::setDataStatus(int i, qint8 v)
{
  if (auto p = d_->cell(i))
    p->status = v;
}

//qint32 VnrSharedMemory::dataSignature(int i) const
//{
//  if (auto p = d_->constCell(i))
//    return p->signature;
//  else
//    return 0;
//}
//
//void VnrSharedMemory::setDataSignature(qint32 v)
//{
//  if (auto p = d_->cell(i))
//    p->signature = v;
//}

qint8 VnrSharedMemory::dataRole(int i) const
{
  if (auto p = d_->constCell(i))
    return p->role;
  else
    return 0;
}

void VnrSharedMemory::setDataRole(int i, qint8 v)
{
  if (auto p = d_->cell(i))
    p->role = v;
}

QString VnrSharedMemory::dataLanguage(int i) const
{
  if (auto p = d_->constCell(i))
    return QString::fromAscii(p->language);
  else
    return QString();
}

void VnrSharedMemory::setDataLanguage(int i, const QString &v)
{
  if (auto p = d_->cell(i)) {
    if (v.isEmpty())
      p->language[0] = 0;
    else if (v.size() < D::LanguageCapacity) {
      auto data = v.toAscii();
      for (int i = v.size() - 1; i >= 0; i--) // iterate in reverse order
        p->language[i] = data[i];
    } else {// truncate string
      auto data = v.toAscii();
      p->language[D::LanguageCapacity - 1] = 0;
      for (int i = D::LanguageCapacity - 2; i >= 0; i--) // iterate in reverse order
        p->language[i] = data[i];
    }
  }
}

QString VnrSharedMemory::dataText(int i) const
{
  if (auto p = d_->constCell(i))
    if (p->textSize > 0 && p->textSize <= d_->textCapacity())
      return QString::fromWCharArray(p->text, p->textSize);
  return QString();
}

void VnrSharedMemory::setDataText(int i, const QString &v)
{
  if (auto p = d_->cell(i)) {
    int limit = d_->textCapacity();
    if (v.size() <= limit) {
      p->textSize = v.size();
      v.toWCharArray(p->text);
    } else {
      QString w = v.left(limit);
      p->textSize = w.size();
      w.toWCharArray(p->text);
    }
  }
}

// EOF

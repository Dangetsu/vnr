// embedmanager.cc
// 4/26/2014 jichi

#include "config.h"
#include "embed/embedmemory.h"
#include <QtCore/QCoreApplication>

#define DEBUG "embedmemory"
#include "sakurakit/skdebug.h"

// Helpers

static inline QString shmem_key()
{
  qint64 pid = QCoreApplication::applicationPid();
  return QString(VNRAGENT_MEMORY_KEY).arg(QString::number(pid));
}

// Construction

EmbedMemory::EmbedMemory(QObject *parent) : Base(::shmem_key(), parent) {}
EmbedMemory::~EmbedMemory() {}

// Management

bool EmbedMemory::create()
{
  enum { ReadOnly = 1 };
  bool ok = Base::create(VNRAGENT_MEMORY_SIZE, VNRAGENT_MEMORY_COUNT, ReadOnly);
  DOUT("ret =" << ok);
  return ok;
}

// EOF

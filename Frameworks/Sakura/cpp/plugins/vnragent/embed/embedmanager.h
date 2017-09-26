#pragma once

// embedmanager.h
// 4/26/2014 jichi
// Embedded game engine text manager.

#include "sakurakit/skglobal.h"
#include <QtCore/QList>
#include <QtCore/QObject>

class EmbedManagerPrivate;
class EmbedManager : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(EmbedManager)
  SK_EXTEND_CLASS(EmbedManager, QObject)
  SK_DECLARE_PRIVATE(EmbedManagerPrivate)

public:
  static Self *instance(); // needed by Engine

  explicit EmbedManager(QObject *parent = nullptr);
  ~EmbedManager();

  // Interface to RPC
signals:
  void textReceived(QString text, qint64 hash, long signature, int role, bool needsTranslation);
public: // synchronized methods
  //void updateTranslation(const QString &text, qint64 hash, int role);
  void clearTranslation();
  void quit();

  // Interface to engine
public: // unsynchronized methods
  QString findTranslation(qint64 hash, int role, QString *language = nullptr) const;

  void setTranslationWaitTime(int msecs);
  QString waitForTranslation(qint64 hash, int role, QString *language = nullptr) const;

  void sendText(const QString &text, qint64 hash, long signature, int role, bool needsTranslation);

  // Expose the internal mutex
  //bool tryLock();
  //void lock();
  //void unlock();
};

// Helper mutex locker class
//class EmbedManagerLock
//{
//  EmbedManager *mutex_;
//public:
//  explicit EmbedManagerLock(EmbedManager *m) : mutex_(m) { mutex_->lock(); }
//  ~EmbedManagerLock() { mutex_->unlock(); }
//};

// EOF

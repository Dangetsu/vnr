// maindriver_p.h
// 2/1/2013 jichi
#include "sakurakit/skglobal.h"
#include <QtCore/QObject>

class AbstractEngine;
class EmbedDriver;
class HijackDriver;
class RpcClient;
class Settings;
class WindowDriver;
class MainDriverPrivate : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(MainDriverPrivate)
  SK_EXTEND_CLASS(MainDriverPrivate, QObject)

  Settings *settings;
  RpcClient *rpc;
  HijackDriver *hijack;
  EmbedDriver *eng;
  WindowDriver *win;
public:
  explicit MainDriverPrivate(QObject *parent);
  void quit();

signals:
  void deleteLaterRequestd();

private slots:
  void onDisconnected();
  void unload();

  void onLoadFinished();

private:
  void createHijackDriver();
  void createEmbedDriver();
  void createWindowDriver();
};

// EOF

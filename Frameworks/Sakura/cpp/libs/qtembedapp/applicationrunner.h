#ifndef _QTEMBEDAPP_APPLICATIONRUNNER_H
#define _QTEMBEDAPP_APPLICATIONRUNNER_H

// applicationrunner.h
// 2/1/2013 jichi

#include "qtembedapp/qtembedapp.h"
#include "sakurakit/skglobal.h"
#include <QtCore/QString>
#include <QtGui/qwindowdefs.h>

QT_FORWARD_DECLARE_CLASS(QCoreApplication)

QTEMBEDAPP_BEGIN_NAMESPACE

class ApplicationRunnerPrivate;
class ApplicationRunner
{
  SK_CLASS(ApplicationRunner)
  SK_DISABLE_COPY(ApplicationRunner)
  SK_DECLARE_PRIVATE(ApplicationRunnerPrivate)

public:
  // Default event loop timer interval in ms
  enum { DefaultEventLoopInterval = 10 };

  //static QCoreApplication *createApplication(HINSTANCE hInstance = nullptr);

  /**
   *  App will be automatically deleted after destruction.
   *  @param  app
   *  @param  interval  msecs to refresh the event loops
   */
  explicit ApplicationRunner(QCoreApplication *app = nullptr, int interval = DefaultEventLoopInterval);
  ~ApplicationRunner();

  QCoreApplication *application() const;
  void setApplication(QCoreApplication *app);

  int interval() const; // event loop interval
  void setInterval(int msec);

  bool isActive() const; // is running
  void start(); // stop the timer
  void stop(); // stop the timer
};

QTEMBEDAPP_END_NAMESPACE

#endif // _QTEMBEDAPP_APPLICATIONRUNNER_H

// EOF

  //**
  // *  Create an instance in the memory.
  // *  @param  interval  msecs to refresh the event loops
  // */
  //static Self *createInstance(int interval = DefaultEventLoopInterval);

  //  Stop the event loop and delete the instance.
  //static void destroyInstance(Self *inst);

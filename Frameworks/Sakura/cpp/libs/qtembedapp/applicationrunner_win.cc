// applicationrunner_win.cc
// 2/1/2013 jichi
//
// Motivations:
// http://stackoverflow.com/questions/2150488/using-a-qt-based-dll-in-a-non-qt-application
// http://stackoverflow.com/questions/1786438/qt-library-event-loop-problems
#include "qtembedapp/applicationrunner.h"
#ifdef WITH_LIB_WINTIMER
# include "wintimer/wintimer.h"
#else
# error "missing wintimer lib"
#endif // WITH_LIB_WINTIMER
#include <QtCore/QCoreApplication>

//#define DEBUG "ApplicationRunner"
#include "sakurakit/skdebug.h"

QTEMBEDAPP_BEGIN_NAMESPACE

/** Private class */

class ApplicationRunnerPrivate
{
  SK_CLASS(ApplicationRunnerPrivate)
public:
  QCoreApplication *app;
  WinTimer timer;

  ApplicationRunnerPrivate() : app(nullptr)
  {
    timer.setSingleShot(false); // repeat
    timer.setMethod(this, &Self::processEvents);
  }

  void processEvents() { if (app) app->processEvents(QEventLoop::AllEvents, timer.interval()); }
};

/** Public class */

// - Construction -

ApplicationRunner::ApplicationRunner(QCoreApplication *app, int interval)
  : d_(new D)
{
  d_->app = app;
  d_->timer.setInterval(interval);
}

ApplicationRunner::~ApplicationRunner()
{
  if (d_->timer.isActive())
    d_->timer.stop();
  delete d_;
}

QCoreApplication *ApplicationRunner::application() const { return d_->app; }
void ApplicationRunner::setApplication(QCoreApplication *value) { d_->app = value; }

bool ApplicationRunner::isActive() const { return d_->timer.isActive(); }
void ApplicationRunner::start() { d_->timer.start(); }
void ApplicationRunner::stop() { d_->timer.stop(); }

int ApplicationRunner::interval() const { return d_->timer.interval(); }
void ApplicationRunner::setInterval(int value) { d_->timer.setInterval(value); }

QTEMBEDAPP_END_NAMESPACE

// EOF

//QCoreApplication *ApplicationRunner::createApplication(HINSTANCE hInstance)
//{
//  static char arg0[MAX_PATH * 2]; // in case it is wchar
//
//  static char *argv[] = { arg0, nullptr };
//  static int argc = 1;
//
// ::GetModuleFileNameA(hInstance, arg0, sizeof(arg0)/sizeof(*arg0));
//  return new QCoreApplication(argc, argv);
//}

//void ApplicationRunner::processEvents() { d_->processEvents(); }

//ApplicationRunner *ApplicationRunner::createInstance(int interval)
//{
//  QCoreApplication *app = QCoreApplication::instance();
//  if (!app)
//    app = createApplication();
//  return new Self(app, interval);
//}

//void ApplicationRunner::destroyInstance(Self *inst)
//{
//  Q_ASSERT(inst);
//  if (inst) {
//    inst->quit();
//    delete inst;
//  }
//}

// loader.cc
// 1/27/2013

#include "config.h"
#include "loader.h"
#include "driver/maindriver.h"
#include "windbg/inject.h"
#include "windbg/util.h"
#include "hijack/hijackmodule.h"
#include "qtembedplugin/pluginmanager.h"
#include "util/location.h"
#include <QtCore/QCoreApplication>
#include <QtCore/QTextCodec>

#ifdef VNRAGENT_ENABLE_APPRUNNER
#include "qtembedapp/applicationrunner.h"
#endif // VNRAGENT_ENABLE_APPRUNNER

#ifdef VNRAGENT_DEBUG
# include "util/msghandler.h"
#endif // VNRAGENT_DEBUG

#define DEBUG "loader"
#include "sakurakit/skdebug.h"

// Global variables

namespace { // unnamed

QCoreApplication *createApplication_(HINSTANCE hInstance)
{
  static char arg0[MAX_PATH * 2]; // in case it is wchar
  static char *argv[] = { arg0, nullptr };
  static int argc = 1;
  ::GetModuleFileNameA(hInstance, arg0, sizeof(arg0)/sizeof(*arg0));
  return new QCoreApplication(argc, argv);
}

// Persistent data
MainDriver *driver_;

#ifdef VNRAGENT_ENABLE_APPRUNNER
QtEmbedApp::ApplicationRunner *appRunner_;
#endif // VNRAGENT_ENABLE_APPRUNNER

} // unnamed namespace

// Loader

void Loader::initWithInstance(HINSTANCE hInstance)
{
  //::GetModuleFileNameW(hInstance, MODULE_PATH, MAX_PATH);
  QTextCodec *codec = QTextCodec::codecForName("UTF-8");
  QTextCodec::setCodecForCStrings(codec);
  QTextCodec::setCodecForTr(codec);

  //::localizePluginManager();
  QtEmbedPlugin::PluginManager::globalInstance()->setPrefix(Util::qtPrefix());

  ::createApplication_(hInstance);

#ifdef VNRAGENT_DEBUG
  Util::installDebugMsgHandler();
#endif // VNRAGENT_DEBUG

  DOUT(QCoreApplication::applicationFilePath());

  ::driver_ = new MainDriver;

  // Hijack UI threads
  {
    WinDbg::ThreadsSuspender suspendedThreads; // lock all threads
    Hijack::overrideModules();
  }

#ifdef VNRAGENT_ENABLE_APPRUNNER
  ::appRunner_ = new QtEmbedApp::ApplicationRunner(qApp, QT_EVENTLOOP_INTERVAL);
  ::appRunner_->start();
#else
  qApp->exec(); // block here
#endif // VNRAGENT_ENABLE_APPRUNNER
}

void Loader::destroy()
{
  if (::driver_) {
    ::driver_->quit();
#ifdef VNRAGENT_ENABLE_UNLOAD
    ::driver_->requestDeleteLater();
    ::driver_ = nullptr;
#endif // VNRAGENT_ENABLE_UNLOAD
  }

#ifdef VNRAGENT_ENABLE_APPRUNNER
  if (::appRunner_ && ::appRunner_->isActive()) {
    ::appRunner_->stop(); // this class is not deleted
#ifdef VNRAGENT_ENABLE_UNLOAD
    delete ::appRunner_;
    ::appRunner_ = nullptr;
#endif // VNRAGENT_ENABLE_UNLOAD
  }
#endif // VNRAGENT_ENABLE_APPRUNNER

  if (qApp) {
    qApp->quit();
    qApp->processEvents(); // might hang here
#ifdef VNRAGENT_ENABLE_UNLOAD
    delete qApp;
#endif // VNRAGENT_ENABLE_UNLOAD
  }
}

// EOF

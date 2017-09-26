// main.cc
// 10/27/2014 jichi

#include "main.h"

int main(int argc, char *argv[])
{
  QApplication a(argc, argv);
  Recorder w;
  w.show();
  w.startRecordingVideo();
  QObject::connect(&a, SIGNAL(aboutToQuit()), &w, SLOT(stop()));
  return a.exec();
}

// EOF

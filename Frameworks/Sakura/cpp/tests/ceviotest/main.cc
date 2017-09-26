// main.cc
// 6/15/2014 jichi
// See: http://guide2.project-cevio.com/interface/com
#include "ceviotts/ceviotts.h"
#include <qt_windows.h>
#include <QDebug>

int main()
{
  CoInitialize(nullptr);

  cevioservice_t *service = cevioservice_create();
  Q_ASSERT(service);
  qDebug() << service;

  ceviotts_t *tts = ceviotts_create();
  Q_ASSERT(tts);
  qDebug() << tts;

  const char *text = "hello";
  //const wchar_t *text = L"hello";
  //const wchar_t *text = L"\u3055";

  ceviotts_speak(tts, text);

  ceviotts_destroy(tts);

  cevioservice_destroy(service);

  CoUninitialize();
  return 0;
}

// EOF

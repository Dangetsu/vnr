// main.cc
// 6/15/2014 jichi
#include "wintts/wintts.h"
#include <qt_windows.h>
#include <QtCore/QString>

int main()
{
  const wchar_t *text = L"hello";
  //const wchar_t *text = L"\u3055";
  //const wchar_t *text = L"\u3055\u3068\u3046\u3055\u3055\u3089";

  //QString q = "hello";
  //QString q = "\u3055\u3068\u3046\u3055\u3055\u3089";
  //QString q = "\x82\xa0";
  //QString q = "\xa4\xa2";
  //const wchar_t *text = (LPCWSTR)q.utf16();

  const wchar_t *voice = L"HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Speech\\Voices\\Tokens\\VW Misaki";
  //const wchar_t *voice = L"HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Speech\\Voices\\Tokens\\CeVIO-\u3055\u3068\u3046\u3055\u3055\u3089";

  //CoInitialize(nullptr);
  //OleInitialize(nullptr);
  CoInitializeEx(nullptr, COINIT_MULTITHREADED);

  wintts_t *tts = wintts_create();
  Q_ASSERT(tts);
  wintts_set_voice(tts, voice);
  wintts_speak(tts, text);
  wintts_destroy(tts);

  //CoUninitialize();
  OleUninitialize();
  return 0;
}

// EOF

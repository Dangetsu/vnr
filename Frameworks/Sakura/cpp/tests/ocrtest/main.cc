// main.cc
// 8/11/2014 jichi
#include "modiocr/modiocr.h"
#include <qt_windows.h>
#include <QtCore/QDebug>
#include <QtCore/QString>

int main()
{
  //std::cerr << "iostream:enter" << std::endl;
  qDebug() << "enter";

  //const wchar_t *path = L"z:\\Users\\jichi\\Desktop\\wiki.tiff";
  //const wchar_t *path = L"en.tiff";
  const wchar_t *path = L"wiki.png";

  //modiocr_flags langs = modiocr_lang_ja|modiocr_lang_zhs|modiocr_lang_zht|modiocr_lang_en;
  //modiocr_flags langs = modiocr_lang_en;
  modiocr_flags langs = modiocr_lang_ko;

  CoInitialize(nullptr);
  if (modiocr_available()) {
    modiocr_lang lang = modiocr_readfile(path, langs, [](const wchar_t *text) {
      qDebug() << QString::fromWCharArray(text);
    });

    qDebug() << (int)lang;
  }

  CoUninitialize();
  //std::cerr << "iostream:leave" << std::endl;
  qDebug() << "leave";
  return 0;
}

// EOF

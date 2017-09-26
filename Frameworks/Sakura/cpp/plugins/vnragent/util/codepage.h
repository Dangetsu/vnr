#pragma once

// codepage.h
// 5/6/2014 jichi

#include <QtCore/QtGlobal>

QT_FORWARD_DECLARE_CLASS(QChar)
QT_FORWARD_DECLARE_CLASS(QString)
QT_FORWARD_DECLARE_CLASS(QTextCodec)

#define ENC_UTF8    "utf-8"
#define ENC_UTF16   "utf-16"
#define ENC_SJIS    "shift-jis" // Japanese
#define ENC_GBK     "gbk"       // Simplified Chinese
#define ENC_BIG5    "big5"      // Traditional Chinese
#define ENC_KSC     "cp949"     // Korean, not the same as euc-kr
#define ENC_TIS     "tis-620"   // Thai
#define ENC_KOI8    "koi8-r"    // Cyrillic, Windows-1251

namespace Util {

// See: http://msdn.microsoft.com/en-us/library/dd317756%28VS.85%29.aspx
enum CodePage {
  NullCodePage = 0
  , Utf8CodePage = 65001 // UTF-8
  , Utf16CodePage = 1200 // UTF-16
  , SjisCodePage = 932  // SHIFT-JIS
  , GbkCodePage = 936   // GB2312
  , KscCodePage = 949   // EUC-KR
  , Big5CodePage = 950  // BIG5
  , TisCodePage = 874   // TIS-620
  , Koi8CodePage = 866  // KOI8-R
};

uint codePageForEncoding(const QString &encoding);
const char *encodingForCodePage(uint cp);

quint8 charSetForCodePage(uint cp);

QTextCodec *codecForName(const char *name);

bool charEncodable(const QChar &ch, const QTextCodec *codec);
bool textDecodable(const char *text, const QTextCodec *codec);

uint codePageFromRegistry();

} // namespace Util

// EOF

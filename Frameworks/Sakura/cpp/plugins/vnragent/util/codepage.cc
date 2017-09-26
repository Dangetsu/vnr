// codepage.cc
// 5/6/2014 jichi
#include "util/codepage.h"
#include "qtembedplugin/codecmanager.h"
#include <QtCore/QString>
#include <QtCore/QSettings>
#include <QtCore/QTextCodec>
#include <qt_windows.h>
// Get real ACP from registry
uint Util::codePageFromRegistry()
{
  static uint ret;
  if (!ret)
    ret =
      QSettings("HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Nls\\CodePage", QSettings::NativeFormat)
      .value("ACP")
      .toUInt()
    ;
    // For registry API, see: http://stackoverflow.com/questions/34065/how-to-read-a-value-from-the-windows-registry
    //HKEY hk;
    //if (0 == ::RegOpenKeyExA(HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Control\\Nls\\CodePage", 0, KEY_READ, &hk)) {
    //  DWORD size = sizeof(ret);
    //  auto err = ::RegQueryValueExA(hk , "ACP" , 0 , nullptr , reinterpret_cast<LPBYTE>(&ret) , &size); //== 0
    //  qDebug() << "9999:"<<err << ":" << ret << ":" << size;
    //}
  return ret;
}

bool Util::charEncodable(const QChar &ch, const QTextCodec *codec)
{
  if (!codec)
    return false;
  if (ch.unicode() <= 127) // ignore ascii characters
    return true;
  QByteArray data = codec->fromUnicode(&ch, 1);
  // Encodable if data is not '\0' and not '?'
  return data.size() != 1 || (data[0] && data[0] != '?');
}

bool Util::textDecodable(const char *text, const QTextCodec *codec)
{
  if (!codec)
    return false;
  QString qs = codec->toUnicode(text);
  return !qs.contains(L'\ufffd');
}

//bool Util::charDecodable(const QByteArray &c) const
//{
//  if (!decoder || c.isEmpty())
//    return false;
//  if (c == "?")
//    return true;
//  return encoder->toUnicode(c) != "?";
//}

QTextCodec *Util::codecForName(const char *name)
{
  if (!name)
    return nullptr;
  QTextCodec *ret = QTextCodec::codecForName(name);
  return ret ? ret : QtEmbedPlugin::CodecManager::globalInstance()->codecForName(name);
}

uint Util::codePageForEncoding(const QString &encoding)
{
  QString t = encoding.toLower();
  if (t == ENC_SJIS)
    return SjisCodePage;
  if (t == ENC_GBK)
    return GbkCodePage;
  if (t == ENC_BIG5)
    return Big5CodePage;
  if (t == ENC_KSC)
    return KscCodePage;
  if (t == ENC_TIS)
    return TisCodePage;
  if (t == ENC_UTF8)
    return Utf8CodePage;
  if (t == ENC_UTF16)
    return Utf16CodePage;
  return NullCodePage;
}

const char *Util::encodingForCodePage(uint cp)
{
  switch (cp) {
  case SjisCodePage: return ENC_SJIS;
  case GbkCodePage: return ENC_GBK;
  case Big5CodePage: return ENC_BIG5;
  case KscCodePage: return ENC_KSC;
  case Koi8CodePage: return ENC_KOI8;
  case Utf8CodePage: return ENC_UTF8;
  case Utf16CodePage: return ENC_UTF16;
  default: return nullptr;
  }
}

// https://msdn.microsoft.com/en-us/library/cc250412.aspx
// typedef enum // BYTE
// {
//   ANSI_CHARSET = 0x00000000,
//   DEFAULT_CHARSET = 0x00000001,
//   SYMBOL_CHARSET = 0x00000002,
//   MAC_CHARSET = 0x0000004D,
//   SHIFTJIS_CHARSET = 0x00000080,
//   HANGUL_CHARSET = 0x00000081,
//   JOHAB_CHARSET = 0x00000082,
//   GB2312_CHARSET = 0x00000086,
//   CHINESEBIG5_CHARSET = 0x00000088,
//   GREEK_CHARSET = 0x000000A1,
//   TURKISH_CHARSET = 0x000000A2,
//   VIETNAMESE_CHARSET = 0x000000A3,
//   HEBREW_CHARSET = 0x000000B1,
//   ARABIC_CHARSET = 0x000000B2,
//   BALTIC_CHARSET = 0x000000BA,
//   RUSSIAN_CHARSET = 0x000000CC,
//   THAI_CHARSET = 0x000000DE,
//   EASTEUROPE_CHARSET = 0x000000EE,
//   OEM_CHARSET = 0x000000FF
// } CharacterSet;

quint8 Util::charSetForCodePage(uint cp)
{
  switch (cp) {
  case TisCodePage:     return THAI_CHARSET;
  case Koi8CodePage:    return RUSSIAN_CHARSET;
  case SjisCodePage:    return SHIFTJIS_CHARSET;
  case GbkCodePage:     return GB2312_CHARSET;
  case Big5CodePage:    return CHINESEBIG5_CHARSET;

  case KscCodePage:     return HANGUL_CHARSET;
  case 1361:            return JOHAB_CHARSET; // alternative Korean character set

  case 1250:            return EASTEUROPE_CHARSET;
  case 1251:            return RUSSIAN_CHARSET; // cyrillic
  case 1253:            return GREEK_CHARSET;
  case 1254:            return TURKISH_CHARSET;

  case 862:             return HEBREW_CHARSET; // obsolete
  case 1255:            return HEBREW_CHARSET;

  case 1256:            return ARABIC_CHARSET;
  case 1257:            return BALTIC_CHARSET;
  case 1258:            return VIETNAMESE_CHARSET;

  //default: return DEFAULT_CHARSET;
  default: return 0;
  }
}

// EOF

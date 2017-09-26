// hijackfuns.cc
// 6/3/2015 jichi
#include "hijack/hijackfuns.h"
#include "hijack/hijackhelper.h"
#include "hijack/hijacksettings.h"
#include "hijack/hijackmanager.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/enginecontroller.h"
#include "util/dyncodec.h"
#include "util/textutil.h"
#include "dyncodec/dynsjis.h"
#include <boost/foreach.hpp>
#include <algorithm>
#include <list>
#include <utility>

//#define DEBUG "hijackfuns"
#include "sakurakit/skdebug.h"

#pragma intrinsic(_ReturnAddress)

// Disable only for debugging purpose
//#define HIJACK_GDI_FONT
//#define HIJACK_GDI_TEXT

#define DEF_FUN(_f) Hijack::_f##_fun_t Hijack::old##_f = ::_f;
  DEF_FUN(CreateFontA)
  DEF_FUN(CreateFontW)
  DEF_FUN(CreateFontIndirectA)
  DEF_FUN(CreateFontIndirectW)
  DEF_FUN(GetGlyphOutlineA)
  DEF_FUN(GetGlyphOutlineW)
  DEF_FUN(GetTextExtentPoint32A)
  DEF_FUN(GetTextExtentPoint32W)
  DEF_FUN(GetTextExtentExPointA)
  DEF_FUN(GetTextExtentExPointW)
  DEF_FUN(GetCharABCWidthsA)
  DEF_FUN(GetCharABCWidthsW)
  DEF_FUN(TextOutA)
  DEF_FUN(TextOutW)
  DEF_FUN(ExtTextOutA)
  DEF_FUN(ExtTextOutW)
  DEF_FUN(TabbedTextOutA)
  DEF_FUN(TabbedTextOutW)
  DEF_FUN(DrawTextA)
  DEF_FUN(DrawTextW)
  DEF_FUN(DrawTextExA)
  DEF_FUN(DrawTextExW)
  DEF_FUN(CharNextA)
  //DEF_FUN(CharNextW)
  //DEF_FUN(CharNextExA)
  //DEF_FUN(CharNextExW)
  DEF_FUN(CharPrevA)
  //DEF_FUN(CharPrevW)
  DEF_FUN(MultiByteToWideChar)
  DEF_FUN(WideCharToMultiByte)
#undef DEF_FUN

/** Helper */

namespace { // unnamed

void customizeLogFontA(LOGFONTA *lplf)
{
  auto p = HijackHelper::instance();
  auto s = p->settings();
  if (s->fontCharSetEnabled) {
    auto charSet = s->fontCharSet;
    if (!charSet)
      charSet = p->systemCharSet();
    if (charSet)
      lplf->lfCharSet = charSet;
  }
  if (s->fontWeight)
    lplf->lfWeight = s->fontWeight;
  if (s->isFontScaled()) {
    lplf->lfWidth *= s->fontScale;
    lplf->lfHeight *= s->fontScale;
  }
}

void customizeLogFontW(LOGFONTW *lplf)
{
  customizeLogFontA((LOGFONTA *)lplf);

  auto p = HijackHelper::instance();
  auto s = p->settings();
  if (!s->fontFamily.isEmpty()) {
    lplf->lfFaceName[s->fontFamily.size()] = 0;
    s->fontFamily.toWCharArray(lplf->lfFaceName);
  }
}

// LogFont manager

class LogFontManager
{
  typedef std::pair<HFONT, LOGFONTW> font_pair;
  std::list<font_pair> fonts_;

  static bool eq(const LOGFONTW &x, const LOGFONTW&y);

public:
  HFONT get(const LOGFONTW &lf) const;
  void add(HFONT hf, const LOGFONTW &lf);
  void remove(HFONT hf);
  void remove(const LOGFONTW &lf);
};

bool LogFontManager::eq(const LOGFONTW &x, const LOGFONTW &y)
{ // I assume there is no padding
  return ::wcscmp(x.lfFaceName, y.lfFaceName) == 0
      && ::memcmp(&x, &y, sizeof(x) - sizeof(x.lfFaceName)) == 0;
}

void LogFontManager::add(HFONT hf, const LOGFONTW &lf)
{ fonts_.push_back(std::make_pair(hf, lf)); }

void LogFontManager::remove(HFONT hf)
{
  std::remove_if(fonts_.begin(), fonts_.end(), [&hf](const font_pair &it) {
    return it.first == hf;
  });
}

void LogFontManager::remove(const LOGFONTW &lf)
{
  std::remove_if(fonts_.begin(), fonts_.end(), [&lf](const font_pair &it) {
    return eq(it.second, lf);
  });
}

HFONT LogFontManager::get(const LOGFONTW &lf) const
{
  BOOST_FOREACH (const font_pair &it, fonts_)
    if (eq(it.second, lf))
      return it.first;
  return nullptr;
}

// GDI font switcher

class DCFontSwitcher
{
  static LogFontManager fonts_;

  HDC hdc_;
  HFONT oldFont_,
        newFont_;

public:
  explicit DCFontSwitcher(HDC hdc); // pass 0 to disable this class
  ~DCFontSwitcher();
};

LogFontManager DCFontSwitcher::fonts_;

DCFontSwitcher::~DCFontSwitcher()
{
  // No idea why selecting old font will crash Mogeko Castle
  //if (oldFont_ && oldFont_ != HGDI_ERROR)
  //  ::SelectObject(hdc_, oldFont_);

  // Never delete new font but cache them
  // This could result in bad font after game is reset and deleted my font
  //if (newFont_)
  //  ::DeleteObject(newFont_);
}

DCFontSwitcher::DCFontSwitcher(HDC hdc)
  : hdc_(hdc), oldFont_(nullptr), newFont_(nullptr)
{
  if (!hdc_)
    return;
  auto p = HijackHelper::instance();
  if (!p)
    return;
  auto s = p->settings();
  if (!s->deviceContextFontEnabled || !s->isFontCustomized())
    return;

  TEXTMETRICW tm;
  if (!::GetTextMetricsW(hdc, &tm))
    return;

  LOGFONTW lf = {};
  lf.lfHeight = tm.tmHeight;
  lf.lfWeight = tm.tmWeight;
  lf.lfItalic = tm.tmItalic;
  lf.lfUnderline = tm.tmUnderlined;
  lf.lfStrikeOut = tm.tmStruckOut;
  lf.lfCharSet = tm.tmCharSet;
  lf.lfPitchAndFamily = tm.tmPitchAndFamily;

  customizeLogFontW(&lf);

  if (s->fontFamily.isEmpty())
    ::GetTextFaceW(hdc_, LF_FACESIZE, lf.lfFaceName);

  newFont_ = fonts_.get(lf);
  if (!newFont_) {
    newFont_ = Hijack::oldCreateFontIndirectW(&lf);
    fonts_.add(newFont_, lf);
  }
  oldFont_ = (HFONT)SelectObject(hdc_, newFont_);
  DOUT("pass");
}

} // unnamed namespace

/** Fonts */

// http://forums.codeguru.com/showthread.php?500522-Need-clarification-about-CreateFontIndirect
// The font creation functions will never fail
HFONT WINAPI Hijack::newCreateFontIndirectA(const LOGFONTA *lplf)
{
  DOUT("pass");
  //DOUT("width:" << lplf->lfWidth << ", height:" << lplf->lfHeight << ", weight:" << lplf->lfWeight);
  if (auto p = HijackHelper::instance()) {
    auto s = p->settings();
    if (lplf && s->isFontCustomized()) {
      union {
        LOGFONTA a;
        LOGFONTW w;
      } lf = {*lplf}; // only initialize the first member of LOGFONTA
      customizeLogFontA(&lf.a);
      if (!s->fontFamily.isEmpty()) {
        if (Util::allAscii(s->fontFamily))
          ::strcpy(lf.a.lfFaceName, s->fontFamily.toLocal8Bit());
        else {
          lf.w.lfFaceName[s->fontFamily.size()] = 0;
          s->fontFamily.toWCharArray(lf.w.lfFaceName);
          return oldCreateFontIndirectW(&lf.w);
        }
      }
      return oldCreateFontIndirectA(&lf.a);
    }
  }
  return oldCreateFontIndirectA(lplf);
}

HFONT WINAPI Hijack::newCreateFontIndirectW(const LOGFONTW *lplf)
{
  DOUT("pass");
  //DOUT("width:" << lplf->lfWidth << ", height:" << lplf->lfHeight << ", weight:" << lplf->lfWeight);
  if (auto p = HijackHelper::instance()) {
    auto s = p->settings();
    if (lplf && s->isFontCustomized()) {
      LOGFONTW lf(*lplf);
      customizeLogFontW(&lf);
      return oldCreateFontIndirectW(&lf);
    }
  }
  return oldCreateFontIndirectW(lplf);
}

#define CREATE_FONT_ARGS    nHeight, nWidth, nEscapement, nOrientation, fnWeight, fdwItalic, fdwUnderline, fdwStrikeOut, fdwCharSet, fdwOutputPrecision, fdwClipPrecision, fdwQuality, fdwPitchAndFamily, lpszFace
HFONT WINAPI Hijack::newCreateFontA(int nHeight, int nWidth, int nEscapement, int nOrientation, int fnWeight, DWORD fdwItalic, DWORD fdwUnderline, DWORD fdwStrikeOut, DWORD fdwCharSet, DWORD fdwOutputPrecision, DWORD fdwClipPrecision, DWORD fdwQuality, DWORD fdwPitchAndFamily, LPCSTR lpszFace)
{
  DOUT("pass");
  if (auto p = HijackHelper::instance()) {
    auto s = p->settings();
    if (s->isFontCustomized()) {
      if (s->fontCharSetEnabled) {
        auto charSet = s->fontCharSet;
        if (!charSet)
          charSet = p->systemCharSet();
        if (charSet)
          fdwCharSet = charSet;
      }
      if (s->fontWeight)
        fnWeight = s->fontWeight;
      if (s->isFontScaled()) {
        nWidth *= s->fontScale;
        nHeight *= s->fontScale;
      }
      if (!s->fontFamily.isEmpty()) {
        if (Util::allAscii(s->fontFamily)) {
          QByteArray ff = s->fontFamily.toLocal8Bit();
          lpszFace = ff.constData();
          return oldCreateFontA(CREATE_FONT_ARGS);
        } else {
          auto lpszFace = (LPCWSTR)s->fontFamily.utf16();
          return oldCreateFontW(CREATE_FONT_ARGS);
        }
      }
    }
  }
  return oldCreateFontA(CREATE_FONT_ARGS);
}

HFONT WINAPI Hijack::newCreateFontW(int nHeight, int nWidth, int nEscapement, int nOrientation, int fnWeight, DWORD fdwItalic, DWORD fdwUnderline, DWORD fdwStrikeOut, DWORD fdwCharSet, DWORD fdwOutputPrecision, DWORD fdwClipPrecision, DWORD fdwQuality, DWORD fdwPitchAndFamily, LPCWSTR lpszFace)
{
  DOUT("pass");
  if (auto p = HijackHelper::instance()) {
    auto s = p->settings();
    if (s->isFontCustomized()) {
      if (s->fontCharSetEnabled) {
        auto charSet = s->fontCharSet;
        if (!charSet)
          charSet = p->systemCharSet();
        if (charSet)
          fdwCharSet = charSet;
      }
      if (s->fontWeight)
        fnWeight = s->fontWeight;
      if (s->isFontScaled()) {
        nWidth *= s->fontScale;
        nHeight *= s->fontScale;
      }
      if (!s->fontFamily.isEmpty())
        lpszFace = (LPCWSTR)s->fontFamily.utf16();
    }
  }
  return oldCreateFontW(CREATE_FONT_ARGS);
}
#undef CREATE_FONT_ARGS

/** Encoding */

LPSTR WINAPI Hijack::newCharNextA(LPCSTR lpString)
{
  DOUT("pass");
  //if (::GetACP() == 932)
  return const_cast<char *>(dynsjis::nextchar(lpString));
  //return oldCharNextA(lpString);
}

LPSTR WINAPI Hijack::newCharPrevA(LPCSTR lpStart, LPCSTR lpCurrent)
{
  DOUT("pass");
  //if (::GetACP() == 932)
  return const_cast<char *>(dynsjis::prevchar(lpCurrent, lpStart));
  //return oldCharNextA(lpStart, lpCurrent);
}

int WINAPI Hijack::newMultiByteToWideChar(UINT CodePage, DWORD dwFlags, LPCSTR lpMultiByteStr, int cbMultiByte, LPWSTR lpWideCharStr, int cchWideChar)
{
  //DOUT("pass");
  if (auto p = HijackHelper::instance())
    if (p->settings()->localeEmulationEnabled)
      if (CodePage == CP_THREAD_ACP || CodePage == CP_OEMCP)
        CodePage = CP_ACP;
  if (auto p = DynamicCodec::instance())
    // CP_ACP(0), CP_MACCP(1), CP_OEMCP(2), CP_THREAD_ACP(3)
    if ((CodePage <= 3 || CodePage == 932) && cchWideChar > 0 && cbMultiByte > 1) {
      bool dynamic;
      QByteArray data(lpMultiByteStr, cbMultiByte);
      QString text = p->decode(data, &dynamic);
      if (dynamic && !text.isEmpty()) {
        DOUT("pass");
        int size = qMin(text.size() + 1, cchWideChar);
        ::memcpy(lpWideCharStr, text.utf16(), size * 2);
        //lpWideCharStr[size - 1] = 0; // enforce trailing zero
        return size - 1;
      }
    }
  return oldMultiByteToWideChar(CodePage, dwFlags, lpMultiByteStr, cbMultiByte, lpWideCharStr, cchWideChar);
}

int WINAPI Hijack::newWideCharToMultiByte(UINT CodePage, DWORD dwFlags, LPCWSTR lpWideCharStr, int cchWideChar, LPSTR lpMultiByteStr, int cbMultiByte, LPCSTR lpDefaultChar, LPBOOL lpUsedDefaultChar)
{
  //DOUT("pass");
  if (auto p = HijackHelper::instance())
    if (p->settings()->localeEmulationEnabled)
      if (CodePage == CP_THREAD_ACP || CodePage == CP_OEMCP)
        CodePage = CP_ACP;
  if (auto p = DynamicCodec::instance())
    if ((CodePage <= 3 || CodePage == 932) && cchWideChar > 0 && cbMultiByte >= 0) {
      bool dynamic;
      QString text = QString::fromWCharArray(lpWideCharStr, cchWideChar);
      QByteArray data = p->encode(text, &dynamic);
      if (dynamic && !data.isEmpty()) {
        DOUT("pass");
        int size = data.size() + 1;
        if (cbMultiByte && cbMultiByte < size)
          size = cbMultiByte;
        ::memcpy(lpMultiByteStr, data.constData(), size);
        //lpMultiByteStr[size - 1] = 0; // enforce trailing zero
        return size - 1;
      }
    }
  return oldWideCharToMultiByte(CodePage, dwFlags, lpWideCharStr, cchWideChar, lpMultiByteStr, cbMultiByte, lpDefaultChar, lpUsedDefaultChar);
}

/** Text */

#define DECODE_CHAR(uChar, ...) \
{ \
  if (uChar > 0xff) \
    if (auto p = DynamicCodec::instance()) { \
      bool dynamic; \
      UINT ch = p->decodeChar(uChar, &dynamic); \
      if (dynamic && ch) { \
        DOUT("dynamic"); \
        uChar = ch; \
        return (__VA_ARGS__); \
      } \
    } \
}

#define DECODE_TEXT(lpString, cchString, ...) \
{ \
  if(cchString == -1 || cchString > 1) \
    if (auto p = DynamicCodec::instance()) { \
      bool dynamic; \
      QByteArray data = QByteArray::fromRawData(lpString, cchString == -1 ? ::strlen(lpString) : cchString); \
      if (data.size() > 1) { \
        QString text = p->decode(data, &dynamic); \
        if (dynamic && !text.isEmpty()) { \
          DOUT("dynamic"); \
          LPCWSTR lpString = (LPCWSTR)text.utf16(); \
          cchString = text.size(); \
          return (__VA_ARGS__); \
        } \
      } \
    } \
}

#define TRANSLATE_TEXT_A(lpString, cchString, ...) \
{ \
  if (auto q = EngineController::instance()) { \
    QByteArray data = QByteArray::fromRawData(lpString, cchString == -1 ? ::strlen(lpString) : cchString); \
    QString oldText = q->decode(data); \
    if (!oldText.isEmpty()) { \
      enum { role = Engine::OtherRole }; \
      ulong split = (ulong)_ReturnAddress(); \
      auto sig = Engine::hashThreadSignature(role, split); \
      QString newText = q->dispatchTextW(oldText, role, sig); \
      if (newText != oldText) { \
        LPCWSTR lpString = (LPCWSTR)newText.utf16(); \
        cchString = newText.size(); \
        return (__VA_ARGS__); \
      } \
    } \
  } \
}

#define TRANSLATE_TEXT_W(lpString, cchString, ...) \
{ \
  if (auto q = EngineController::instance()) { \
    QString text = QString::fromWCharArray(lpString, cchString); \
    if (!text.isEmpty()) { \
      enum { role = Engine::OtherRole }; \
      ulong split = (ulong)_ReturnAddress(); \
      auto sig = Engine::hashThreadSignature(role, split); \
      text = q->dispatchTextW(text, role, sig); \
      LPCWSTR lpString = (LPCWSTR)text.utf16(); \
      cchString = text.size(); \
      return (__VA_ARGS__); \
    } \
  } \
}

DWORD WINAPI Hijack::newGetGlyphOutlineA(HDC hdc, UINT uChar, UINT uFormat, LPGLYPHMETRICS lpgm, DWORD cbBuffer, LPVOID lpvBuffer, const MAT2 *lpmat2)
{
  DOUT("pass");
  DCFontSwitcher fs(hdc);
  DECODE_CHAR(uChar, oldGetGlyphOutlineW(hdc, ch, uFormat, lpgm, cbBuffer, lpvBuffer, lpmat2))
  return oldGetGlyphOutlineA(hdc, uChar, uFormat, lpgm, cbBuffer, lpvBuffer, lpmat2);
}

DWORD WINAPI Hijack::newGetGlyphOutlineW(HDC hdc, UINT uChar, UINT uFormat, LPGLYPHMETRICS lpgm, DWORD cbBuffer, LPVOID lpvBuffer, const MAT2 *lpmat2)
{
  DOUT("pass");
  DCFontSwitcher fs(hdc);
  return oldGetGlyphOutlineW(hdc, uChar, uFormat, lpgm, cbBuffer, lpvBuffer, lpmat2);
}

BOOL WINAPI Hijack::newGetTextExtentPoint32A(HDC hdc, LPCSTR lpString, int cchString, LPSIZE lpSize)
{
  DOUT("pass");
  DCFontSwitcher fs(hdc);
  //TRANSLATE_TEXT_A(lpString, cchString, oldGetTextExtentPoint32W(hdc, lpString, cchString, lpSize))
  DECODE_TEXT(lpString, cchString, oldGetTextExtentPoint32W(hdc, lpString, cchString, lpSize))
  return oldGetTextExtentPoint32A(hdc, lpString, cchString, lpSize);
}

BOOL WINAPI Hijack::newGetTextExtentPoint32W(HDC hdc, LPCWSTR lpString, int cchString, LPSIZE lpSize)
{
  DOUT("pass");
  DCFontSwitcher fs(hdc);
  //TRANSLATE_TEXT_W(lpString, cchString, oldGetTextExtentPoint32W(hdc, lpString, cchString, lpSize))
  return oldGetTextExtentPoint32W(hdc, lpString, cchString, lpSize);
}

BOOL WINAPI Hijack::newGetTextExtentExPointA(HDC hdc, LPCSTR lpString, int cchString, int nMaxExtent, LPINT lpnFit, LPINT alpDx, LPSIZE lpSize)
{
  DOUT("pass");
  DCFontSwitcher fs(hdc);
  //TRANSLATE_TEXT_A(lpString, cchString, oldGetTextExtentExPointW(hdc, lpString, cchString, nMaxExtent, lpnFit, alpDx, lpSize))
  DECODE_TEXT(lpString, cchString, oldGetTextExtentExPointW(hdc, lpString, cchString, nMaxExtent, lpnFit, alpDx, lpSize))
  return oldGetTextExtentExPointA(hdc, lpString, cchString, nMaxExtent, lpnFit, alpDx, lpSize);
}

BOOL WINAPI Hijack::newGetTextExtentExPointW(HDC hdc, LPCWSTR lpString, int cchString, int nMaxExtent, LPINT lpnFit, LPINT alpDx, LPSIZE lpSize)
{
  DOUT("pass");
  DCFontSwitcher fs(hdc);
  //TRANSLATE_TEXT_W(lpString, cchString, oldGetTextExtentExPointW(hdc, lpString, cchString, nMaxExtent, lpnFit, alpDx, lpSize))
  return oldGetTextExtentExPointW(hdc, lpString, cchString, nMaxExtent, lpnFit, alpDx, lpSize);
}

int WINAPI Hijack::newDrawTextA(HDC hdc, LPCSTR lpString, int cchString, LPRECT lpRect, UINT uFormat)
{
  DOUT("pass");
  DCFontSwitcher fs(hdc);
  if (HijackManager::instance()->isFunctionTranslated((ulong)::DrawTextA))
    TRANSLATE_TEXT_A(lpString, cchString, oldDrawTextW(hdc, lpString, cchString, lpRect, uFormat))
  else
    DECODE_TEXT(lpString, cchString, oldDrawTextW(hdc, lpString, cchString, lpRect, uFormat))
  return oldDrawTextA(hdc, lpString, cchString, lpRect, uFormat);
}

int WINAPI Hijack::newDrawTextW(HDC hdc, LPCWSTR lpString, int cchString, LPRECT lpRect, UINT uFormat)
{
  DOUT("pass");
  DCFontSwitcher fs(hdc);
  if (HijackManager::instance()->isFunctionTranslated((ulong)::DrawTextW))
    TRANSLATE_TEXT_W(lpString, cchString, oldDrawTextW(hdc, lpString, cchString, lpRect, uFormat))
  return oldDrawTextW(hdc, lpString, cchString, lpRect, uFormat);
}

int WINAPI Hijack::newDrawTextExA(HDC hdc, LPSTR lpString, int cchString, LPRECT lpRect, UINT dwDTFormat, LPDRAWTEXTPARAMS lpDTParams)
{
  DOUT("pass");
  DCFontSwitcher fs(hdc);
  if (!(dwDTFormat & DT_MODIFYSTRING)) {
    if (HijackManager::instance()->isFunctionTranslated((ulong)::DrawTextExA))
      TRANSLATE_TEXT_A(lpString, cchString, oldDrawTextExW(hdc, const_cast<LPWSTR>(lpString), cchString, lpRect, dwDTFormat, lpDTParams))
    else
      DECODE_TEXT(lpString, cchString, oldDrawTextExW(hdc, const_cast<LPWSTR>(lpString), cchString, lpRect, dwDTFormat, lpDTParams))
  }
  return oldDrawTextExA(hdc, lpString, cchString, lpRect, dwDTFormat, lpDTParams);
}

int WINAPI Hijack::newDrawTextExW(HDC hdc, LPWSTR lpString, int cchString, LPRECT lpRect, UINT dwDTFormat, LPDRAWTEXTPARAMS lpDTParams)
{
  DOUT("pass");
  DCFontSwitcher fs(hdc);
  if (!(dwDTFormat & DT_MODIFYSTRING) && HijackManager::instance()->isFunctionTranslated((ulong)::DrawTextExW))
    TRANSLATE_TEXT_W(lpString, cchString, oldDrawTextExW(hdc, const_cast<LPWSTR>(lpString), cchString, lpRect, dwDTFormat, lpDTParams))
  return oldDrawTextExW(hdc, lpString, cchString, lpRect, dwDTFormat, lpDTParams);
}

BOOL WINAPI Hijack::newTextOutA(HDC hdc, int nXStart, int nYStart, LPCSTR lpString, int cchString)
{
  DOUT("pass");
  DCFontSwitcher fs(hdc);
  if (HijackManager::instance()->isFunctionTranslated((ulong)::TextOutA))
    TRANSLATE_TEXT_A(lpString, cchString, oldTextOutW(hdc, nXStart, nYStart, lpString, cchString))
  else
    DECODE_TEXT(lpString, cchString, oldTextOutW(hdc, nXStart, nYStart, lpString, cchString))
  return oldTextOutA(hdc, nXStart, nYStart, lpString, cchString);
}

BOOL WINAPI Hijack::newTextOutW(HDC hdc, int nXStart, int nYStart, LPCWSTR lpString, int cchString)
{
  DOUT("pass");
  DCFontSwitcher fs(hdc);
  if (HijackManager::instance()->isFunctionTranslated((ulong)::TextOutW))
    TRANSLATE_TEXT_W(lpString, cchString, oldTextOutW(hdc, nXStart, nYStart, lpString, cchString))
  return oldTextOutW(hdc, nXStart, nYStart, lpString, cchString);
}

BOOL WINAPI Hijack::newExtTextOutA(HDC hdc, int X, int Y, UINT fuOptions, const RECT *lprc, LPCSTR lpString, UINT cchString, const INT *lpDx)
{
  DOUT("pass");
  DCFontSwitcher fs(hdc);
  if (HijackManager::instance()->isFunctionTranslated((ulong)::ExtTextOutA))
    TRANSLATE_TEXT_A(lpString, cchString, oldExtTextOutW(hdc, X, Y, fuOptions, lprc, lpString, cchString, lpDx))
  else
    DECODE_TEXT(lpString, cchString, oldExtTextOutW(hdc, X, Y, fuOptions, lprc, lpString, cchString, lpDx))
  return oldExtTextOutA(hdc, X, Y, fuOptions, lprc, lpString, cchString, lpDx);
}

BOOL WINAPI Hijack::newExtTextOutW(HDC hdc, int X, int Y, UINT fuOptions, const RECT *lprc, LPCWSTR lpString, UINT cchString, const INT *lpDx)
{
  DOUT("pass");
  DCFontSwitcher fs(hdc);
  if (HijackManager::instance()->isFunctionTranslated((ulong)::ExtTextOutW))
    TRANSLATE_TEXT_W(lpString, cchString, oldExtTextOutW(hdc, X, Y, fuOptions, lprc, lpString, cchString, lpDx))
  return oldExtTextOutW(hdc, X, Y, fuOptions, lprc, lpString, cchString, lpDx);
}

LONG WINAPI Hijack::newTabbedTextOutA(HDC hdc, int X, int Y, LPCSTR lpString, int cchString, int nTabPositions, const int *lpnTabStopPositions, int nTabOrigin)
{
  DOUT("pass");
  DCFontSwitcher fs(hdc);
  if (HijackManager::instance()->isFunctionTranslated((ulong)::TabbedTextOutA))
    TRANSLATE_TEXT_A(lpString, cchString, oldTabbedTextOutW(hdc, X, Y, lpString, cchString, nTabPositions, lpnTabStopPositions, nTabOrigin))
  else
    DECODE_TEXT(lpString, cchString, oldTabbedTextOutW(hdc, X, Y, lpString, cchString, nTabPositions, lpnTabStopPositions, nTabOrigin))
  return oldTabbedTextOutA(hdc, X, Y, lpString, cchString, nTabPositions, lpnTabStopPositions, nTabOrigin);
}

LONG WINAPI Hijack::newTabbedTextOutW(HDC hdc, int X, int Y, LPCWSTR lpString, int cchString, int nTabPositions, const int *lpnTabStopPositions, int nTabOrigin)
{
  DOUT("pass");
  DCFontSwitcher fs(hdc);
  if (HijackManager::instance()->isFunctionTranslated((ulong)::TabbedTextOutW))
    TRANSLATE_TEXT_W(lpString, cchString, oldTabbedTextOutW(hdc, X, Y, lpString, cchString, nTabPositions, lpnTabStopPositions, nTabOrigin))
  return oldTabbedTextOutW(hdc, X, Y, lpString, cchString, nTabPositions, lpnTabStopPositions, nTabOrigin);
}

// EOF

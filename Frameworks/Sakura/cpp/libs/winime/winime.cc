// winime.cc
// 4/1/2013 jichi
//
// See:
// http://msdn.microsoft.com/en-us/library/windows/desktop/hh851782%28v=vs.85%29.aspx
// http://tech.ddvip.com/2007-09/118923427533812.html
// http://www.haogongju.net/art/1673851
// http://www.ccrun.com/article.asp?i=1028&d=r0j832
//
// The code must be wrapped within OleInitialize/OleUninitialize

#include "winime/winime.h"
#include <windows.h>
#include <msime.h>
//#include <QDebug>

// Interface ID for IFELanguage
// {019F7152-E6DB-11d0-83C3-00C04FDDB82E}
//DEFINE_GUID(IID_IFELanguage,
//0x19f7152, 0xe6db, 0x11d0, 0x83, 0xc3, 0x0, 0xc0, 0x4f, 0xdd, 0xb8, 0x2e);
static const IID IID_IFELanguage = { 0x019f7152, 0xe6db, 0x11d0, { 0x83, 0xc3, 0x00, 0xc0, 0x4f, 0xdd, 0xb8, 0x2e } };

winime_t *winime_create(const wchar_t *cls) ///< create an im engine of given class
{

  CLSID clsid;
  if (FAILED(::CLSIDFromString(cls, &clsid))) // resolve clsid at runtime, instead of CLSID_MSIME_JAPANESE_?
    return nullptr;
  //Q_ASSERT(cls);

  IFELanguage *ife = nullptr;
  if (FAILED(::CoCreateInstance(clsid, nullptr, CLSCTX_SERVER, IID_IFELanguage,
                                reinterpret_cast<LPVOID *>(&ife))))
    return nullptr;

  if (SUCCEEDED(ife->Open())) {
    DWORD dwCaps;
    if (SUCCEEDED(ife->GetConversionModeCaps(&dwCaps)))
      return ife;
    ife->Close();
  }
  ife->Release();
  return nullptr;
}

void winime_destroy(winime_t *ife)
{
  if (ife) {
    ife->Close();
    ife->Release();
  }
}

// Get the entire result
bool winime_apply(winime_t *ife, unsigned long req, unsigned long mode,
    const wchar_t *src, size_t len, const winime_apply_fun_t &fun)
{
  if (!ife || !src || !fun)
    return false;
  MORRSLT *mr = nullptr;
  if (FAILED(ife->GetJMorphResult(req, mode, len, src, nullptr, &mr)) || !mr)
    return false;
  //Q_ASSERT(mr);
  //qDebug() << QString::fromWCharArray(mr->pwchOutput, mr->cchOutput);
  fun(mr->pwchOutput, mr->cchOutput);
  ::CoTaskMemFree(mr);
  return true;
}

bool winime_collect(winime_t *ife, unsigned long req, unsigned long mode,
    const wchar_t *src, size_t len, const winime_collect_fun_t &fun)
{
  if (!ife || !src || !fun)
    return false;
  MORRSLT *mr = nullptr;
  if (FAILED(ife->GetJMorphResult(req, mode, len, src, nullptr, &mr)) || !mr)
    return false;
  //Q_ASSERT(mr);
  //qDebug() << QString::fromWCharArray(mr->pwchOutput, mr->cchOutput);
  //qDebug() << mr->cWDD;

  //for (int i = 0; i < mr->cWDD; i++) {
  //  const WDD *it = mr->pWDD + i;
  for (const WDD *it = mr->pWDD; it != mr->pWDD + mr->cWDD; ++it)
    fun(src + it->wReadPos, it->cchRead,
         mr->pwchOutput + it->wDispPos, it->cchDisp);
    //qDebug()<<QString::fromWCharArray(pwchInput+mr->pWDD[i].wReadPos, mr->pWDD[i].cchRead);
    //qDebug()<<QString::fromWCharArray(mr->pwchOutput+mr->pWDD[i].wReadPos, mr->pWDD[i].cchRead);
  ::CoTaskMemFree(mr);
  return true;
}

// EOF

/*
#include <QtCore>
#include <qt_windows.h>
#include <msime.h>
HRESULT SetIMEEngine(LPCWSTR msime)
{
  static const IID IID_IFELanguage = { 0x019f7152, 0xe6db, 0x11d0, { 0x83, 0xc3, 0x00, 0xc0, 0x4f, 0xdd, 0xb8, 0x2e } };
  //UnsetIMEEngine();

  CLSID clsid;
  if (S_OK != ::CLSIDFromString(const_cast<LPWSTR>(msime), &clsid))
    return S_FALSE;

  ::OleInitialize(nullptr);

  IFELanguage *ife = nullptr;
  if (S_OK != ::CoCreateInstance(clsid, nullptr, CLSCTX_SERVER, IID_IFELanguage, reinterpret_cast<LPVOID *>(&ife)))
    return S_FALSE;
  Q_ASSERT(ife);
  if (S_OK == ife->Open()) {
    DWORD dwCaps;
    if (S_OK == ife->GetConversionModeCaps(&dwCaps)) {
      MORRSLT *mr = nullptr;

      // http://msdn.microsoft.com/ja-jp/library/windows/desktop/hh851782%28v=vs.85%29.aspx
      DWORD dwRequest = FELANG_REQ_REV;
      DWORD dwCMode = FELANG_CMODE_HIRAGANAOUT;
      LPWSTR pwchInput = L"\u7F8E\u7F8E\u7F8E\u7F8E"; // utukusi
      if (S_OK == ife->GetJMorphResult(dwRequest, dwCMode,
          static_cast<INT>(::wcslen(pwchInput)), const_cast<WCHAR*>(pwchInput),
          nullptr, &mr)) {
        Q_ASSERT(mr);
        qDebug() << QString::fromWCharArray(mr->pwchOutput, mr->cchOutput);
        qDebug() << mr->cWDD;
        for(int i=0; i<mr->cWDD;i++) {
          qDebug()<<QString::fromWCharArray(pwchInput+mr->pWDD[i].wReadPos, mr->pWDD[i].cchRead);
          qDebug()<<QString::fromWCharArray(mr->pwchOutput+mr->pWDD[i].wReadPos, mr->pWDD[i].cchRead);
        }
        ::CoTaskMemFree(mr);
      }
    }

    ife->Close();
  }

  ife->Release();

  ::CoUninitialize();

  //m_bCoCreat = TRUE;

  //if (m_pIFELanguage)
  //  if (m_pIFELanguage->Open() == S_OK)
  //    m_bLangOpen = TRUE;

  //m_pIFELanguage->GetConversionModeCaps( &m_dwCaps );
  //m_ImeName = msime;

  return S_OK;
}

//L"MSIME.China";
//L"MSIME.Japan";
//L"MSIME.Taiwan";
//L"MSIME.Taiwan.ImeBbo";

int main()
{
  SetIMEEngine(L"MSIME.Japan");
  //DWORD dwRequest;           // [in]
  // DWORD dwCMode;            //  [in]
  // INT cwchInput;            //  [in]
  // const WCHAR *pwchInput;   //  [in]
  // DWORD *pfCInfo;           //  [in]
  // MORRSLT **ppResult;       //  [out]
  //HRESULT ret = GetJMorphResult(dwRequest, dwCMode, cwchInput, pwchInput, pfCInfo, ppResult);
  return 0;
}
*/

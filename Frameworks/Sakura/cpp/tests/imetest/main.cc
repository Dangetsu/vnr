// main.cc
// 1/5/2015 jichi
// Test Pinyin
// http://www.ccrun.com/article.asp?i=1028&d=r0j832
#include <qt_windows.h>
#include <msime.h>
#include <QtCore>

int main()
{
  //CoInitialize(nullptr);
  OleInitialize(nullptr);
  //CoInitializeEx(nullptr, COINIT_MULTITHREADED);

  static const IID IID_IFELanguage = {
    0x019f7152, 0xe6db, 0x11d0,
    { 0x83, 0xc3, 0x00, 0xc0, 0x4f, 0xdd, 0xb8, 0x2e }
  };

  LPCWSTR msime = L"MSIME.China";
  //LPCWSTR msime = L"MSIME.China.14";
  //LPCWSTR msime = L"MSIME.Korea";
  //LPCWSTR msime = L"MSIME.Korea.14";
  CLSID clsid;
  if(CLSIDFromString(const_cast<LPWSTR>(msime), &clsid) != S_OK)
      return 0;

  // 创建一个IFELanguage的COM实例，得到接口指针
  IFELanguage *pIFELanguage;
  if (CoCreateInstance(clsid, NULL, CLSCTX_SERVER,
      IID_IFELanguage, (LPVOID*)&pIFELanguage) != S_OK)
    return 0;

  if (!pIFELanguage)
    return 0;

  // 打开
  if (pIFELanguage->Open() != S_OK) {
    pIFELanguage->Release();
    return 0;
  }

  //
  DWORD dwCaps;
  if (pIFELanguage->GetConversionModeCaps(&dwCaps) != S_OK) {
    pIFELanguage->Close();
    pIFELanguage->Release();
  }

  LPCWSTR w = L"hello";
  MORRSLT *pmorrslt;
  if (pIFELanguage->GetJMorphResult(
      FELANG_REQ_REV,
      FELANG_CMODE_PINYIN |
      FELANG_CMODE_NOINVISIBLECHAR,
      wcslen(w), w, NULL, &pmorrslt) != S_OK) {
    pIFELanguage->Close();
    pIFELanguage->Release();
  }
  if (!pmorrslt) {
    pIFELanguage->Close();
    pIFELanguage->Release();
  }

  qDebug() << pmorrslt->cchOutput;
  qDebug() << pmorrslt->cWDD;

  CoTaskMemFree(pmorrslt);
  pIFELanguage->Close();
  pIFELanguage->Release();

  OleUninitialize();
  return 0;
}

// EOF

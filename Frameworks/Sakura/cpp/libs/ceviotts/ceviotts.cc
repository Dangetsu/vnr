// ceviotts.cc
// 6/15/2014 jichi
// http://guide2.project-cevio.com/interface/com

#include "ceviotts/ceviotts.h"
#include "cevio/cevio.h"
#include "ccutil/ccmacro.h"

// For 2.2.5.1
//#import "libid:D3AAEA482-B527-4818-8CEA-810AFFCB24B6" named_guids rename_namespace("CeVIO")
//#import "C:\Program Files\CeVIO\CeVIO Creative Studio\CeVIO.Talk.RemoteService.tlb" named_guids rename_namespace("CeVIO")

#define CEVIO_SERVICE_CONTROL // TODO: missing service control

// Service control

cevioservice_t *cevioservice_create(bool launch)
{
  CeVIO::IServiceControl *ret;
  HRESULT ok = ::CoCreateInstance(CeVIO::CLSID_ServiceControl,
    nullptr,
    CLSCTX_INPROC_SERVER,
    CeVIO::IID_IServiceControl,
    reinterpret_cast<LPVOID *>(&ret));
  if (FAILED(ok))
    return nullptr;

  if (launch)
    ret->StartHost(false);
  return ret;
}

void cevioservice_destroy(cevioservice_t *service)
{
  if (CC_LIKELY(service)) {
      service->CloseHost(0);
    service->Release();
  }
}

// Talker

ceviotts_t *ceviotts_create()
{
  CeVIO::ITalker *ret = nullptr;
  HRESULT ok = ::CoCreateInstance(CeVIO::CLSID_Talker,
      nullptr,
      CLSCTX_INPROC_SERVER,
      CeVIO::IID_ITalker,
      reinterpret_cast<LPVOID *>(&ret));
  return SUCCEEDED(ok) ? ret : nullptr;
}

void ceviotts_destroy(ceviotts_t *talker)
{ talker->Release(); }

ceviotask_t *ceviotts_speak(ceviotts_t *talker, const char *text)
{ return talker->Speak(text); }

bool ceviotask_wait(ceviotask_t *state)
{ return SUCCEEDED(state->Wait()); }

bool ceviotask_wait(ceviotask_t *state, double seconds)
{ return SUCCEEDED(state->Wait_2(seconds)); }

// Properties

void ceviotts_set_cast(ceviotts_t *talker, const char *value)
{ talker->Cast = value; }

void ceviotts_set_volume(ceviotts_t *talker, long value)
{ talker->Volume = value; }

void ceviotts_set_speed(ceviotts_t *talker, long value)
{ talker->Speed = value; }

void ceviotts_set_tone(ceviotts_t *talker, long value)
{ talker->Tone = value; }

void ceviotts_set_alpha(ceviotts_t *talker, long value)
{ talker->Alpha = value; }

// EOF

/*
// タイプライブラリインポート
// （タイプライブラリの登録は、【CeVIO Creative Studio】インストール時に行われます。）
#import "libid:D3AEA482-B527-4818-8CEA-810AFFCB24B6" named_guids rename_namespace("CeVIO")

int _tmain(int argc, _TCHAR* argv[])
{

  // COM初期化
  ::CoInitialize(NULL);

  // Talkerインスタンス生成
  CeVIO::ITalker *pTalker;
  HRESULT result = ::CoCreateInstance(CeVIO::CLSID_Talker,
    NULL,
    CLSCTX_INPROC_SERVER,
    CeVIO::IID_ITalker,
    reinterpret_cast<LPVOID *>(&pTalker));
  if (FAILED(result)) {
    // 失敗
    ::CoUninitialize();
    return 0;
  }

  // キャスト設定
  pTalker->Cast = "さとうささら";

  // （例）音量設定
  pTalker->Volume = 100;

  // （例）再生
  CeVIO::ISpeakingStatePtr pState = pTalker->Speak("こんにちは");

  // （例）再生終了を待つ
  pState->Wait();

  // （例）音素データ取得
  CeVIO::IPhonemeDataArrayPtr pPhonemes = pTalker->GetPhonemes("はじめまして");

  // Talker解放
  pTalker->Release();

  // COM使用終了
  ::CoUninitialize();

  return 0;
}
*/

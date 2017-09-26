// main.cc
// 9/17/2014 jichi
#include <windows.h>
#include <iostream>
#include <string>

extern "C" {
typedef DWORD (__stdcall *InitContext)(BYTE arg1, const char *path, BYTE arg3, BYTE arg4, BYTE arg5, int arg6, int arg7, BYTE arg8);
typedef BOOL (__stdcall *CloseContext)();
typedef DWORD (__stdcall *TranslateMem)(UINT fmt, HGLOBAL in, HGLOBAL *out);
}

int main()
{
  const wchar_t *text = L"hello world";
  std::cerr << "enter" << std::endl;
  HMODULE h = ::LoadLibraryA("pars.dll");
  BOOL ok;
  std::cerr << h << std::endl;
  if (h) {
    const char *path = "Z:\\Local\\Windows\\Applications\\Power Translator 15\\Pars\\EnRu\\DIC\\gen_";
    InitContext initContext = (InitContext)::GetProcAddress(h, "InitContext");
    CloseContext closeContext = (CloseContext)::GetProcAddress(h, "CloseContext");
    TranslateMem translateMem = (TranslateMem)::GetProcAddress(h, "TranslateMem");

    DWORD r = initContext(0, path, 0, 0, 0, 1, 0, 1);
    std::cerr << "InitContext: " << r << std::endl;
    wchar_t *p;
    if (r == 0) {
      SIZE_T memsize = 0x2000;
      HGLOBAL in = ::GlobalAlloc(0, memsize);
      p = (wchar_t *)::GlobalLock(in);
      wcscpy(p, text);
      ok = ::GlobalUnlock(in);

      std::cerr << "begin"<< std::endl;
      HGLOBAL out = nullptr;
      r = translateMem(CF_UNICODETEXT, in, &out);
      std::cerr << "end"<< std::endl;
      std::cerr << "TranslateMem: " << r << std::endl;
      std::cerr << "mem: " << out << std::endl;
      r = ::GlobalSize(out);
      std::cerr << "size: " << r << std::endl;

      p = (wchar_t *)::GlobalLock(out);
      std::cerr << "GlobalLock 0: " << std::hex << int(p[0]) << std::endl;
      std::cerr << "GlobalLock 1: " << std::hex << int(p[1]) << std::endl;
      std::cerr << "GlobalLock 2: " << std::hex << int(p[2]) << std::endl;
      std::cerr << "GlobalLock 3: " << std::hex << int(p[3]) << std::endl;
      //std::cerr << "GlobalLock 7: " << int(p[7]) << std::endl;
      //std::cerr << "GlobalLock 8: " << int(p[8]) << std::endl;
      //std::cerr << "GlobalLock 9: " << int(p[9]) << std::endl;
      ok = ::GlobalUnlock(out);
      std::cerr << "GlobalUnlock: " << ok << std::endl;

      ok = closeContext();
      std::cerr << "CloseContext: " << ok << std::endl;
    }
  }
  std::cerr << "leave" << std::endl;
  return 0;
}

// EOF

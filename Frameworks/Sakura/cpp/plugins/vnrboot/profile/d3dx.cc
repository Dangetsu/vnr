// profile/d3dx.cc
// 8/4/2015

#include "profile.h"
#include "winhook/hookcode.h"
#include "winhook/hookfun.h"
#include <windows.h>
#include <d3dx9.h>
#include <string>

#ifdef _MSC_VER
# pragma warning(disable:4800) // C4800: forcing value to bool (performance warning)
#endif // _MSC_VER

#include "debug.h"
namespace { // unnamed

// INT DrawText(
//   [in] LPD3DXSPRITE pSprite,
//   [in] LPCTSTR      pString,
//   [in] INT          Count,
//   [in] LPRECT       pRect,
//   [in] DWORD        Format,
//   [in] D3DCOLOR     Color
// );
bool beforeDrawTextA(int i, winhook::hook_stack *s)
{
  std::string t = std::to_string((long long)i);
  dmsg(t.c_str());
  return true;
}
void hookFont(ID3DXFont *self)
{
  unsigned long *p = (unsigned long *)self;
  p = (unsigned long *)*p;
  std::string t = std::to_string((long long)p);
  dmsg(t.c_str());
  return;
  //winhook::hook_before(p[14], beforeDrawTextA);
  bool ok = true;
  for (int i = 2; i < 18; i++) {
    ok = winhook::hook_before(p[i], [i](winhook::hook_stack *s) -> bool {
      return beforeDrawTextA(i, s);
    }) && ok;
  }
  if (ok)
    dmsg("hook ok");
  else
    dmsg("hook failed");
}

//enum { D3D_OK = 0 };
//
//typedef LPVOID LPDIRECT3DDEVICE9;
//typedef LPVOID LPD3DXFONT;
//typedef void D3DXFONT_DESCA;

// HRESULT WINAPI D3DXCreateFontIndirect(
//   _In_        LPDIRECT3DDEVICE9 pDevice,
//   _In_  const D3DXFONT_DESCA    *pDesc,
//   _Out_       LPD3DXFONT        *ppFont
// );
typedef HRESULT (WINAPI *D3DXCreateFontIndirectA_fun_t)(LPDIRECT3DDEVICE9 pDevice, const D3DXFONT_DESCA *pDesc, LPD3DXFONT *ppFont);
D3DXCreateFontIndirectA_fun_t oldD3DXCreateFontIndirectA;
HRESULT WINAPI newD3DXCreateFontIndirectA(LPDIRECT3DDEVICE9 pDevice, const D3DXFONT_DESCA *pDesc, LPD3DXFONT *ppFont)
{
  static bool pass;
  auto ret = oldD3DXCreateFontIndirectA(pDevice, pDesc, ppFont);
  if (ret == D3D_OK && !pass) {
    pass = true;
    hookFont(*ppFont);
  }
  return ret;
}

// IDirect3D9* Direct3DCreate9(
//    UINT SDKVersion
// );

/*
typedef IDirect3D9 *(WINAPI *Direct3DCreate9_fun_t)(UINT SDKVersion);
Direct3DCreate9_fun_t oldDirect3DCreate9;
IDirect3D9 *WINAPI newDirect3DCreate9(UINT SDKVersion)
{
  static bool pass;
  auto ret = oldDirect3DCreate9(SDKVersion);
  if (ret && !pass) {
    pass = true;
  }
  return ret;
}
*/
} // unnamed namespace

namespace D3DXProfile {

bool load()
{
  HMODULE h =::GetModuleHandleA("d3dx9_33.dll");
  if (!h)
    return false;
  LPCVOID addr = ::GetProcAddress(h, "D3DXCreateFontIndirectA");
  if (!addr)
    return false;
  return oldD3DXCreateFontIndirectA = (D3DXCreateFontIndirectA_fun_t)winhook::replace_fun((ULONG)addr, (ULONG)newD3DXCreateFontIndirectA);
  /*
  HMODULE h =::GetModuleHandleA("d3d9.dll");
  if (!h)
    return false;
  LPCVOID addr = ::GetProcAddress(h, "Direct3DCreate9");
  if (!addr)
    return false;
  return oldDirect3DCreate9 = (Direct3DCreate9_fun_t)winhook::replace_fun((ULONG)addr, (ULONG)newDirect3DCreate9);
  */
}

} // namespace D3DXProfile

// EOF

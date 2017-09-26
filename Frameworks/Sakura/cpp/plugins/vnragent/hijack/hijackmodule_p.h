#pragma once

// hijackmodule_p.h
// 1/27/2013 jichi

#include <windows.h>

#define HIJACK_FUNCTIONS_INITIALIZER \
    { "kernel32.dll", "GetProcAddress", ::GetProcAddress, Hijack::newGetProcAddress } \
  , { "kernel32.dll", "LoadLibraryA", ::LoadLibraryA, Hijack::newLoadLibraryA } \
  , { "kernel32.dll", "LoadLibraryW", ::LoadLibraryW, Hijack::newLoadLibraryW } \
  , { "kernel32.dll", "LoadLibraryExA", ::LoadLibraryExA, Hijack::newLoadLibraryExA } \
  , { "kernel32.dll", "LoadLibraryExW", ::LoadLibraryExW, Hijack::newLoadLibraryExW } \
  , { "user32.dll", "TrackPopupMenu", ::TrackPopupMenu, Hijack::newTrackPopupMenu } \
  , { "user32.dll", "TrackPopupMenuEx", ::TrackPopupMenuEx, Hijack::newTrackPopupMenuEx } \
  , { "gdi32.dll", "CreateFontA", ::CreateFontA, Hijack::newCreateFontA } \
  , { "gdi32.dll", "CreateFontW", ::CreateFontW, Hijack::newCreateFontW } \
  , { "gdi32.dll", "CreateFontIndirectA", ::CreateFontIndirectA, Hijack::newCreateFontIndirectA } \
  , { "gdi32.dll", "CreateFontIndirectW", ::CreateFontIndirectW, Hijack::newCreateFontIndirectW }
  //{ "gdi32.dll", "GetGlyphOutlineA", ::GetGlyphOutlineA, Hijack::newGetGlyphOutlineA }
  //{ "gdi32.dll", "GetTextExtentPoint32A", ::GetTextExtentPoint32A, Hijack::newGetTextExtentPoint32A }
  //{ "gdi32.dll", "TextOutA", ::TextOutA, Hijack::newTextOutA }
  //{ "gdi32.dll", "ExtTextOutA", ::ExtTextOutA, Hijack::newExtTextOutA }
  //{ "user32.dll", "DrawTextA", ::DrawTextA, Hijack::newDrawTextA }
  //{ "user32.dll", "DrawTextExA", ::DrawTextExA, Hijack::newDrawTextExA }
  //{ "kernel32.dll", "MultiByteToWideChar", ::MultiByteToWideChar, Hijack::newMultiByteToWideChar }
  //{ "kernel32.dll", "WideCharToMultiByte", ::WideCharToMultiByte, Hijack::newWideCharToMultiByte }

namespace Hijack {

struct FunctionInfo {
  LPCSTR moduleName;
  LPCSTR functionName;
  LPVOID oldFunctionAddress;
  LPVOID newFunctionAddress;
};

void overrideModuleFunctions(HMODULE hModule);
void restoreModuleFunctions(HMODULE hModule);

// Return new function used to override proc name
LPVOID getOverridingFunctionAddress(HMODULE hModule, LPCSTR lpProcName);

// - KERNEL32 -

LPVOID WINAPI newGetProcAddress(
  _In_ HMODULE hModule,
  _In_ LPCSTR lpProcName
);
HMODULE WINAPI newLoadLibraryA(
  _In_  LPCSTR lpFileName
);
HMODULE WINAPI newLoadLibraryW(
  _In_  LPCWSTR lpFileName
);
HMODULE WINAPI newLoadLibraryExA(
  _In_ LPCSTR lpFileName,
  __reserved HANDLE hFile,  // _Reserved_ not supported in MSVC 2010
  _In_ DWORD dwFlags
);
HMODULE WINAPI newLoadLibraryExW(
  _In_ LPCWSTR lpFileName,
  __reserved HANDLE hFile,
  _In_ DWORD dwFlags
);

//int WINAPI newMultiByteToWideChar(
//  _In_       UINT CodePage,
//  _In_       DWORD dwFlags,
//  _In_       LPCSTR lpMultiByteStr,
//  _In_       int cbMultiByte,
//  _Out_opt_  LPWSTR lpWideCharStr,
//  _In_       int cchWideChar
//);
//
//int WINAPI newWideCharToMultiByte(
//  _In_       UINT CodePage,
//  _In_       DWORD dwFlags,
//  _In_       LPCWSTR lpWideCharStr,
//  _In_       int cchWideChar,
//  _Out_opt_  LPSTR lpMultiByteStr,
//  _In_       int cbMultiByte,
//  _In_opt_   LPCSTR lpDefaultChar,
//  _Out_opt_  LPBOOL lpUsedDefaultChar
//);

// - USER32 -

BOOL WINAPI newTrackPopupMenu(
  _In_ HMENU hMenu,
  _In_ UINT uFlags,
  _In_ int x,
  _In_ int y,
  _In_ int nReserved,
  _In_ HWND hWnd,
  _In_opt_ CONST RECT *prcRect
);

BOOL WINAPI newTrackPopupMenuEx(
  _In_ HMENU hMenu,
  _In_ UINT uFlags,
  _In_ int x,
  _In_ int y,
  _In_ HWND hWnd,
  _In_opt_ LPTPMPARAMS lptpm
);

/*
int WINAPI newDrawTextA(
  _In_     HDC hDC,
  _Inout_  LPCSTR lpchText,
  _In_     int nCount,
  _Inout_  LPRECT lpRect,
  _In_     UINT uFormat
);

//int WINAPI newDrawTextW(
//  _In_    HDC hDC,
//  _Inout_ LPCWSTR lpchText,
//  _In_    int nCount,
//  _Inout_ LPRECT lpRect,
//  _In_    UINT uFormat
//);

int WINAPI newDrawTextExA(
  _In_    HDC hdc,
  _Inout_ LPSTR lpchText,
  _In_    int cchText,
  _Inout_ LPRECT lprc,
  _In_    UINT dwDTFormat,
  _In_    LPDRAWTEXTPARAMS lpDTParams
);

//int WINAPI newDrawTextExW(
//  _In_    HDC hdc,
//  _Inout_ LPWSTR lpchText,
//  _In_    int cchText,
//  _Inout_ LPRECT lprc,
//  _In_    UINT dwDTFormat,
//  _In_    LPDRAWTEXTPARAMS lpDTParams
//);
*/

} // namespace Hijack

// EOF

/*
int WINAPI newMessageBoxA(
  _In_opt_ HWND hWnd,
  _In_opt_ LPCSTR lpText,
  _In_opt_ LPCSTR lpCaption,
  _In_ UINT uType
);
int WINAPI newMessageBoxW(
  _In_ HWND hWnd,
  _In_ LPCWSTR lpText,
  _In_ LPCWSTR lpCaption,
  _In_ UINT uType
);
*/

// - DirectX -

// See: http://stackoverflow.com/questions/1994676/hooking-directx-endscene-from-an-injected-dll
// See: http://www.rohitab.com/discuss/topic/35950-directx9-base-hook/
// See: http://bbs.pediy.com/showthread.php?t=85368
//#include <d3d9.h>
//IDirect3D9* WINAPI newDirect3DCreate9(
//  UINT SDKVersion
//);

/*
HDC WINAPI newGetDC(
  _In_ HWND hWnd
);
HDC WINAPI newGetDCEx(
  _In_ HWND hWnd,
  _In_ HRGN hrgnClip,
  _In_ DWORD flags
);

HDC WINAPI newBeginPaint(
  _In_ HWND hWnd,
  _Out_ LPPAINTSTRUCT lpPaint
);
#include <d3dx9core.h>
//
//INT WINAPI newDrawTextW(
//  _In_ LPD3DXSPRITE pSprite,
//  _In_ LPCWSTR pString,
//  _In_ INT Count,
//  _In_ LPRECT pRect,
//  _In_ DWORD Format,
//  _In_ D3DCOLOR Color
//);

HRESULT newD3DXCreateFontA(
  _In_ LPDIRECT3DDEVICE9 pDevice,
  _In_ INT Height,
  _In_ UINT Width,
  _In_ UINT Weight,
  _In_ UINT MipLevels,
  _In_ BOOL Italic,
  _In_ DWORD CharSet,
  _In_ DWORD OutputPrecision,
  _In_ DWORD Quality,
  _In_ DWORD PitchAndFamily,
  _In_ LPCSTR pFacename,
  _Out_ LPD3DXFONT *ppFont
);

HRESULT newD3DXCreateFontW(
  _In_ LPDIRECT3DDEVICE9 pDevice,
  _In_ INT Height,
  _In_ UINT Width,
  _In_ UINT Weight,
  _In_ UINT MipLevels,
  _In_ BOOL Italic,
  _In_ DWORD CharSet,
  _In_ DWORD OutputPrecision,
  _In_ DWORD Quality,
  _In_ DWORD PitchAndFamily,
  _In_ LPCWSTR pFacename,
  _Out_ LPD3DXFONT *ppFont
);
   { "D3DXCreateFontA", "d3dx9_24.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_24.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_25.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_25.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_26.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_26.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_27.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_27.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_28.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_28.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_29.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_29.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_30.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_30.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_31.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_31.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_32.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_32.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_33.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_33.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_34.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_34.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_35.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_35.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_36.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_36.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_37.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_37.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_38.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_38.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_39.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_39.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_40.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_40.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_41.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_41.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_42.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_42.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9_43.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9_43.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9d_33.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9d_33.dll", newD3DXCreateFontW },
   { "D3DXCreateFontA", "d3dx9d_43.dll", newD3DXCreateFontA },
   { "D3DXCreateFontW", "d3dx9d_43.dll", newD3DXCreateFontW }
*/

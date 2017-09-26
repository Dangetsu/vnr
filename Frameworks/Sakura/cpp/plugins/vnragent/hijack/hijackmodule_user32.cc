// hijackmodule_user32.cc
// 1/27/2013 jichi
#include "hijack/hijackmodule_p.h"
#include "window/windowdriver_p.h"

// FIXME: This function is not thread-safe
BOOL WINAPI Hijack::newTrackPopupMenu(HMENU hMenu, UINT uFlags, int x, int y, int nReserved, HWND hWnd, CONST RECT *prcRect)
{
  //if (HANDLE hThread = CreateThread(0, 0, TranslateMenuThreadProc, hMenu, 0, 0))
  //  CloseHandle(hThread);
  if (auto p = WindowDriverPrivate::instance())
    p->requestUpdateContextMenu(hMenu, hWnd);
  return ::TrackPopupMenu(hMenu, uFlags, x, y, nReserved, hWnd, prcRect);
}

// FIXME: This function is not thread-safe
BOOL WINAPI Hijack::newTrackPopupMenuEx(HMENU hMenu, UINT uFlags, int x, int y, HWND hWnd, LPTPMPARAMS lptpm)
{
  //if (HANDLE hThread = CreateThread(0, 0, TranslateMenuThreadProc, hMenu, 0, 0))
  //  CloseHandle(hThread);
  if (auto p = WindowDriverPrivate::instance())
    p->requestUpdateContextMenu(hMenu, hWnd);
  return ::TrackPopupMenuEx(hMenu, uFlags, x, y, hWnd, lptpm);
}

// - GDI -

// CHECKPOINT
/*
#include "growl.h"
static int i = 0;
BOOL WINAPI newTextOutA(HDC hdc, int nXStart, int nYStart, LPCSTR lpString, int cchString)
{
  //growl::warn(QString("%1, %2").arg(QString::number(nXStart), QString::number(nYStart)));
  int j = i++;
  if (j < 0)
    return true;
  Q_UNUSED(lpString);
  Q_UNUSED(cchString);
  QString s = "Konnichiwa, minasama >_<"; // dividable by 2
  //if (j % 3)
  //  return true;;
  //j /= 3;
  //if (j >= s.size()/2)
  //  return true;
  int index =  j % (s.size()/2);
  QString t = s.mid(index*2, 2);
  return ::TextOutA(hdc, nXStart, nYStart, t.toLocal8Bit(), t.size());
}
*/

//BOOL WINAPI newTextOutW(HDC hdc, int nXStart, int nYStart, LPCWSTR lpString, int cchString)
//{
//  growl::warn("TextOutW");
//  return ::TextOutW(hdc, nXStart, nYStart, lpString, cchString);
//}

// - D3D -

// See: http://stackoverflow.com/questions/1994676/hooking-directx-endscene-from-an-injected-dll
// See: http://www.rohitab.com/discuss/topic/35950-directx9-base-hook/
// See: http://bbs.pediy.com/showthread.php?t=85368
//IDirect3D9* WINAPI newDirect3DCreate9(UINT SDKVersion)
//{
//  growl::warn("d3d");
//  return ::Direct3DCreate9(SDKVersion);
//}

// EOF

/*
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
)
{
  growl::warn(L"message A");
  return ::D3DXCreateFontA(pDevice, Height, Width, Weight, MipLevels, Italic, CharSet, OutputPrecision, Quality, PitchAndFamily, pFacename, ppFont);
}
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
)
{
  growl::warn(L"message W");
  return ::D3DXCreateFontW(pDevice, Height, Width, Weight, MipLevels, Italic, CharSet, OutputPrecision, Quality, PitchAndFamily, pFacename, ppFont);
}

  BOOL CALLBACK EnumThreadWndProc(HWND hWnd, LPARAM params)
  {
    CC_USED(params);

    if (!SupportsWindowClass(hWnd))
      return TRUE;

      if (!strcmp(type, "SysTabControl32")) {
        int changed = 0;
        LRESULT count = SendMessage(hWnd, TCM_GETITEMCOUNT, 0, 0);
        TCITEM item;
        for (int i=0; i<count; i++) {
          item.mask = TCIF_TEXT;
          item.pszText = buffer->text;
          item.cchTextMax = buffer->size;
          if (!SendMessage(hWnd, TCM_GETITEM, i, (LPARAM)&item)) break;
          if (HasJap(buffer->text)) {
            wchar_t *eng = TranslateFullLog(buffer->text);
            if (eng) {
              item.mask = TCIF_TEXT;
              item.pszText = eng;
              SendMessage(hWnd, TCM_SETITEM,  i, (LPARAM)&item);
              changed = 1;
              free(eng);
              buffer->updated = 1;
            }
          }
        }
        if (changed) {
          Sleep(100);
          InvalidateRect(hWnd, 0, 1);
        }
      }
      else if (!strcmp(type, "SysListView32")) {
        int changed = 0;
        for (int i = 0; true; ++i) {
          LVCOLUMN column;
          column.mask = LVCF_TEXT;
          column.pszText = buffer->text;
          column.cchTextMax = buffer->size;
          if (TRUE != ListView_GetColumn(hWnd, i, &column))
            break;
          if (HasJap(buffer->text)) {
            wchar_t *eng = TranslateFullLog(buffer->text);
            if (eng) {
              column.mask = TCIF_TEXT;
              column.pszText = eng;
              ListView_SetColumn(hWnd, i, (LPARAM) &column);
              changed = 1;
              buffer->updated = 1;
              free(eng);
            }
          }
        }
        if (changed) {
          Sleep(100);
          InvalidateRect(hWnd, 0, 1);
        }
      }

    //int top = 0;
    //if (buffer->updated < 0) {
    //  top = 1;
    //  buffer->updated = 0;
    //}

    int len = GetWindowTextLengthW(hWnd);
    if (len > 0) {
      if (buffer->size < len+1) {
        buffer->size = len+150;
        buffer->text = (wchar_t*) realloc(buffer->text, sizeof(wchar_t)*buffer->size);
      }
      if (GetWindowTextW(hWnd, buffer->text, buffer->size)) {
        if (HasJap(buffer->text)) {
          wchar_t *eng = TranslateFullLog(buffer->text);
          if (eng) {
            SetWindowTextW(hWnd, eng);
            buffer->updated = 1;
            if (!strcmp(type, "Static") || !strcmp(type, "Button")) {
              HDC hDC = GetDC(hWnd);
              SIZE s;
              if (hDC) {
                int changed = 0;
                if (GetTextExtentPointW(hDC, eng, wcslen(eng), &s)) {
                  RECT client, window;
                  if (GetClientRect(hWnd, &client) && GetWindowRect(hWnd, &window)) {
                    int wantx = s.cx - client.right;
                    if (wantx < 0) wantx = 0;
                    int wanty = s.cy - client.bottom;
                    if (wanty < 0) wanty = 0;
                    if (wantx || wanty) {
                      HWND hParent = GetParent(hWnd);
                      if (hParent) {
                        FitInfo info;
                        info.hWnd = hWnd;
                        info.r = window;
                        info.target = window;
                        info.target.right += wantx;
                        info.target.bottom += wanty;
                        RECT pRect;
                        GetWindowRect(hParent, &pRect);
                        if (info.target.right >= pRect.right) {
                          info.target.right = pRect.right-5;
                          info.target.bottom = pRect.bottom;
                        }
                        EnumChildWindows(hParent, (WNDENUMPROC)EnumFitWndProc, (LPARAM)&info);
                        SetWindowPos(hWnd, 0, 0, 0, info.target.right-info.target.left, info.target.bottom-info.target.top, SWP_NOACTIVATE | SWP_NOMOVE | SWP_NOOWNERZORDER | SWP_NOZORDER);
                      }
                    }
                  }
                }
                ReleaseDC(hWnd, hDC);
              }
            }
            free(eng);
          }
        }
      }
    }
    HMENU hMenu = GetMenu(hWnd);
    if (hMenu) {
      //if (ProcessMenu(hMenu, buffer)) {
      //  DrawMenuBar(hWnd);
      //}
      MainObject::instance()->addMenu(hWnd);
      MainObject::instance()->update();
    }
    EnumChildWindows(hWnd, (WNDENUMPROC)EnumThreadWndProc, nullptr);
    //if (top) {
    //  if (buffer->updated > 0)
    //    InvalidateRect(hWnd, 0, 1);
    //  buffer->updated = -1;
    //}
    return TRUE;
  }

  // Used to resize buttons/windows. TODO
  struct FitInfo {
    HWND hWnd;
    RECT r;
    RECT target;
  };

  BOOL CALLBACK EnumFitWndProc(HWND hWnd, FitInfo *fit) {
    if (fit->hWnd == hWnd)
      return TRUE;
    RECT r;
    if (!GetWindowRect(hWnd, &r))
      return TRUE;
    // inside the other.
    if (fit->r.right  < r.right  && fit->r.left > r.left &&
      fit->r.bottom < r.bottom && fit->r.top  > r.top) {
        if (fit->target.right > r.right-4) {
          fit->target.right = r.right-4;
        }
        if (fit->target.bottom > r.bottom-4) {
          fit->target.bottom = r.bottom-4;
        }
        return TRUE;
    }
    if (r.left < fit->target.right && r.right > fit->target.left) {
      if (r.bottom > fit->target.top && r.top <= fit->target.bottom) {
        fit->target.bottom = r.top - 1;
        if (fit->target.bottom < fit->r.bottom) {
          fit->target.bottom = fit->r.bottom;
        }
      }
    }
    if (r.top < fit->target.bottom && r.bottom > fit->target.top) {
      if (r.right > fit->target.left && r.left <= fit->target.right) {
        fit->target.right = r.left - 1;
        if (fit->target.right < fit->r.right) {
          fit->target.right = fit->r.right;
        }
      }
    }
    return TRUE;
  }

int WINAPI newMessageBoxA(HWND hWnd, LPCSTR lpText, LPCSTR lpCaption, UINT uType) {
  //int len = -1;
  //wchar_t *uni1 = StringToUnicode(lpText, len);
  //len = -1;
  //wchar_t *uni2 = StringToUnicode(lpCaption, len);
  //int res = newMessageBoxW(hWnd, uni1, uni2, uType);
  //free(uni1);
  //free(uni2);
  //return res;
  return MessageBoxA(hWnd, lpText, lpCaption, uType);
}

int WINAPI newMessageBoxW(HWND hWnd, LPCWSTR lpText, LPCWSTR lpCaption, UINT uType)
{
  //int ret = 0;
  ////if (AtlasIsLoaded()) {
  //if (true) {
  //  wchar_t *uni1 = TranslateFullLog(lpText);
  //  wchar_t *uni2 = TranslateFullLog(lpCaption);
  //  ret = MessageBoxW(hWnd, uni1, uni2, uType);
  //  free(uni1);
  //  free(uni2);
  //} else
  return MessageBoxW(hWnd, lpText, lpCaption, uType);
}
*/

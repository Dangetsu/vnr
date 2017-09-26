// winshell.cc
// 6/13/2013 jichi

#include "winshell/winshell.h"
#include <windows.h>
#include <shlguid.h>
#include <shobjidl.h>

// http://msdn.microsoft.com/en-us/library/windows/desktop/bb776891%28v=vs.85%29.aspx
bool WinShell::resolveLink(const wchar_t *link, wchar_t *buf, int bufsize)
{
  //Q_ASSERT(link);
  //Q_ASSERT(buf);
  //Q_ASSERT(bufsize > 0);
  //buf[0] = L'\0'; // Assume failure

  IShellLink *psl;
  HRESULT hr = ::CoCreateInstance(CLSID_ShellLink, nullptr, CLSCTX_INPROC_SERVER, IID_IShellLink, (void **)&psl);
  if (SUCCEEDED(hr))  {
    IPersistFile *ppf;
    hr = psl->QueryInterface(IID_IPersistFile, (void **)&ppf);
    if (SUCCEEDED(hr))  {
      hr = ppf->Load(link, STGM_READ);
      if (SUCCEEDED(hr))
        //hr = psl->GetPath(buf, bufsize, nullptr, SLGP_SHORTPATH);
        hr = psl->GetPath(buf, bufsize, nullptr, 0);
      ppf->Release();
    }
    psl->Release();
  }

  return SUCCEEDED(hr);
}

// EOF

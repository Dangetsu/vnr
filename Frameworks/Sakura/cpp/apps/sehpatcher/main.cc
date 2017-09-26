// main.cc
// 10/2/2013 jichi
// ITH3/IHF_EnableSEH/EnableSEH.cpp rev 133

#include <windows.h>
#include <cstdio>

namespace { // unnamed

void growl(const wchar_t *msg, const wchar_t *title = nullptr)
{ MessageBoxW(nullptr, msg, title, MB_OK); }

} // unnamed namespace

int main()
{
  BYTE file[0x1000];
  LPWSTR f = wcsrchr(GetCommandLine(), L' ');
  if (f == 0) {
    growl(L"Missing command line parameters");
    return 1;
  }
  f++;

  HANDLE hFile = CreateFile(f,GENERIC_WRITE|GENERIC_READ,FILE_SHARE_READ,0,OPEN_EXISTING,0,0);
  if (hFile == INVALID_HANDLE_VALUE) {
    growl(L"Cannot access file");
    return 1;
  }
  DWORD high;
  DWORD size = GetFileSize(hFile,&high);
  if (high == 0 && size < 0x1000000) {
    DWORD d;
    //char* file=(char*)HeapAlloc(GetProcessHeap(),0, size);
    ReadFile(hFile, file, 0x1000, &d, 0);
    IMAGE_DOS_HEADER *DosHdr = (IMAGE_DOS_HEADER *)file;
    IMAGE_NT_HEADERS *NtHdr = (IMAGE_NT_HEADERS *)((DWORD)DosHdr+DosHdr->e_lfanew);
    if ((BYTE *)&NtHdr->OptionalHeader.DllCharacteristics - file >= 0x1000)
      growl(0, L"Overflow");
    else {
      // 12/3/2013 jichi
      // http://msdn.microsoft.com/en-us/library/windows/desktop/ms680339%28v=vs.85%29.aspx
      // 0xfbff = ~0x400
      // IMAGE_DLLCHARACTERISTICS_NO_SEH = 0x400
      //NtHdr->OptionalHeader.DllCharacteristics &= ~IMAGE_DLLCHARACTERISTICS_NO_SEH;
      NtHdr->OptionalHeader.DllCharacteristics &= 0xfbff;
      SetFilePointer(hFile, 0, 0, FILE_BEGIN);
      WriteFile(hFile, file, 0x1000, &d, 0);
      //growl(0, L"Succeed");
    }
  }

  CloseHandle(hFile);
  return 0;
}

// EOF

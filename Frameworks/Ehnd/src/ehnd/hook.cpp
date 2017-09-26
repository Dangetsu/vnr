#include "stdafx.h"
#include "hook.h"
#include "ehnd.h"

LPBYTE lpfnRetn, lpfnfopen;
LPBYTE lpfnwc2mb, lpfnmb2wc;
LPBYTE lpfnWordInfo;
int wc2mb_type = 0, mb2wc_type = 0;

bool hook()
{
  HMODULE hDll, hDll2;
  TCHAR lpEztPath[MAX_PATH], lpDllPath[MAX_PATH];
  LPCSTR aEztFunction[] = {
    "J2K_Initialize",
    "J2K_InitializeEx",
    "J2K_FreeMem",
    "J2K_GetPriorDict",
    "J2K_GetProperty",
    "J2K_ReloadUserDict",
    "J2K_SetDelJPN",
    "J2K_SetField",
    "J2K_SetHnj2han",
    "J2K_SetJWin",
    "J2K_SetPriorDict",
    "J2K_SetProperty",
    "J2K_StopTranslation",
    "J2K_Terminate",
    "J2K_TranslateChat",
    "J2K_TranslateFM",
    "J2K_TranslateMM",
    "J2K_TranslateMMEx",
    "J2K_TranslateMMNT",
    "?GetJ2KMainDir@@YA?AVCString@@XZ" };
  LPCSTR aMsvFunction[] = {
    "free",
    "malloc",
    "fopen" };
  int i;

  GetLoadPath(lpEztPath, MAX_PATH);

  // jichi 4/4/2015: Dynamically get j2kengine.dlx location
  hDll = GetEztrModule();
  if (!hDll)
  {
    MessageBox(0, L"J2KEngine Load Failed", L"EzTransHook", MB_ICONERROR);
    return false;
  }

  for (i = 0; i < _countof(aEztFunction); i++)
  {
    apfnEzt[i] = GetProcAddress(hDll, aEztFunction[i]);
    if (!apfnEzt[i])
    {
      MessageBox(0, L"J2KEngine Function Load Failed", L"EzTransHook", MB_ICONERROR);
      return false;
    }
  }

  lpDllPath[0] = 0;
  GetSystemDirectory(lpDllPath, MAX_PATH);
  wcscat_s(lpDllPath, L"\\msvcrt.dll");
  hDll2 = LoadLibrary(lpDllPath);
  if (!hDll2)
  {
    MessageBox(0, L"MSVCRT.DLL Load Failed", L"EzTransHook", MB_ICONERROR);
    return false;
  }

  for (i = 0; i < _countof(aMsvFunction); i++)
  {
    apfnMsv[i] = GetProcAddress(hDll2, aMsvFunction[i]);
    if (!apfnMsv[i])
    {
      MessageBox(0, L"MSVCRT.DLL Function Load Failed", L"EzTransHook", MB_ICONERROR);
      return false;
    }
  }

  hEzt = hDll;
  hMsv = hDll2;

  return true;
}

int search_ptn(LPWORD ptn, size_t ptn_size, LPBYTE *addr)
{
  // jichi 4/4/2015: Dynamically get j2kengine.dlx location
  HMODULE hDll = GetEztrModule();
  if (hDll == NULL) MessageBox(0, L"J2KEngine Load Failed", L"", 0);

  MODULEINFO dllInfo;
  GetModuleInformation(GetCurrentProcess(), hDll, &dllInfo, sizeof(dllInfo));

  // Modified BMH - http://en.wikipedia.org/wiki/Boyer-Moore-Horspool_algorithm

  UINT i;
  int scan;
  LPBYTE p;

  UINT defSkipLen;
  UINT skipLen[UCHAR_MAX + 1];
  UINT searchSuccessCount;

  UINT ptnEnd = ptn_size - 1;
  while ((HIBYTE(ptn[ptnEnd]) != 0x00) && (ptnEnd > 0)) {
    ptnEnd--;
  }
  defSkipLen = ptnEnd;
  for (i = 0; i < ptnEnd; i++)
  {
    if (HIBYTE(ptn[i]) != 0x00) {
      defSkipLen = ptnEnd - i;
    }
  }

  for (i = 0; i < UCHAR_MAX + 1; i++)
  {
    skipLen[i] = defSkipLen;
  }

  for (i = 0; i < ptnEnd; i++)
  {
    if (HIBYTE(ptn[i]) == 0x00)
    {
      skipLen[LOBYTE(ptn[i])] = ptnEnd - i;
    }
  }

  searchSuccessCount = 0;
  p = (LPBYTE)dllInfo.lpBaseOfDll;
  LPBYTE searchEnd = (LPBYTE)dllInfo.lpBaseOfDll + dllInfo.SizeOfImage;

  while (p + ptn_size < searchEnd)
  {
    scan = ptnEnd;
    while (scan >= 0)
    {
      if ((HIBYTE(ptn[scan]) == 0x00) && (LOBYTE(ptn[scan]) != p[scan]))
        break;
      if (scan == 0)
      {
        *addr = p;
        searchSuccessCount++;
      }
      scan--;
    }
    p += skipLen[p[ptnEnd]];
  }
  if (searchSuccessCount != 1) addr = 0;
  return searchSuccessCount;
}

bool hook_userdict(void)
{
  WORD ptn[] = { 0x8B, 0x4D, 0x04, 0x03, 0xC1, 0x80, 0x38 };

  LPBYTE addr = 0;
  int r = search_ptn(ptn, _countof(ptn), &addr);

  if (r == 0)
  {
    WriteLog(NORMAL_LOG, L"HookUserDict : J2KEngine Pattern Search Failed\n");
    return false;
  }
  else if (r > 1)
  {
    WriteLog(NORMAL_LOG, L"HookUserDict : J2KEngine Pattern Search Failed\n");
    return false;
  }
  else
  {
    BYTE Patch[] = { 0x90, 0x90, 0x90, 0x90, 0x90, 0xE9, -1, -1, -1, -1, 0x90, 0x90, 0x74, 0x08 };

    int PatchSize = _countof(Patch);
    LPBYTE Offset = (LPBYTE)((LPBYTE)&userdict_patch - (addr + 10));
    lpfnRetn = addr + 10;
    Patch[6] = (WORD)LOBYTE(LOWORD(Offset));
    Patch[7] = (WORD)HIBYTE(LOWORD(Offset));
    Patch[8] = (WORD)LOBYTE(HIWORD(Offset));
    Patch[9] = (WORD)HIBYTE(HIWORD(Offset));

    DWORD OldProtect, OldProtect2;
    HANDLE hHandle;
    hHandle = OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, FALSE, GetCurrentProcessId());
    VirtualProtectEx(hHandle, (void *)addr, PatchSize, PAGE_EXECUTE_READWRITE, &OldProtect);
    memcpy(addr, Patch, PatchSize);
    hHandle = OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, FALSE, GetCurrentProcessId());
    VirtualProtectEx(hHandle, (void *)addr, PatchSize, OldProtect, &OldProtect2);
    WriteLog(NORMAL_LOG, L"HookUserDict : Success.\n");
  }

  return true;
}

bool hook_userdict2(void)
{
  // 101C4B00 . 8B43 14        MOV EAX,DWORD PTR DS:[EBX+14]
  // 101C4B03 . 8B3D A4192A10  MOV EDI,DWORD PTR DS:[<&MSVCRT.fopen>]   ;  msvcrt.fopen << intercept here
  // 101C4B09 . 68 60982110    PUSH J2KEngin.10219860                   ; /mode = "rb"
  // 101C4B0E . 50             PUSH EAX                                 ; |path
  // 101C4B0F . FFD7           CALL EDI                                 ; \fopen
  // 101C4B11 . 8BF0           MOV ESI,EAX

  WORD ptn[] = { 0x8B, 0x43, 0x14, 0x8B, 0x3D, -1, -1, -1, -1, 0x68, -1, -1, -1, -1, 0x50, 0xFF, 0xD7, 0x8B, 0xF0 };

  LPBYTE addr = 0;
  int r = search_ptn(ptn, _countof(ptn), &addr);

  if (r == 0)
  {
    WriteLog(NORMAL_LOG, L"HookUserDict2 : J2KEngine Pattern Search Failed\n");
    return false;
  }
  else if (r > 1)
  {
    WriteLog(NORMAL_LOG, L"HookUserDict2 : J2kEngine Pattern Search Failed\n");
    return false;
  }
  else
  {
    addr += 5;
    BYTE Patch[4];
    int PatchSize = _countof(Patch);
    lpfnfopen = (LPBYTE)(fopen_patch);
    Patch[0] = (WORD)LOBYTE(LOWORD(&lpfnfopen));
    Patch[1] = (WORD)HIBYTE(LOWORD(&lpfnfopen));
    Patch[2] = (WORD)LOBYTE(HIWORD(&lpfnfopen));
    Patch[3] = (WORD)HIBYTE(HIWORD(&lpfnfopen));

    DWORD OldProtect, OldProtect2;
    HANDLE hHandle;
    hHandle = OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, FALSE, GetCurrentProcessId());
    VirtualProtectEx(hHandle, (void *)addr, PatchSize, PAGE_EXECUTE_READWRITE, &OldProtect);
    memcpy(addr, Patch, PatchSize);
    hHandle = OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, FALSE, GetCurrentProcessId());
    VirtualProtectEx(hHandle, (void *)addr, PatchSize, OldProtect, &OldProtect2);

    WriteLog(NORMAL_LOG, L"HookUserDict2 : Success.\n");
  }

  return true;
}

bool hook_getwordinfo(void)
{
  /*
  05BBF270    6A FF           PUSH -1
  05BBF272    68 1B59BF05     PUSH j2keng_1.05BF591B
  05BBF277    64:A1 00000000  MOV EAX,DWORD PTR FS:[0]
  05BBF27D    50              PUSH EAX
  05BBF27E    64:8925 0000000>MOV DWORD PTR FS:[0],ESP
  05BBF285    83EC 18         SUB ESP,18
  05BBF288    53              PUSH EBX
  05BBF289    8B5C24 30       MOV EBX,DWORD PTR SS:[ESP+30]
  05BBF28D    55              PUSH EBP
  05BBF28E    56              PUSH ESI
  05BBF28F    8B7424 34       MOV ESI,DWORD PTR SS:[ESP+34]
  05BBF293    57              PUSH EDI
  05BBF294    8D4424 18       LEA EAX,DWORD PTR SS:[ESP+18]
  05BBF298    8BF9            MOV EDI,ECX
  05BBF29A    50              PUSH EAX
  05BBF29B    51              PUSH ECX
  05BBF29C    33ED            XOR EBP,EBP
  05BBF29E    8BCC            MOV ECX,ESP
  05BBF2A0    896424 2C       MOV DWORD PTR SS:[ESP+2C],ESP
  05BBF2A4    56              PUSH ESI
  05BBF2A5    897C24 28       MOV DWORD PTR SS:[ESP+28],EDI
  05BBF2A9    892B            MOV DWORD PTR DS:[EBX],EBP
  05BBF2AB    896C24 24       MOV DWORD PTR SS:[ESP+24],EBP
  */

  WORD ptn[] = { 0x6A, 0xFF, 0x68, -1, -1, -1, -1, 0x64, 0xA1, 0x00, 0x00, 0x00, 0x00,
           0x50, 0x64, 0x89, 0x25, 0x00, 0x00, 0x00, 0x00, 0x83, 0xEC, 0x18,
           0x53, 0x8B, 0x5C, 0x24, 0x30, 0x55, 0x56};

  LPBYTE addr = 0;
  int r = search_ptn(ptn, _countof(ptn), &addr);

  if (r == 0)
  {
    WriteLog(NORMAL_LOG, L"HookGetWordInfo : J2KEngine Pattern Search Failed\n");
    return false;
  }
  else if (r > 1)
  {
    WriteLog(NORMAL_LOG, L"HookGetWordInfo : J2kEngine Pattern Search Failed\n");
    return false;
  }
  else
  {
    lpfnWordInfo = addr;
    BYTE Patch[5];
    int PatchSize = 2;
    Patch[0] = 0xEB;
    Patch[1] = 0x05;
    //Patch[2] = (WORD)LOBYTE(HIWORD(&lpfnWordInfo));
    //Patch[3] = (WORD)HIBYTE(HIWORD(&lpfnWordInfo));

    DWORD OldProtect, OldProtect2;
    HANDLE hHandle;
    hHandle = OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, FALSE, GetCurrentProcessId());
    VirtualProtectEx(hHandle, (void *)addr, PatchSize, PAGE_EXECUTE_READWRITE, &OldProtect);
    memcpy(addr, Patch, PatchSize);
    hHandle = OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, FALSE, GetCurrentProcessId());
    VirtualProtectEx(hHandle, (void *)addr, PatchSize, OldProtect, &OldProtect2);

    // 0x07
    PatchSize = 5;
    addr += 7;

    Patch[0] = 0xE9;
    LPBYTE Offset = (LPBYTE)((LPBYTE)&user_wordinfo - (addr + 5));
    Patch[1] = (WORD)LOBYTE(LOWORD(Offset));
    Patch[2] = (WORD)HIBYTE(LOWORD(Offset));
    Patch[3] = (WORD)LOBYTE(HIWORD(Offset));
    Patch[4] = (WORD)HIBYTE(HIWORD(Offset));

    hHandle = OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, FALSE, GetCurrentProcessId());
    VirtualProtectEx(hHandle, (void *)addr, PatchSize, PAGE_EXECUTE_READWRITE, &OldProtect);
    memcpy(addr, Patch, PatchSize);
    hHandle = OpenProcess(PROCESS_VM_OPERATION | PROCESS_VM_READ | PROCESS_VM_WRITE, FALSE, GetCurrentProcessId());
    VirtualProtectEx(hHandle, (void *)addr, PatchSize, OldProtect, &OldProtect2);

    // 0x0D

    WriteLog(NORMAL_LOG, L"HookWordInfo : Success.\n");
  }

  return true;
}

bool GetRealWC2MB(void)
{
  HMODULE hDll = GetModuleHandle(L"kernel32.dll");
  lpfnwc2mb = (LPBYTE)GetProcAddress(hDll, "WideCharToMultiByte");

  // KERNEL32 HOOK
  // 756770D0 >  8BFF            MOV EDI, EDI
  // 756770D2    55              PUSH EBP
  // 756770D3    8BEC            MOV EBP, ESP

  BOOL bMatch = true;
  WORD ptn_kernel32[] = { 0x8B, 0xFF, 0x55, 0x8B, 0xEC, 0x5D };

  for (int i = 0; i < _countof(ptn_kernel32); i++)
    if (*(lpfnwc2mb + i) != ptn_kernel32[i])
    {
      bMatch = false;
      break;
    }

  if (bMatch)
  {
    lpfnwc2mb += 6;
    wc2mb_type = 1;
    return true;
  }

  // AILAYER HOOK
  // 230083D2    55              PUSH EBP
  // 230083D3    8BEC            MOV EBP, ESP
  // 230083D5    833D A8360123 0>CMP DWORD PTR DS : [230136A8], 0
  // 230083DC    74 11           JE SHORT AlLayer.230083EF
  // 230083DE    817D 08 E9FD000>CMP DWORD PTR SS : [EBP + 8], 0FDE9
  // 230083E5    74 08           JE SHORT AlLayer.230083EF


  bMatch = true;
  WORD ptn_ailayer[] = { 0x55, 0x8B, 0xEC, 0x83, 0x3D };

  for (int i = 0; i < _countof(ptn_ailayer); i++)
    if (*(lpfnwc2mb + i) != ptn_ailayer[i])
    {
      bMatch = false;
      break;
    }

  if (bMatch)
  {
    if (*(lpfnwc2mb + 0x1E) == 0xA1)
    {
      LPBYTE l1, l2, l3;
      char *p = (char *)&l1;
      for (int i = 0; i < 4; i++)
        p[i] = *(lpfnwc2mb + 0x1F + i);
      p = (char *)&l2;
      for (int i = 0; i < 4; i++)
        p[i] = *(l1 + i);
      l2 += 0x15C;
      p = (char *)&l3;
      for (int i = 0; i < 4; i++)
        p[i] = *(l2 + i);

      bMatch = true;
      for (int i = 0; i < _countof(ptn_kernel32); i++)
        if (*(l3 + i) != ptn_kernel32[i])
        {
          bMatch = false;
          break;
        }

      if (bMatch)
      {
        lpfnwc2mb = l3 + 6;
        wc2mb_type = 1;
        WriteLog(NORMAL_LOG, L"lpfnwc2mb: %x\n", lpfnwc2mb);
        return true;
      }
    }
  }
  return true;
}

bool GetRealMB2WC(void)
{
  HMODULE hDll = GetModuleHandle(L"kernel32.dll");
  lpfnmb2wc = (LPBYTE)GetProcAddress(hDll, "MultiByteToWideChar");

  // KERNEL32 HOOK
  // 756770D0 >  8BFF            MOV EDI, EDI
  // 756770D2    55              PUSH EBP
  // 756770D3    8BEC            MOV EBP, ESP

  BOOL bMatch = true;
  WORD ptn_kernel32[] = { 0x8B, 0xFF, 0x55, 0x8B, 0xEC, 0x5D };

  for (int i = 0; i < _countof(ptn_kernel32); i++)
    if (*(lpfnmb2wc + i) != ptn_kernel32[i])
    {
      bMatch = false;
      break;
    }

  if (bMatch)
  {
    lpfnmb2wc += 6;
    mb2wc_type = 1;
    return true;
  }

  // AILAYER HOOK
  // 230083D2    55              PUSH EBP
  // 230083D3    8BEC            MOV EBP, ESP
  // 230083D5    833D A8360123 0>CMP DWORD PTR DS : [230136A8], 0
  // 230083DC    74 11           JE SHORT AlLayer.230083EF
  // 230083DE    817D 08 E9FD000>CMP DWORD PTR SS : [EBP + 8], 0FDE9
  // 230083E5    74 08           JE SHORT AlLayer.230083EF

  bMatch = true;
  WORD ptn_ailayer[] = { 0x55, 0x8B, 0xEC, 0x83, 0x3D };

  for (int i = 0; i < _countof(ptn_ailayer); i++)
    if (*(lpfnmb2wc + i) != ptn_ailayer[i])
    {
      bMatch = false;
      break;
    }

  if (bMatch)
  {
    if (*(lpfnmb2wc + 0x40) == 0xA1)
    {
      LPBYTE l1, l2, l3;
      char *p = (char*)&l1;
      for (int i = 0; i < 4; i++)
        p[i] = *(lpfnmb2wc + 0x41 + i);
      p = (char*)&l2;
      for (int i = 0; i < 4; i++)
        p[i] = *(l1 + i);
      l2 += 0x144;
      p = (char*)&l3;
      for (int i = 0; i < 4; i++)
        p[i] = *(l2 + i);

      bMatch = true;
      for (int i = 0; i < _countof(ptn_kernel32); i++)
        if (*(l3 + i) != ptn_kernel32[i])
        {
          bMatch = false;
          break;
        }

      if (bMatch)
      {
        lpfnmb2wc = l3 + 6;
        mb2wc_type = 1;
        WriteLog(NORMAL_LOG, L"lpfnlpfnmb2wc: %x\n", lpfnmb2wc);
        return true;
      }
    }
  }
  return true;
}

__declspec(naked) int __stdcall _WideCharToMultiByte(UINT a, DWORD b, LPCWSTR c, int d, LPSTR e, int f, LPCSTR g, LPBOOL h)
{
  if (wc2mb_type == 1)
  {
    __asm
    {
      MOV EDI, EDI // kernelbase
      PUSH EBP
      MOV EBP, ESP
      POP EBP
    }
  }
  __asm JMP lpfnwc2mb
}

__declspec(naked) int __stdcall _MultiByteToWideChar(UINT a, DWORD b, LPCSTR c, int d, LPWSTR e, int f)
{
  if (mb2wc_type == 1)
  {
    __asm
    {
      MOV EDI, EDI // kernelbase
      PUSH EBP
      MOV EBP, ESP
      POP EBP
    }
  }
  __asm JMP lpfnmb2wc
}

void *fopen_patch(char *path, char *mode)
{
  if (strstr(path, "UserDict.jk"))
  {
    path = g_DicPath;
    //WriteLog(NORMAL_LOG, L"fopen_path\n");
  }
  return msvcrt_fopen(path, mode);
}

__declspec(naked) void userdict_patch(void)
{

  // binary search (lower bound)
  // [ESP + 0x10]  // current addr (start)
  // [ESP + 0x18]  // current count (end)
  // [EBP + 0x08]  // total count
  // [ESP + 0x38] // word_string
  //
  // [EBP + 0x04] + 0x6E * cnt + 0x01 = USERDICT_JPN
  //

  // UserDic이 켜져있는지 확인. 꺼져있으면 처리를 하지 않는다
  __asm
  {
    CALL userdict_check
    CMP AL, 0
    JE lFinish
  }

  // 일치하는 단어가 나오면 단어 등록을 하고 다시 돌아옴
  __asm
  {
    PUSH DWORD PTR SS : [EBP+0x08] // total count
    PUSH DWORD PTR SS : [ESP+0x1C] // current_count
    PUSH DWORD PTR SS : [EBP+0x04] // base
    PUSH DWORD PTR SS : [ESP+0x44] // word_str
    CALL userdict_proc
    ADD ESP, 0x10

    CMP EAX, DWORD PTR SS : [EBP+0x08]
    JA lFinish

    // word_string 출력
    // ESP+0x14를 count용으로 사용
    // count는 자동으로 올라가니 건들 필요가 없다
    CMP DWORD PTR SS : [ESP+0x18], 0
    JNZ lNext

    PUSH EAX
    PUSH DWORD PTR SS : [ESP+0x3C]
    CALL userdict_log
    ADD ESP, 0x04
    POP EAX

  lNext:

    // addr=base+point*0x6E
    MOV DWORD PTR SS : [ESP+0x18], EAX
    MOV ECX, 0x6E
    MUL ECX
    MOV DWORD PTR SS : [ESP+0x10], EAX
    ADD EAX, DWORD PTR SS : [EBP+0x04]
    PUSH EAX
    ADD EAX, 0x6A
    PUSH DWORD PTR SS : [ESP+0x18] // ESP+0x14 + 0x04
    PUSH DWORD PTR DS : [EAX]
    CALL userdict_log2
    ADD ESP, 0x08
    POP EAX
    MOV CL, 1
    TEST CL, CL
    JMP lpfnRetn
  lFinish:
    MOV EDX, DWORD PTR SS : [EBP+0x08]
    MOV DWORD PTR SS : [ESP+0x18], EDX
    MOV EBX, DWORD PTR SS:[ESP+0x38]
    MOV CL, 0
    TEST CL, CL
    JMP lpfnRetn
  }
}

__declspec(naked) void user_wordinfo()
{
  __asm
  {
    MOV EAX, lpfnWordInfo
    ADD EAX, 0x03
    PUSH -1
    PUSH DWORD PTR DS:[EAX]
    MOV EAX, DWORD PTR DS : [lpfnWordInfo]
    ADD EAX, 0x0D
    PUSH EAX
    MOV EAX, DWORD PTR FS : [0]
    RETN
  }
}

void userdict_log(char *s)
{
  int len;
  len = _MultiByteToWideChar(932, MB_PRECOMPOSED, s, -1, NULL, NULL);
  wchar_t *str = (wchar_t *)msvcrt_malloc((len + 1) * 2);
  _MultiByteToWideChar(932, 0, s, -1, str, len);

  WriteLog(USERDIC_LOG, L"UserDic_Req : %s\n", str);
  msvcrt_free(str);
}

void userdict_log2(int idx, int num)
{
  WriteLog(USERDIC_LOG, L"UserDic (%d) : [%s:%d] %s | %s | (%s) | %s\n", num+1, pFilter->GetDicDB(idx), pFilter->GetDicLine(idx),
    pFilter->GetDicJPN(idx), pFilter->GetDicKOR(idx), pFilter->GetDicTYPE(idx), pFilter->GetDicATTR(idx));
}
bool userdict_check()
{
  return pConfig->GetUserDicSwitch();
}
inline unsigned int userdict_calhash(const char *str, int count)
{
  unsigned int hash = 5381;
  int c = 0;
  int i = 0;

  while (c = *str++)
  {
    hash = ((hash << 5) + hash) + c;
    i++;
    if (i == count) break;
  }

  return (hash & 0x7FFFFFFF);
}
inline bool userdict_compare(const char *src, const char *dest, int len)
{
  return (userdict_calhash(src, len) == userdict_calhash(dest, len));
}
int userdict_proc(char *word_str, char *base, int cur, int total)
{
  int idx = -1;
  int s = cur, e = total, m, min, max;
  char *dic_str;

  // Upper bound로 최대값 산출
  while (e - s > 0)
  {
    m = (s + e) / 2;
    dic_str = (char *)base + (0x6E * m) + 0x01;

    if (word_str[0] <= dic_str[0])
      s = m + 1;
    else e = m;
  }
  max = s;

  // Lower bound로 최소값 산출
  s = cur, e = max;
  while (e - s > 0)
  {
    m = (s + e) / 2;
    dic_str = (char *)base + (0x6E * m) + 0x01;

    if (word_str[0] < dic_str[0])
      s = m + 1;
    else e = m;
  }
  min = s;

  for (int i = min; i < max; i++)
  {
    dic_str = (char *)base + (0x6E * i) + 0x01;

    if (userdict_compare(dic_str, word_str, strlen(dic_str)) &&
      !strncmp(word_str, dic_str, strlen(dic_str)))
      return i;
  }
  return total + 1;
}

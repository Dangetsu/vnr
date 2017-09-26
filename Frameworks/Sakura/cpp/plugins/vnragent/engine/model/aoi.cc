// aoi.cc
// 6/6/2015 jichi
#include "engine/model/aoi.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
#include "hijack/hijackmanager.h"
#include "memdbg/memsearch.h"
#include "winhook/hookcode.h"
#include <qt_windows.h>
#include <boost/foreach.hpp>
#include <cstdint>

#define DEBUG "model/aoi"
#include "sakurakit/skdebug.h"

namespace { // unnamed

// Helper functions

/**
 * @param  hModule
 * @param  functionName  original function name without name hashing
 * @param  minParamNum  minimum number of parameters
 * @param  maxParamNum  maximum number of parameters
 * @return  address of the procedure or 0
 */
ulong findCppProc(HMODULE hModule, LPCSTR functionName, int minParamNum = 0, int maxParamNum = 10)
{
  for (int i = minParamNum; i < maxParamNum; i++) {
    std::string sig; // function signature name, such as _AgsSpriteCreateText@20
    sig.push_back('_');
    sig += functionName;
    sig.push_back('@');
    sig += std::to_string(4ll * i);
    if (auto proc = ::GetProcAddress(hModule, sig.c_str()))
      return (ulong)proc;
  }
  return 0;
}

namespace AgsHookW {
namespace Private {

  template<typename wstrT>
  wstrT ltrimW(wstrT text)
  {
    static const char *quotes[] = { "<>", "[]" }; // skip leading quotes
    BOOST_FOREACH (const char *q, quotes)
      while (text[0] == q[0]) {
        if (auto p = ::wcschr(text, q[1])) {
          text = p + 1;
          if (*text == 0x3000) // skip \u3000 leading space
            text++;
        } else
          break;
      }
    return text;
  }

  /**
   *  Sample game:
   *  - 悪魔娘の看板料理: _AgsSpriteCreateText@20
   *  - BunnyBlack2: _AgsSpriteCreateText@24
   *
   *  - arg1: text address in heap, which can be directly overwritten
   *  - arg2: split
   *  - arg3:
   *  - arg4:
   *
   *  Sample text:
   *  [f9S30e0u]　が、それは人間相手の話だ。
   */
  bool beforeAgsSpriteCreateTextW(winhook::hook_stack *s)
  {
    // All threads including character names are linked together

    auto text = (LPWSTR)s->stack[1]; // arg1
    if (!text || !*text || !Engine::isAddressWritable(text)) // skip modifying readonly text in code region
      return true;

    bool containsTags = ::wcsstr(text, L"[u]");

    text = ltrimW(text);
    if (!*text)
      return true;

    int role = Engine::OtherRole;
    //ulong split = s->stack[0]; // retaddr
    ulong split = s->stack[2]; // arg2
    if (!containsTags)
      switch (split) {
      case 0x63a1:
        role = Engine::NameRole;
        break;
      case 0x639e:
          role = Engine::ScenarioRole;
        break;
      }
    auto sig = Engine::hashThreadSignature(role, split);

    QString oldText = QString::fromWCharArray(text),
            newText = EngineController::instance()->dispatchTextW(oldText, role, sig);
    if (newText == oldText)
      return true;
    text[newText.size()] = 0;
    if (!newText.isEmpty())
      newText.toWCharArray(text);
    return true;
  }

  bool beforeAgsSpriteCreateTextExW(winhook::hook_stack *s)
  {
    auto text = (LPWSTR)s->stack[2]; // arg2
    if (!text || !*text || !Engine::isAddressWritable(text))
      return true;

    text = ltrimW(text);
    if (!*text)
      return true;

    enum { role = Engine::OtherRole };
    ulong split = s->stack[0]; // retaddr
    auto sig = Engine::hashThreadSignature(role, split);

    QString oldText = QString::fromWCharArray(text),
            newText = EngineController::instance()->dispatchTextW(oldText, role, sig);
    if (newText == oldText)
      return true;
    text[newText.size()] = 0;
    if (!newText.isEmpty())
      newText.toWCharArray(text);
    return true;
  }

} // namespace Private

bool attach(HMODULE hModule) // attach scenario
{
  ulong addr = findCppProc(hModule, "AgsSpriteCreateText", 1);
  if (!addr || !winhook::hook_before(addr, Private::beforeAgsSpriteCreateTextW))
    return false;
  if (addr = findCppProc(hModule, "AgsSpriteCreateTextEx", 1))
    winhook::hook_before(addr, Private::beforeAgsSpriteCreateTextExW);
  return true;
}

} // namespace AgsHookW

namespace AgsHookA {
namespace Private {

  template<typename wstrT>
  wstrT ltrimA(wstrT text)
  {
    static const char *quotes[] = { "<>", "[]" }; // skip leading quotes
    BOOST_FOREACH (const char *q, quotes)
      while (text[0] == q[0]) {
        if (auto p = ::strchr(text, q[1])) {
          text = p + 1;
          if ((uchar)text[0] == 0x81 && (uchar)text[1] == 0x40) // skip \u3000 leading space, assuming sjis encoding
            text += 2;
        } else
          break;
      }
    return text;
  }

  /**
   *  Sample game: 王賊
   *  _AgsSpriteCreateText@24 0x100108b0 0x000108b0 97 (0x61) Ags.dll Z:\Local\Windows\Games\SystemAoi\kingT\Ags.dll Exported Function
   *
   *  - arg1: text address in heap, which can be directly overwritten
   *  - arg2: split
   *  - arg3:
   *  - arg4:
   *
   *  Sample text:
   *  <s6e0u>八重
   *  <s6e0u>　ソフトホウスキャラ最新
   */
  bool beforeAgsSpriteCreateTextA(winhook::hook_stack *s)
  {
    // All threads including character names are linked together

    auto text = (LPSTR)s->stack[1]; // arg1
    if (!text || !*text || !Engine::isAddressWritable(text)) // skip modifying readonly text in code region
      return true;

    bool containsTags = ::strstr(text, "[u]");

    text = ltrimA(text);
    if (!*text)
      return true;

    int role = Engine::OtherRole;
    //ulong split = s->stack[0]; // retaddr
    ulong split = s->stack[2]; // arg2
    if (!containsTags)
      switch (split) {
      case 0x639d:
        role = Engine::NameRole;
        break;
      case 0x639c:
          role = Engine::ScenarioRole;
        break;
      }
    auto sig = Engine::hashThreadSignature(role, split);
    QByteArray data = EngineController::instance()->dispatchTextA(text, role, sig);
    ::strcpy(text, data.constData());
    return true;
  }

} // namespace Private

bool attach(HMODULE hModule) // attach scenario
{
  ulong addr = findCppProc(hModule, "AgsSpriteCreateText", 1);
  return addr && winhook::hook_before(addr, Private::beforeAgsSpriteCreateTextA);
}

} // namespace AgsHookA

namespace AgsPatchA {
namespace Private {

  struct HookArgument {
    ulong unknown[13]; // + 0x34
    LPCSTR text;
  };
  HookArgument *arg_;
  LPCSTR text_;

  bool hookBefore(winhook::hook_stack *s)
  {
    LPCSTR src = (LPCSTR)s->stack[6]; // original text in arg7
    //LPSTR dest = *(LPSTR *)(s->stack[0] + 0x34); // bad text in arg1+0x34
    arg_ = (HookArgument *)s->stack[0];
    text_ = arg_->text;
    arg_->text = src;
    return true;
  }

  bool hookAfter(winhook::hook_stack *)
  {
    if (arg_) {
      arg_->text = text_;
      arg_ = nullptr;
    }
    return true;
  }

} // namespace Private

/**
 *  Sample game: 王賊
 *
 *  Prevent Aoi engine from modifying illegal characters.
 *
 *  Function found by hijack DrawTextExA.
 *
 *  100173BD   CC               INT3
 *  100173BE   CC               INT3
 *  100173BF   CC               INT3
 *  100173C0   83EC 28          SUB ESP,0x28
 *  100173C3   53               PUSH EBX
 *  100173C4   33DB             XOR EBX,EBX
 *  100173C6   55               PUSH EBP
 *  100173C7   8B6C24 34        MOV EBP,DWORD PTR SS:[ESP+0x34]
 *  100173CB   56               PUSH ESI
 *  100173CC   57               PUSH EDI
 *  100173CD   8BF8             MOV EDI,EAX
 *  100173CF   C745 30 18000000 MOV DWORD PTR SS:[EBP+0x30],0x18
 *  100173D6   381F             CMP BYTE PTR DS:[EDI],BL
 *  100173D8   895C24 28        MOV DWORD PTR SS:[ESP+0x28],EBX
 *  100173DC   C74424 2C FFFFFF>MOV DWORD PTR SS:[ESP+0x2C],0x7FFFFFFF
 *  100173E4   895C24 1C        MOV DWORD PTR SS:[ESP+0x1C],EBX
 *  100173E8   895C24 20        MOV DWORD PTR SS:[ESP+0x20],EBX
 *  100173EC   895C24 30        MOV DWORD PTR SS:[ESP+0x30],EBX
 *  100173F0   895C24 34        MOV DWORD PTR SS:[ESP+0x34],EBX
 *  100173F4   895C24 24        MOV DWORD PTR SS:[ESP+0x24],EBX
 *  100173F8   895C24 14        MOV DWORD PTR SS:[ESP+0x14],EBX
 *  100173FC   895C24 18        MOV DWORD PTR SS:[ESP+0x18],EBX
 *  10017400   8BF7             MOV ESI,EDI
 *  10017402   74 12            JE SHORT Ags.10017416
 *  10017404   56               PUSH ESI
 *  10017405   FF15 90A00210    CALL DWORD PTR DS:[<&AoiLib._AoiString2B>; AoiLib._AoiString2ByteIs@4
 *  1001740B   85C0             TEST EAX,EAX
 *  1001740D   74 7D            JE SHORT Ags.1001748C
 *  1001740F   83C6 02          ADD ESI,0x2
 *  10017412   381E             CMP BYTE PTR DS:[ESI],BL
 *  10017414  ^75 EE            JNZ SHORT Ags.10017404
 *  10017416   57               PUSH EDI
 *  10017417   FF15 94A00210    CALL DWORD PTR DS:[<&AoiLib._AoiStrlen@4>; AoiLib._AoiStrlen@4
 *  1001741D   8BC8             MOV ECX,EAX
 *  1001741F   83C1 02          ADD ECX,0x2
 *  10017422   395C24 1C        CMP DWORD PTR SS:[ESP+0x1C],EBX
 *  10017426   74 0C            JE SHORT Ags.10017434
 *  10017428   8BC1             MOV EAX,ECX
 *  1001742A   33D2             XOR EDX,EDX
 *  1001742C   F77424 2C        DIV DWORD PTR SS:[ESP+0x2C]
 *  10017430   8D4C01 01        LEA ECX,DWORD PTR DS:[ECX+EAX+0x1]
 *  10017434   395C24 28        CMP DWORD PTR SS:[ESP+0x28],EBX
 *  10017438   74 07            JE SHORT Ags.10017441
 *  1001743A   8B4424 24        MOV EAX,DWORD PTR SS:[ESP+0x24]
 *  1001743E   8D0C41           LEA ECX,DWORD PTR DS:[ECX+EAX*2]
 *  10017441   51               PUSH ECX
 *  10017442   FF15 18A00210    CALL DWORD PTR DS:[<&AoiLib._AoiMemoryAl>; AoiLib._AoiMemoryAlloc@4
 *  10017448   8945 34          MOV DWORD PTR SS:[EBP+0x34],EAX
 *  1001744B   381F             CMP BYTE PTR DS:[EDI],BL
 *  1001744D   8BF0             MOV ESI,EAX
 *  1001744F   0F84 6C020000    JE Ags.100176C1
 *  10017455   8B2D 50A10210    MOV EBP,DWORD PTR DS:[<&AoiLib._AoiStrin>; AoiLib._AoiString1to2Byte@8
 *  1001745B   EB 03            JMP SHORT Ags.10017460
 *  1001745D   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  10017460   57               PUSH EDI
 *  10017461   FF15 90A00210    CALL DWORD PTR DS:[<&AoiLib._AoiString2B>; AoiLib._AoiString2ByteIs@4
 *  10017467   85C0             TEST EAX,EAX
 *  10017469   0F84 99010000    JE Ags.10017608
 *  1001746F   8A0F             MOV CL,BYTE PTR DS:[EDI]
 *  10017471   880E             MOV BYTE PTR DS:[ESI],CL
 *  10017473   8A57 01          MOV DL,BYTE PTR DS:[EDI+0x1]
 *  10017476   83C7 01          ADD EDI,0x1
 *  10017479   83C6 01          ADD ESI,0x1
 *  1001747C   8816             MOV BYTE PTR DS:[ESI],DL
 *  1001747E   83C6 01          ADD ESI,0x1
 *  10017481   83C7 01          ADD EDI,0x1
 *  10017484   83C3 02          ADD EBX,0x2
 *  10017487   E9 F8010000      JMP Ags.10017684
 *  1001748C   803E 3C          CMP BYTE PTR DS:[ESI],0x3C
 *  1001748F   74 0D            JE SHORT Ags.1001749E
 *  10017491   83C6 01          ADD ESI,0x1
 *  10017494   834424 24 01     ADD DWORD PTR SS:[ESP+0x24],0x1
 *  10017499  ^E9 74FFFFFF      JMP Ags.10017412
 *  1001749E   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
 *  100174A1   83C6 01          ADD ESI,0x1
 *  100174A4   84C0             TEST AL,AL
 *  100174A6  ^0F84 6AFFFFFF    JE Ags.10017416
 *  100174AC   8D6424 00        LEA ESP,DWORD PTR SS:[ESP]
 *  100174B0   3C 3E            CMP AL,0x3E
 *  100174B2  ^0F84 5AFFFFFF    JE Ags.10017412
 *  100174B8   0FBEC0           MOVSX EAX,AL
 *  100174BB   83C0 B5          ADD EAX,-0x4B
 *  100174BE   83F8 2A          CMP EAX,0x2A
 *  100174C1   77 52            JA SHORT Ags.10017515
 *  100174C3   0FB680 70770110  MOVZX EAX,BYTE PTR DS:[EAX+0x10017770]
 *  100174CA   FF2485 50770110  JMP DWORD PTR DS:[EAX*4+0x10017750]
 *  100174D1   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
 *  100174D4   83C6 01          ADD ESI,0x1
 *  100174D7   33C9             XOR ECX,ECX
 *  100174D9   3C 30            CMP AL,0x30
 *  100174DB   7C 1A            JL SHORT Ags.100174F7
 *  100174DD   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  100174E0   3C 39            CMP AL,0x39
 *  100174E2   7F 13            JG SHORT Ags.100174F7
 *  100174E4   83C6 01          ADD ESI,0x1
 *  100174E7   0FBED0           MOVSX EDX,AL
 *  100174EA   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  100174EC   3C 30            CMP AL,0x30
 *  100174EE   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
 *  100174F1   8D4C4A D0        LEA ECX,DWORD PTR DS:[EDX+ECX*2-0x30]
 *  100174F5  ^7D E9            JGE SHORT Ags.100174E0
 *  100174F7   6A 0A            PUSH 0xA
 *  100174F9   53               PUSH EBX
 *  100174FA   51               PUSH ECX
 *  100174FB   FF15 88A00210    CALL DWORD PTR DS:[<&AoiLib._AoiMathLimi>; AoiLib._AoiMathLimit@12
 *  10017501   8B0485 08CB0210  MOV EAX,DWORD PTR DS:[EAX*4+0x1002CB08]
 *  10017508   8945 30          MOV DWORD PTR SS:[EBP+0x30],EAX
 *  1001750B   EB 0B            JMP SHORT Ags.10017518
 *  1001750D   C74424 28 010000>MOV DWORD PTR SS:[ESP+0x28],0x1
 *  10017515   83C6 01          ADD ESI,0x1
 *  10017518   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  1001751A   84C0             TEST AL,AL
 *  1001751C  ^75 92            JNZ SHORT Ags.100174B0
 *  1001751E  ^E9 F3FEFFFF      JMP Ags.10017416
 *  10017523   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
 *  10017526   83C6 01          ADD ESI,0x1
 *  10017529   33C9             XOR ECX,ECX
 *  1001752B   3C 30            CMP AL,0x30
 *  1001752D   C74424 1C 010000>MOV DWORD PTR SS:[ESP+0x1C],0x1
 *  10017535  ^7C E1            JL SHORT Ags.10017518
 *  10017537   3C 39            CMP AL,0x39
 *  10017539   7F 13            JG SHORT Ags.1001754E
 *  1001753B   83C6 01          ADD ESI,0x1
 *  1001753E   0FBED0           MOVSX EDX,AL
 *  10017541   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  10017543   3C 30            CMP AL,0x30
 *  10017545   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
 *  10017548   8D4C4A D0        LEA ECX,DWORD PTR DS:[EDX+ECX*2-0x30]
 *  1001754C  ^7D E9            JGE SHORT Ags.10017537
 *  1001754E   3BCB             CMP ECX,EBX
 *  10017550  ^74 C6            JE SHORT Ags.10017518
 *  10017552   894C24 2C        MOV DWORD PTR SS:[ESP+0x2C],ECX
 *  10017556  ^EB C0            JMP SHORT Ags.10017518
 *  10017558   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
 *  1001755B   83C6 01          ADD ESI,0x1
 *  1001755E   3C 30            CMP AL,0x30
 *  10017560  ^7C B6            JL SHORT Ags.10017518
 *  10017562   3C 39            CMP AL,0x39
 *  10017564  ^7F B2            JG SHORT Ags.10017518
 *  10017566   0FBEC0           MOVSX EAX,AL
 *  10017569   66:8B0C45 94CA02>MOV CX,WORD PTR DS:[EAX*2+0x1002CA94]
 *  10017571   66:81C9 0080     OR CX,0x8000
 *  10017576   0FB7D1           MOVZX EDX,CX
 *  10017579   895424 20        MOV DWORD PTR SS:[ESP+0x20],EDX
 *  1001757D  ^EB 96            JMP SHORT Ags.10017515
 *  1001757F   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
 *  10017582   83C6 01          ADD ESI,0x1
 *  10017585   3C 30            CMP AL,0x30
 *  10017587  ^7C 8F            JL SHORT Ags.10017518
 *  10017589   3C 39            CMP AL,0x39
 *  1001758B  ^7F 8B            JG SHORT Ags.10017518
 *  1001758D   0FBEC0           MOVSX EAX,AL
 *  10017590   0FB70C45 94CA021>MOVZX ECX,WORD PTR DS:[EAX*2+0x1002CA94]
 *  10017598   894C24 20        MOV DWORD PTR SS:[ESP+0x20],ECX
 *  1001759C  ^E9 74FFFFFF      JMP Ags.10017515
 *  100175A1   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
 *  100175A4   83C6 01          ADD ESI,0x1
 *  100175A7   3C 30            CMP AL,0x30
 *  100175A9  ^0F8C 69FFFFFF    JL Ags.10017518
 *  100175AF   3C 39            CMP AL,0x39
 *  100175B1  ^0F8F 61FFFFFF    JG Ags.10017518
 *  100175B7   0FBED0           MOVSX EDX,AL
 *  100175BA   0FB70455 94CA021>MOVZX EAX,WORD PTR DS:[EDX*2+0x1002CA94]
 *  100175C2   894424 30        MOV DWORD PTR SS:[ESP+0x30],EAX
 *  100175C6  ^E9 4AFFFFFF      JMP Ags.10017515
 *  100175CB   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
 *  100175CE   83C6 01          ADD ESI,0x1
 *  100175D1   33C9             XOR ECX,ECX
 *  100175D3   3C 30            CMP AL,0x30
 *  100175D5  ^0F8C 3DFFFFFF    JL Ags.10017518
 *  100175DB   EB 03            JMP SHORT Ags.100175E0
 *  100175DD   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  100175E0   3C 39            CMP AL,0x39
 *  100175E2   7F 13            JG SHORT Ags.100175F7
 *  100175E4   83C6 01          ADD ESI,0x1
 *  100175E7   0FBED0           MOVSX EDX,AL
 *  100175EA   8A06             MOV AL,BYTE PTR DS:[ESI]
 *  100175EC   3C 30            CMP AL,0x30
 *  100175EE   8D0C89           LEA ECX,DWORD PTR DS:[ECX+ECX*4]
 *  100175F1   8D4C4A D0        LEA ECX,DWORD PTR DS:[EDX+ECX*2-0x30]
 *  100175F5  ^7D E9            JGE SHORT Ags.100175E0
 *  100175F7   3BCB             CMP ECX,EBX
 *  100175F9  ^0F84 19FFFFFF    JE Ags.10017518
 *  100175FF   894C24 34        MOV DWORD PTR SS:[ESP+0x34],ECX
 *  10017603  ^E9 10FFFFFF      JMP Ags.10017518
 *  10017608   8A07             MOV AL,BYTE PTR DS:[EDI]
 *  1001760A   3C 3C            CMP AL,0x3C
 *  1001760C   75 2A            JNZ SHORT Ags.10017638
 *  1001760E   83C7 01          ADD EDI,0x1
 *  10017611   8806             MOV BYTE PTR DS:[ESI],AL
 *  10017613   8A07             MOV AL,BYTE PTR DS:[EDI]
 *  10017615   83C6 01          ADD ESI,0x1
 *  10017618   84C0             TEST AL,AL
 *  1001761A   74 16            JE SHORT Ags.10017632
 *  1001761C   8D6424 00        LEA ESP,DWORD PTR SS:[ESP]
 *  10017620   3C 3E            CMP AL,0x3E
 *  10017622   74 0E            JE SHORT Ags.10017632
 *  10017624   83C7 01          ADD EDI,0x1
 *  10017627   8806             MOV BYTE PTR DS:[ESI],AL
 *  10017629   8A07             MOV AL,BYTE PTR DS:[EDI]
 *  1001762B   83C6 01          ADD ESI,0x1
 *  1001762E   84C0             TEST AL,AL
 *  10017630  ^75 EE            JNZ SHORT Ags.10017620
 *  10017632   8A07             MOV AL,BYTE PTR DS:[EDI]
 *  10017634   8806             MOV BYTE PTR DS:[ESI],AL
 *  10017636   EB 46            JMP SHORT Ags.1001767E
 *  10017638   3C 0A            CMP AL,0xA
 *  1001763A   74 27            JE SHORT Ags.10017663
 *  1001763C   3C 7C            CMP AL,0x7C
 *  1001763E   74 23            JE SHORT Ags.10017663
 *  10017640   837C24 28 00     CMP DWORD PTR SS:[ESP+0x28],0x0
 *  10017645   74 0F            JE SHORT Ags.10017656
 *  10017647   50               PUSH EAX
 *  10017648   56               PUSH ESI
 *  10017649   FFD5             CALL EBP
 *  1001764B   83C6 02          ADD ESI,0x2
 *  1001764E   83C7 01          ADD EDI,0x1
 *  10017651   83C3 02          ADD EBX,0x2
 *  10017654   EB 2E            JMP SHORT Ags.10017684
 *  10017656   8806             MOV BYTE PTR DS:[ESI],AL
 *  10017658   83C6 01          ADD ESI,0x1
 *  1001765B   83C7 01          ADD EDI,0x1
 *  1001765E   83C3 01          ADD EBX,0x1
 *  10017661   EB 21            JMP SHORT Ags.10017684
 *  10017663   395C24 14        CMP DWORD PTR SS:[ESP+0x14],EBX
 *  10017667   73 04            JNB SHORT Ags.1001766D
 *  10017669   895C24 14        MOV DWORD PTR SS:[ESP+0x14],EBX
 *  1001766D   837C24 1C 00     CMP DWORD PTR SS:[ESP+0x1C],0x0
 *  10017672   74 3D            JE SHORT Ags.100176B1
 *  10017674   33DB             XOR EBX,EBX
 *  10017676   834424 18 01     ADD DWORD PTR SS:[ESP+0x18],0x1
 *  1001767B   C606 0A          MOV BYTE PTR DS:[ESI],0xA
 *  1001767E   83C6 01          ADD ESI,0x1
 *  10017681   83C7 01          ADD EDI,0x1
 *  10017684   3B5C24 2C        CMP EBX,DWORD PTR SS:[ESP+0x2C]
 *  10017688   72 1E            JB SHORT Ags.100176A8
 *  1001768A   395C24 14        CMP DWORD PTR SS:[ESP+0x14],EBX
 *  1001768E   73 04            JNB SHORT Ags.10017694
 *  10017690   895C24 14        MOV DWORD PTR SS:[ESP+0x14],EBX
 *  10017694   837C24 1C 00     CMP DWORD PTR SS:[ESP+0x1C],0x0
 *  10017699   74 16            JE SHORT Ags.100176B1
 *  1001769B   834424 18 01     ADD DWORD PTR SS:[ESP+0x18],0x1
 *  100176A0   33DB             XOR EBX,EBX
 *  100176A2   C606 0A          MOV BYTE PTR DS:[ESI],0xA
 *  100176A5   83C6 01          ADD ESI,0x1
 *  100176A8   803F 00          CMP BYTE PTR DS:[EDI],0x0
 *  100176AB  ^0F85 AFFDFFFF    JNZ Ags.10017460
 *  100176B1   395C24 14        CMP DWORD PTR SS:[ESP+0x14],EBX
 *  100176B5   8B6C24 3C        MOV EBP,DWORD PTR SS:[ESP+0x3C]
 *  100176B9   73 04            JNB SHORT Ags.100176BF
 *  100176BB   895C24 14        MOV DWORD PTR SS:[ESP+0x14],EBX
 *  100176BF   33DB             XOR EBX,EBX
 *  100176C1   8B4C24 18        MOV ECX,DWORD PTR SS:[ESP+0x18]
 *  100176C5   83C1 01          ADD ECX,0x1
 *  100176C8   807E FF 0A       CMP BYTE PTR DS:[ESI-0x1],0xA
 *  100176CC   75 03            JNZ SHORT Ags.100176D1
 *  100176CE   83C6 FF          ADD ESI,-0x1
 *  100176D1   C606 00          MOV BYTE PTR DS:[ESI],0x0
 *  100176D4   8B45 30          MOV EAX,DWORD PTR SS:[EBP+0x30]
 *  100176D7   8BD0             MOV EDX,EAX
 *  100176D9   0FAFC1           IMUL EAX,ECX
 *  100176DC   0FAF5424 14      IMUL EDX,DWORD PTR SS:[ESP+0x14]
 *  100176E1   8945 10          MOV DWORD PTR SS:[EBP+0x10],EAX
 *  100176E4   A1 BC3F0310      MOV EAX,DWORD PTR DS:[0x10033FBC]
 *  100176E9   D1EA             SHR EDX,1
 *  100176EB   8955 0C          MOV DWORD PTR SS:[EBP+0xC],EDX
 *  100176EE   8B88 44010000    MOV ECX,DWORD PTR DS:[EAX+0x144]
 *  100176F4   3999 28010000    CMP DWORD PTR DS:[ECX+0x128],EBX
 *  100176FA   74 19            JE SHORT Ags.10017715
 *  100176FC   8B5424 30        MOV EDX,DWORD PTR SS:[ESP+0x30]
 *  10017700   8B4424 20        MOV EAX,DWORD PTR SS:[ESP+0x20]
 *  10017704   52               PUSH EDX
 *  10017705   50               PUSH EAX
 *  10017706   8B4424 3C        MOV EAX,DWORD PTR SS:[ESP+0x3C]
 *  1001770A   55               PUSH EBP
 *  1001770B   E8 90F5FFFF      CALL Ags.10016CA0	; jichi: the paint function, bad text  address in arg1 + 0x34, good text in arg7
 *  10017710   83C4 0C          ADD ESP,0xC
 *  10017713   EB 1B            JMP SHORT Ags.10017730
 *  10017715   8B4C24 30        MOV ECX,DWORD PTR SS:[ESP+0x30]
 *  10017719   8B5424 20        MOV EDX,DWORD PTR SS:[ESP+0x20]
 *  1001771D   8B45 34          MOV EAX,DWORD PTR SS:[EBP+0x34]
 *  10017720   51               PUSH ECX
 *  10017721   8B4C24 38        MOV ECX,DWORD PTR SS:[ESP+0x38]
 *  10017725   52               PUSH EDX
 *  10017726   50               PUSH EAX
 *  10017727   55               PUSH EBP
 *  10017728   E8 33F9FFFF      CALL Ags.10017060
 *  1001772D   83C4 10          ADD ESP,0x10
 *  10017730   8B4D 30          MOV ECX,DWORD PTR SS:[EBP+0x30]
 *  10017733   8BC1             MOV EAX,ECX
 *  10017735   99               CDQ
 *  10017736   2BC2             SUB EAX,EDX
 *  10017738   5F               POP EDI
 *  10017739   D1F8             SAR EAX,1
 *  1001773B   5E               POP ESI
 *  1001773C   8945 1C          MOV DWORD PTR SS:[EBP+0x1C],EAX
 *  1001773F   894D 20          MOV DWORD PTR SS:[EBP+0x20],ECX
 *  10017742   5D               POP EBP
 *  10017743   B8 01000000      MOV EAX,0x1
 *  10017748   5B               POP EBX
 *  10017749   83C4 28          ADD ESP,0x28
 *  1001774C   C3               RETN
 *  1001774D   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
 *  10017750   7F 75            JG SHORT Ags.100177C7
 *  10017752   0110             ADD DWORD PTR DS:[EAX],EDX
 *  10017754   CB               RETF                                     ; Far return
 *  10017755   75 01            JNZ SHORT Ags.10017758
 *  10017757   1058 75          ADC BYTE PTR DS:[EAX+0x75],BL
 *  1001775A   0110             ADD DWORD PTR DS:[EAX],EDX
 *  1001775C   A1 75011023      MOV EAX,DWORD PTR DS:[0x23100175]
 *  10017761   75 01            JNZ SHORT Ags.10017764
 *  10017763   10D1             ADC CL,DL
 *  10017765   74 01            JE SHORT Ags.10017768
 *  10017767   100D 75011015    ADC BYTE PTR DS:[0x15100175],CL
 *  1001776D   75 01            JNZ SHORT Ags.10017770
 *  1001776F   1000             ADC BYTE PTR DS:[EAX],AL
 *  10017771   0107             ADD DWORD PTR DS:[EDI],EAX
 *  10017773   07               POP ES                                   ; Modification of segment register
 *  10017774   07               POP ES                                   ; Modification of segment register
 *  10017775   07               POP ES                                   ; Modification of segment register
 *  10017776   07               POP ES                                   ; Modification of segment register
 *  10017777   07               POP ES                                   ; Modification of segment register
 *  10017778   07               POP ES                                   ; Modification of segment register
 *  10017779   07               POP ES                                   ; Modification of segment register
 *  1001777A   07               POP ES                                   ; Modification of segment register
 *  1001777B   07               POP ES                                   ; Modification of segment register
 *  1001777C   07               POP ES                                   ; Modification of segment register
 *  1001777D   07               POP ES                                   ; Modification of segment register
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x8b,0x44,0x24, 0x3c,   // 10017706   8b4424 3c        mov eax,dword ptr ss:[esp+0x3c]
    0x55,                   // 1001770a   55               push ebp
    0xe8, XX4,              // 1001770b   e8 90f5ffff      call ags.10016ca0	; jichi: the paint function, bad text  address in arg1 + 0x34, good text in arg7
    0x83,0xc4, 0x0c,        // 10017710   83c4 0c          add esp,0xc
    0xeb, 0x1b              // 10017713   eb 1b            jmp short ags.10017730
  };
  enum { addr_offset = 0x1001770b - 0x10017706 }; // == 5
  ulong addr = MemDbg::matchBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  return winhook::hook_both(addr + addr_offset, Private::hookBefore, Private::hookAfter);
}
} // namespace AgsPatchA

} // unnamed namespace

/** Public class */

bool SystemAoiEngine::attach()
{
  HMODULE hModule = ::GetModuleHandleA("Ags.dll");
  if (hModule) { // Aoi <= 3
    if (!AgsHookA::attach(hModule))
      return false;

    ulong startAddress, stopAddress;
    if (Engine::getModuleMemoryRange(L"Ags.dll", &startAddress, &stopAddress) &&
        AgsPatchA::attach(startAddress, stopAddress)) {
      enableDynamicEncoding = true;
      DOUT("patch encoding succeeded");
    } else
      DOUT("patch encoding FAILED");

    name = "EmbedSystemAoiA";
    HijackManager::instance()->attachFunction((ulong)::DrawTextExA); // Font can already be dynamically changed and hence not needed
    return true;

  } else { // Aoi >= 4, UTF-16
    hModule = ::GetModuleHandleA("Ags5.dll");
    if (!hModule)
      hModule = ::GetModuleHandleA("Ags4.dll");
    if (!hModule || !AgsHookW::attach(hModule))
      return false;
    name = "EmbedSystemAoiW";
    encoding = Utf16Encoding;
    return true;
  }
}

// EOF

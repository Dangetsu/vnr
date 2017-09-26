// circus.cc
// 6/5/2014 jichi
#include "engine/model/circus.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
#include "hijack/hijackmanager.h"
#include "memdbg/memsearch.h"
#include "winhook/hookcode.h"
#include <qt_windows.h>
#include <QtCore/QRegExp>
#include <cstdint>

#define DEBUG "model/circus"
#include "sakurakit/skdebug.h"

/** Private data */

namespace { // unnamed

// Skip leading tags such as @K and @c5
template <typename strT>
strT ltrim(strT s)
{
  if (s && *s == '@')
    while ((signed char)*++s > 0);
  return s;
}

namespace ScenarioHook {
namespace Private {

  DWORD nameReturnAddress_,
        scenarioReturnAddress_;

  /**
   *  Sample game: DC3, function: 0x4201d0
   *
   *  IDA: sub_4201D0      proc near
   *  - arg_0 = dword ptr  4
   *  - arg_4 = dword ptr  8
   *
   *  Observations:
   *  - arg1: LPVOID, pointed to unknown object
   *  - arg2: LPCSTR, the actual text
   *
   *  Example runtime stack:
   *  0012F15C   0040C208  RETURN to .0040C208 from .00420460
   *  0012F160   0012F7CC ; jichi: unknown stck
   *  0012F164   0012F174 ; jichi: text
   *  0012F168   0012F6CC
   *  0012F16C   0012F7CC
   *  0012F170   0012F7CC
   */
  bool hookBefore(winhook::hook_stack *s)
  {
    static QByteArray data_; // persistent storage, which makes this function not thread-safe
    LPCSTR text = (LPCSTR)s->stack[2], // arg2
           trimmedText = ltrim(text);
    if (!trimmedText || !*trimmedText)
      return true;
    auto retaddr = s->stack[0]; // retaddr
    auto role = retaddr == scenarioReturnAddress_ ? Engine::ScenarioRole :
                retaddr == nameReturnAddress_ ? Engine::NameRole :
                Engine::OtherRole;
                //s->ebx? Engine::OtherRole : // other threads ebx is not zero
                //// 004201e4  |. 83c1 02        |add ecx,0x2
                //// 004201e7  |. eb 04          |jmp short dc3.004201ed
                //*(BYTE *)(retaddr + 3) == 0xe9 // old name
                //? Engine::NameRole : // retaddr+3 is jmp
                //Engine::ScenarioRole;
    auto sig = Engine::hashThreadSignature(role, retaddr);
    QByteArray oldData = trimmedText,
               newData = EngineController::instance()->dispatchTextA(oldData, role, sig);
    if (oldData == newData)
      return true;
    if (trimmedText != text)
      newData.prepend(text, trimmedText - text);
    data_ = newData;
    s->stack[2] = (DWORD)data_.constData(); // reset arg2
    return true;
  }

  // Alternatively, using the following pattern bytes also works:
  //
  // 3c24750583c102eb0488024241
  //
  // 004201e0  |> 3c 24          /cmp al,0x24
  // 004201e2  |. 75 05          |jnz short dc3.004201e9
  // 004201e4  |. 83c1 02        |add ecx,0x2
  // 004201e7  |. eb 04          |jmp short dc3.004201ed
  // 004201e9  |> 8802           |mov byte ptr ds:[edx],al
  // 004201eb  |. 42             |inc edx
  // 004201ec  |. 41             |inc ecx
  ulong findFunctionAddress(ulong startAddress, ulong stopAddress) // find the function to hook
  {
    //return 0x4201d0; // DC3 function address
    for (ulong i = startAddress + 0x1000; i < stopAddress -4; i++)
      // *  004201e0  |> 3c 24          /cmp al,0x24
      // *  004201e2  |. 75 05          |jnz short dc3.004201e9
      if ((*(ulong *)i & 0xffffff) == 0x75243c) { // cmp al, 24; je
        enum { range = 0x80 }; // the range is small, since it is a small function
        if (ulong addr = MemDbg::findEnclosingAlignedFunction(i, range))
          return addr;
      }
    return 0;
  }

} // namespace Private

/**
 *  jichi 6/5/2014: Sample function from DC3 at 0x4201d0
 *
 *  Sample game: DC3PP
 *  0042CE1E   68 E0F0B700      PUSH .00B7F0E0
 *  0042CE23   A3 0C824800      MOV DWORD PTR DS:[0x48820C],EAX
 *  0042CE28   E8 A352FFFF      CALL .004220D0  ; jichi: name thread
 *  0042CE2D   C705 08024D00 01>MOV DWORD PTR DS:[0x4D0208],0x1
 *  0042CE37   EB 52            JMP SHORT .0042CE8B
 *  0042CE39   392D 08024D00    CMP DWORD PTR DS:[0x4D0208],EBP
 *  0042CE3F   74 08            JE SHORT .0042CE49
 *  0042CE41   392D 205BB900    CMP DWORD PTR DS:[0xB95B20],EBP
 *  0042CE47   74 07            JE SHORT .0042CE50
 *  0042CE49   C605 E0F0B700 00 MOV BYTE PTR DS:[0xB7F0E0],0x0
 *  0042CE50   8D5424 40        LEA EDX,DWORD PTR SS:[ESP+0x40]
 *  0042CE54   52               PUSH EDX
 *  0042CE55   68 30B5BA00      PUSH .00BAB530
 *  0042CE5A   892D 08024D00    MOV DWORD PTR DS:[0x4D0208],EBP
 *  0042CE60   E8 6B52FFFF      CALL .004220D0  ; jichi: scenario thread
 *  0042CE65   C705 A0814800 FF>MOV DWORD PTR DS:[0x4881A0],-0x1
 *  0042CE6F   892D 2C824800    MOV DWORD PTR DS:[0x48822C],EBP
 *
 *  Sample game: 水夏弐律
 *
 *  004201ce     cc             int3
 *  004201cf     cc             int3
 *  004201d0  /$ 8b4c24 08      mov ecx,dword ptr ss:[esp+0x8]
 *  004201d4  |. 8a01           mov al,byte ptr ds:[ecx]
 *  004201d6  |. 84c0           test al,al
 *  004201d8  |. 74 1c          je short dc3.004201f6
 *  004201da  |. 8b5424 04      mov edx,dword ptr ss:[esp+0x4]
 *  004201de  |. 8bff           mov edi,edi
 *  004201e0  |> 3c 24          /cmp al,0x24
 *  004201e2  |. 75 05          |jnz short dc3.004201e9
 *  004201e4  |. 83c1 02        |add ecx,0x2
 *  004201e7  |. eb 04          |jmp short dc3.004201ed
 *  004201e9  |> 8802           |mov byte ptr ds:[edx],al
 *  004201eb  |. 42             |inc edx
 *  004201ec  |. 41             |inc ecx
 *  004201ed  |> 8a01           |mov al,byte ptr ds:[ecx]
 *  004201ef  |. 84c0           |test al,al
 *  004201f1  |.^75 ed          \jnz short dc3.004201e0
 *  004201f3  |. 8802           mov byte ptr ds:[edx],al
 *  004201f5  |. c3             retn
 *  004201f6  |> 8b4424 04      mov eax,dword ptr ss:[esp+0x4]
 *  004201fa  |. c600 00        mov byte ptr ds:[eax],0x0
 *  004201fd  \. c3             retn
 *
 *  Sample registers:
 *  EAX 0012F998
 *  ECX 000000DB
 *  EDX 00000059
 *  EBX 00000000    ; ebx is zero for name/scenario thread
 *  ESP 0012F96C
 *  EBP 00000003
 *  ESI 00000025
 *  EDI 000000DB
 *  EIP 022C0000
 *
 *  EAX 0012F174
 *  ECX 0012F7CC
 *  EDX FDFBF80C
 *  EBX 0012F6CC
 *  ESP 0012F15C
 *  EBP 0012F5CC
 *  ESI 800000DB
 *  EDI 00000001
 *  EIP 00420460 .00420460
 *
 *  EAX 0012F174
 *  ECX 0012F7CC
 *  EDX FDFBF7DF
 *  EBX 0012F6CC
 *  ESP 0012F15C
 *  EBP 0012F5CC
 *  ESI 00000108
 *  EDI 00000001
 *  EIP 00420460 .00420460
 *
 *  0042DC5D   52               PUSH EDX
 *  0042DC5E   68 E038AC00      PUSH .00AC38E0                           ; ASCII "Ami"
 *  0042DC63   E8 F827FFFF      CALL .00420460  ; jichi: name thread
 *  0042DC68   83C4 08          ADD ESP,0x8
 *  0042DC6B   E9 48000000      JMP .0042DCB8
 *  0042DC70   83FD 58          CMP EBP,0x58
 *  0042DC73   74 07            JE SHORT .0042DC7C
 *  0042DC75   C605 E038AC00 00 MOV BYTE PTR DS:[0xAC38E0],0x0
 *  0042DC7C   8D4424 20        LEA EAX,DWORD PTR SS:[ESP+0x20]
 *  0042DC80   50               PUSH EAX
 *  0042DC81   68 0808AF00      PUSH .00AF0808
 *  0042DC86   E8 D527FFFF      CALL .00420460 ; jichi: scenario thread
 *  0042DC8B   83C4 08          ADD ESP,0x8
 *  0042DC8E   33C0             XOR EAX,EAX
 *  0042DC90   C705 D0DF4700 FF>MOV DWORD PTR DS:[0x47DFD0],-0x1
 *  0042DC9A   A3 0CE04700      MOV DWORD PTR DS:[0x47E00C],EAX
 *  0042DC9F   A3 940EB200      MOV DWORD PTR DS:[0xB20E94],EAX
 *  0042DCA4   A3 2C65AC00      MOV DWORD PTR DS:[0xAC652C],EAX
 *  0042DCA9   C705 50F9AC00 59>MOV DWORD PTR DS:[0xACF950],0x59
 *  0042DCB3   A3 3C70AE00      MOV DWORD PTR DS:[0xAE703C],EAX
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  ulong addr = Private::findFunctionAddress(startAddress, stopAddress);
  if (!addr)
    return false;
  // Find the nearest two callers (distance within 100)
  ulong lastCall = 0;
  auto fun = [&lastCall](ulong call) -> bool {
    // scenario: 0x42b78c
    // name: 0x42b754
    if (call - lastCall < 100) {
      Private::scenarioReturnAddress_ = call + 5;
      Private::nameReturnAddress_ = lastCall + 5;
      DOUT("found scenario and name calls");
      return false; // found target
    }
    lastCall = call;
    return true; // replace all functions
  };
  MemDbg::iterNearCallAddress(fun, addr, startAddress, stopAddress);
  if (!Private::scenarioReturnAddress_ && lastCall) {
    Private::scenarioReturnAddress_ = lastCall + 5;
    DOUT("scenario and name calls NOT FOUND");
  }
  return winhook::hook_before(addr, Private::hookBefore);
}

} // namespace ScenarioHook

namespace OtherHook {
namespace Private {

  bool hookBefore(winhook::hook_stack *s)
  {
    LPSTR text = ltrim((LPSTR)s->stack[5]);// arg5
    if (!text || !*text)
      return true;
    auto retaddr = s->stack[0]; // retaddr
    enum { role = Engine::OtherRole };
    auto sig = Engine::hashThreadSignature(role, retaddr);
    QByteArray data = EngineController::instance()->dispatchTextA(text, role, sig);
    ::strcpy(text, data.constData());
    //if (trimmedText != text)
    //  newData.prepend(text, trimmedText - text);
    //data_ = newData;
    //s->stack[5] = (DWORD)data_.constData(); // reset arg5
    return true;
  }

} // namespace Private

/**
 *  Sample game: DC3 XRated
 *  See: http://capita.tistory.com/m/post/117
 *
 *  HOOK(0x00401DF0,TRANS([ESP+0x14],PTRBACKUP,OVERWRITE(IGNORE)),RETNPOS(COPY)),HOOK(0x00421A90,TRANS([ESP+0x4],PTRBACKUP,OVERWRITE(IGNORE)),RETNPOS(COPY)),FORCEFONT(5),ENCODEKOR,HOOK(0x0042B74F,TRANS([ESP+0x4],PTRCHEAT,PTRBACKUP),RETNPOS(COPY)),FONT(돋움,-13)
 *
 *  The first hook is Other hook.
 *  The last hook is name, that is exactly the same as my name hook (mine is better).
 *  The second hook is equivalent to my scenario hook, and invoked after my scenario threads (mine is better).
 *
 *  00401DEE   CC               INT3
 *  00401DEF   CC               INT3
 *  00401DF0   55               PUSH EBP
 *  00401DF1   56               PUSH ESI
 *  00401DF2   8B7424 0C        MOV ESI,DWORD PTR SS:[ESP+0xC]
 *  00401DF6   6A 00            PUSH 0x0
 *  00401DF8   6A 04            PUSH 0x4
 *  00401DFA   56               PUSH ESI
 *  00401DFB   E8 10FBFFFF      CALL .00401910
 *  00401E00   8BE8             MOV EBP,EAX
 *  00401E02   83C4 0C          ADD ESP,0xC
 *  00401E05   83FD FF          CMP EBP,-0x1
 *  00401E08   0F84 95000000    JE .00401EA3
 *  00401E0E   57               PUSH EDI
 *  00401E0F   E8 9CFFFFFF      CALL .00401DB0
 *  00401E14   6BF6 58          IMUL ESI,ESI,0x58
 *  00401E17   8B8E A0C84800    MOV ECX,DWORD PTR DS:[ESI+0x48C8A0]
 *  00401E1D   8B5424 14        MOV EDX,DWORD PTR SS:[ESP+0x14]
 *  00401E21   8B7424 18        MOV ESI,DWORD PTR SS:[ESP+0x18]
 *  00401E25   03CD             ADD ECX,EBP
 *  00401E27   6BC9 4C          IMUL ECX,ECX,0x4C
 *  00401E2A   8991 50CE4800    MOV DWORD PTR DS:[ECX+0x48CE50],EDX
 *  00401E30   89B1 54CE4800    MOV DWORD PTR DS:[ECX+0x48CE54],ESI
 *  00401E36   8BF8             MOV EDI,EAX
 *  00401E38   8B4424 1C        MOV EAX,DWORD PTR SS:[ESP+0x1C]
 *  00401E3C   89B9 2CCE4800    MOV DWORD PTR DS:[ECX+0x48CE2C],EDI
 *  00401E42   8BCF             MOV ECX,EDI
 *  00401E44   69C9 54110000    IMUL ECX,ECX,0x1154
 *  00401E4A   8981 208F4900    MOV DWORD PTR DS:[ECX+0x498F20],EAX
 *  00401E50   8B4424 24        MOV EAX,DWORD PTR SS:[ESP+0x24]
 *  00401E54   8991 5CA04900    MOV DWORD PTR DS:[ECX+0x49A05C],EDX
 *  00401E5A   8991 64A04900    MOV DWORD PTR DS:[ECX+0x49A064],EDX
 *  00401E60   8B5424 20        MOV EDX,DWORD PTR SS:[ESP+0x20]
 *  00401E64   C781 1C8F4900 00>MOV DWORD PTR DS:[ECX+0x498F1C],0x0
 *  00401E6E   8981 248F4900    MOV DWORD PTR DS:[ECX+0x498F24],EAX
 *  00401E74   C681 CC904900 00 MOV BYTE PTR DS:[ECX+0x4990CC],0x0
 *  00401E7B   89B1 60A04900    MOV DWORD PTR DS:[ECX+0x49A060],ESI
 *  00401E81   89B1 68A04900    MOV DWORD PTR DS:[ECX+0x49A068],ESI
 *  00401E87   8D89 2C8F4900    LEA ECX,DWORD PTR DS:[ECX+0x498F2C]
 *  00401E8D   2BCA             SUB ECX,EDX
 *  00401E8F   90               NOP
 *  00401E90   8A02             MOV AL,BYTE PTR DS:[EDX]
 *  00401E92   880411           MOV BYTE PTR DS:[ECX+EDX],AL
 *  00401E95   42               INC EDX
 *  00401E96   84C0             TEST AL,AL
 *  00401E98  ^75 F6            JNZ SHORT .00401E90
 *  00401E9A   893D 24C84800    MOV DWORD PTR DS:[0x48C824],EDI
 *  00401EA0   8BC5             MOV EAX,EBP
 *  00401EA2   5F               POP EDI
 *  00401EA3   5E               POP ESI
 *  00401EA4   5D               POP EBP
 *  00401EA5   C3               RETN
 *  00401EA6   CC               INT3
 *  00401EA7   CC               INT3
 *  00401EA8   CC               INT3
 *  00401EA9   CC               INT3
 *  00401EAA   CC               INT3
 */
bool attach(ulong startAddress, ulong stopAddress)
{
  const uint8_t bytes[] = {
    0x0f,0x84, 0x95,0x00,0x00,0x00, // 00401e08   0f84 95000000    je .00401ea3
    0x57                            // 00401e0e   57               push edi
  };
  ulong addr = MemDbg::findBytes(bytes, sizeof(bytes), startAddress, stopAddress);
  if (!addr)
    return false;
  addr = MemDbg::findEnclosingAlignedFunction(addr);
  if (!addr)
    return false;
  return winhook::hook_before(addr, Private::hookBefore);
}

} // namespace OtherHook

} // unnamed namespace

/** Public class */

bool CircusEngine::attach()
{
  ulong startAddress, stopAddress;
  if (!Engine::getProcessMemoryRange(&startAddress, &stopAddress))
    return false;
  if (!ScenarioHook::attach(startAddress, stopAddress))
    return false;
  if (OtherHook::attach(startAddress, stopAddress))
    DOUT("other text found");
  else
    DOUT("other text NOT FOUND");
  HijackManager::instance()->attachFunction((ulong)::GetGlyphOutlineA); // this is only needed for ruby
  return true;
}

/**
 *  Get rid of ruby. Examples:
 *  ｛くらき／蔵木｝
 *  ｛・・・・／いいから｝この私に、紅茶を淹れなさい」
 */
QString CircusEngine::rubyCreate(const QString &rb, const QString &rt)
{
  static QString fmt = QString::fromWCharArray(L"\xff5b%2\xff0f%1\xff5d");
  return fmt.arg(rb, rt);
}

// Remove furigana in scenario thread.
QString CircusEngine::rubyRemove(const QString &text)
{
  if (!text.contains((wchar_t)0xff5b))
    return text;
  static QRegExp rx(QString::fromWCharArray(L"\xff5b.+\xff0f(.+)\xff5d"));
  if (!rx.isMinimal())
    rx.setMinimal(true);
  return QString(text).replace(rx, "\\1");
}

  //const wchar_t
  //  w_open = 0xff5b    /* ｛ */
  //  , w_close = 0xff5d /* ｝ */
  //  , w_split = 0xff0f /* ／ */
  //;
  //if (!text.contains(w_open))
  //  return text;
  //QString ret = text;
  //for (int pos = ret.indexOf(w_open); pos != -1; pos = ret.indexOf(w_open, pos)) {
  //  int split_pos = ret.indexOf(w_split, pos);
  //  if (split_pos == -1)
  //    return ret;
  //  int close_pos = ret.indexOf(w_close, split_pos);
  //  if (close_pos == -1)
  //    return ret;
  //  ret.remove(close_pos, 1);
  //  ret.remove(pos, split_pos - pos + 1);
  //  pos += close_pos - split_pos - 1;
  //}
  //return ret;

// EOF

/*
// Remove "\n" for scenario text
QString CircusEngine::textFilter(const QString &text, int role)
{
  QString ret = text;
  if (role == Engine::ScenarioRole)
    ret.remove('\n');
  return ret;
}

// Insert "\n"
QString CircusEngine::translationFilter(const QString &text, int role)
{
  if (role != Engine::ScenarioRole)
    return text;
  enum { MaxLineWitdth = 61 }; // estimated in DC3. FIXME: This might be different for different game

  QString ret;
  int lineWidth = 0, // estimated line width
      lineCount = 0; // number of characters
  foreach (const QChar &c, text) {
    int w = c.unicode() <= 255 ? 1 : 2;
    if (lineWidth + w <= MaxLineWitdth) {
      lineCount ++;
      lineWidth += w;
    } else {
      bool wordWrap = false;
      if (lineCount)
        for (int i = 0; i < lineCount; i++)
          if (ret[ret.size() - i - 1].isSpace()) {
            wordWrap = true;
            ret[ret.size() - i - 1] = '\n';
            lineCount = i;
            lineWidth = 0;
            for (int i = 0; i < lineCount; i++)
              lineWidth +=  ret[ret.size() - i - 2].unicode() < 255 ? 1 : 2;
            break;
          }
      if (!wordWrap) {
        ret.append('\n');
        lineWidth = lineCount = 0;
      }
    }
    ret.append(c);
  }
  return ret;
}
*/

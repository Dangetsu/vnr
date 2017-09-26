# coding: utf8
# engines.py
# 10/3/2013 jichi
# Windows only

if __name__ == '__main__': # DEBUG
  import sys
  sys.path.append("..")

import os, re
from glob import glob
from sakurakit.skdebug import dprint
from sakurakit.skfileio import escapeglob
#from sakurakit.skclass import memoized

SJIS_ENCODING = 'shift-jis'
UTF8_ENCODING = 'utf8'
UTF16_ENCODING = 'utf-16'

ENINES = []
def engines():
  """
  @yield  Engine
  """
  if not ENINES:
    ENGINES = [
      MonoEngine(),
      System4Engine(),
      NitroplusEngine(),
      #GXPEngine(),
    ]
  return ENGINES

class Engine(object): # placeholder
  NAME = ''
  ENCODING = ''

  DEBUG = False
  #DEBUG = True

  def name(self): return self.NAME
  def encoding(self): return self.ENCODING

  def addHook(self, code, name=''): # str, str -> bool
   from texthook import texthook
   return texthook.global_().addHook(code, name=name or self.name(), verbose=self.DEBUG)

  # Pure virtual functions
  def match(self, pid):
    """
    @param  pid  long
    @return  bool
    """
    return False

  def inject(self, pid):
    """
    @param  pid  long
    @return  bool
    """
    return False

  # Helpers

  def getAppName(self, pid):
    """
    @param  pid  long
    @return  unicode or None
    """
    from sakurakit import skwin
    return skwin.get_process_name(pid)

  def getAppPath(self, pid):
    """
    @param  pid  long
    @return  unicode or None
    """
    from sakurakit import skwin
    return skwin.get_process_path(pid)

  def getAppDirectory(self, pid):
    """
    @param  pid  long
    @return  unicode or None
    """
    path = self.getAppPath(pid)
    if path:
      return os.path.dirname(path)

  def exists(self, pattern, pid):
    """
    @param  pattern  unicode
    @param  pid  long
    @return  bool
    """
    path = self.getAppDirectory(pid)
    return bool(path) and os.path.exists(os.path.join(path, pattern))

  def globAppDirectory(self, pattern, pid):
    """
    @param  pattern  str
    @param  pid  long
    @return  [unicode path] or None
    """
    path = self.getAppDirectory(pid)
    if path:
      return glob(os.path.join(escapeglob(path), pattern))

  def globAppDirectories(self, patterns, pid):
    """Return all paths or None if failed
    @param  pattern  [str]
    @param  pid  long
    @return  [unicode path] or None  if return list, it must have the same length as patterns
    """
    path = self.getAppDirectory(pid)
    if path:
      ret = []
      for pat in patterns:
        r = glob(os.path.join(escapeglob(path), pat))
        if not r:
          return None
        ret.append(r)
      return ret

# jichi 4/21/2014: Mono (Unity3D)
# Sample game: BSZ
# See (ok123): http://sakuradite.com/topic/214
# Pattern: 33DB66390175
#
# Example: /HWN-8*0:3C@ mono.dll search 33DB66390175
# - length_offset: 1
# - module: 1690566707 = 0x64c40033
# - off: 4294967284 = 0xfffffff4 = -0xc
# - split: 60 = 0x3c
# - type: 1114 = 0x45a
#
# Function starts:
# 1003b818  /$ 55             push ebp ; jichi: text also in arg1+0xc, and arg2 is the char count?
# 1003b819  |. 8bec           mov ebp,esp
# 1003b81b  |. 51             push ecx
# 1003b81c  |. 807d 10 00     cmp byte ptr ss:[ebp+0x10],0x0
# 1003b820  |. 8b50 08        mov edx,dword ptr ds:[eax+0x8]
# 1003b823  |. 53             push ebx
# 1003b824  |. 8b5d 08        mov ebx,dword ptr ss:[ebp+0x8]
# 1003b827  |. 56             push esi
# 1003b828  |. 8b75 0c        mov esi,dword ptr ss:[ebp+0xc]
# 1003b82b  |. 57             push edi
# 1003b82c  |. 8d78 0c        lea edi,dword ptr ds:[eax+0xc]
# 1003b82f  |. 897d 08        mov dword ptr ss:[ebp+0x8],edi
# 1003b832  |. 74 44          je short mono.1003b878
# 1003b834  |. 2bf2           sub esi,edx
# 1003b836  |. 03f1           add esi,ecx
# 1003b838  |. 894d 10        mov dword ptr ss:[ebp+0x10],ecx
# 1003b83b  |. 8975 08        mov dword ptr ss:[ebp+0x8],esi
# 1003b83e  |. 3bce           cmp ecx,esi
# 1003b840  |. 7f 67          jg short mono.1003b8a9
# 1003b842  |. 8d4c4b 0c      lea ecx,dword ptr ds:[ebx+ecx*2+0xc]
# 1003b846  |> 0fb707         /movzx eax,word ptr ds:[edi]
# 1003b849  |. 33db           |xor ebx,ebx    ; jichi hook here
# 1003b84b  |. 66:3901        |cmp word ptr ds:[ecx],ax
# 1003b84e  |. 75 16          |jnz short mono.1003b866
# 1003b850  |. 8bf1           |mov esi,ecx
# 1003b852  |> 43             |/inc ebx
# 1003b853  |. 83c6 02        ||add esi,0x2
# 1003b856  |. 3bda           ||cmp ebx,edx
# 1003b858  |. 74 19          ||je short mono.1003b873
# 1003b85a  |. 66:8b06        ||mov ax,word ptr ds:[esi]
# 1003b85d  |. 66:3b045f      ||cmp ax,word ptr ds:[edi+ebx*2]
# 1003b861  |.^74 ef          |\je short mono.1003b852
# 1003b863  |. 8b75 08        |mov esi,dword ptr ss:[ebp+0x8]
# 1003b866  |> ff45 10        |inc dword ptr ss:[ebp+0x10]
# 1003b869  |. 83c1 02        |add ecx,0x2
# 1003b86c  |. 3975 10        |cmp dword ptr ss:[ebp+0x10],esi
# 1003b86f  |.^7e d5          \jle short mono.1003b846
class MonoEngine(Engine):

  NAME = "Mono" # str, override
  ENCODING = UTF16_ENCODING # str, override

  # Disable for CM3D, see: http://sakuradite.com/topic/996
  # Disable for PlayClub
  BLOCKED_FILES = "CM3D*.exe", "PlayClub.exe"
  def match(self, pid): # override
    if not self.globAppDirectory("*/Mono/mono.dll", pid):
      return False
    for it in self.BLOCKED_FILES:
      if self.globAppDirectory(it, pid):
        return False
    return True

  def inject(self, pid): # override
    from gamedebugger import GameDebugger
    dbg = GameDebugger(pid)
    ret = False
    if dbg.active():
      # See (ok123): http://9baka.com/read.php?tid=411756
      #pattern = 0x90, 0xff, 0x50, 0x3c, 0x83, 0xc4, 0x20, 0x8b, 0x45, 0xec
      #addr = dbg.searchbytes(pattern)

      pattern = 0x33db66390175
      #length = 0x50000 # larger than 0x3b849

      addr = dbg.search_module_memory(pattern, "mono.dll")
      if addr > 0:
        # NO_ASCII(J)
        code = "/HWNF-8*:3C@%x" % addr
        ret = self.addHook(code)
    dprint(ret)
    return ret

# 8/10/2015
# Sample game: ランス03 リーザス陥落 体験版
# H-code: /HSN-1c:-14@1D3D75:Rance03Trial.exe
#
# 005D3D1E   CC               INT3
# 005D3D1F   CC               INT3
# 005D3D20   53               PUSH EBX
# 005D3D21   56               PUSH ESI
# 005D3D22   8B7424 0C        MOV ESI,DWORD PTR SS:[ESP+0xC]
# 005D3D26   57               PUSH EDI
# 005D3D27   8BF9             MOV EDI,ECX
# 005D3D29   8B5E 10          MOV EBX,DWORD PTR DS:[ESI+0x10]
# 005D3D2C   43               INC EBX
# 005D3D2D   3B5F 0C          CMP EBX,DWORD PTR DS:[EDI+0xC]
# 005D3D30   76 1A            JBE SHORT .005D3D4C
# 005D3D32   53               PUSH EBX
# 005D3D33   8D4F 04          LEA ECX,DWORD PTR DS:[EDI+0x4]
# 005D3D36   C747 0C 00000000 MOV DWORD PTR DS:[EDI+0xC],0x0
# 005D3D3D   E8 6E710700      CALL .0064AEB0
# 005D3D42   84C0             TEST AL,AL
# 005D3D44   75 06            JNZ SHORT .005D3D4C
# 005D3D46   5F               POP EDI
# 005D3D47   5E               POP ESI
# 005D3D48   5B               POP EBX
# 005D3D49   C2 0400          RETN 0x4
# 005D3D4C   837E 14 10       CMP DWORD PTR DS:[ESI+0x14],0x10
# 005D3D50   72 02            JB SHORT .005D3D54
# 005D3D52   8B36             MOV ESI,DWORD PTR DS:[ESI]
# 005D3D54   837F 0C 00       CMP DWORD PTR DS:[EDI+0xC],0x0
# 005D3D58   75 15            JNZ SHORT .005D3D6F
# 005D3D5A   53               PUSH EBX
# 005D3D5B   33C0             XOR EAX,EAX
# 005D3D5D   56               PUSH ESI
# 005D3D5E   50               PUSH EAX
# 005D3D5F   E8 EC9A0C00      CALL .0069D850
# 005D3D64   83C4 0C          ADD ESP,0xC
# 005D3D67   B0 01            MOV AL,0x1
# 005D3D69   5F               POP EDI
# 005D3D6A   5E               POP ESI
# 005D3D6B   5B               POP EBX
# 005D3D6C   C2 0400          RETN 0x4
# 005D3D6F   8B47 08          MOV EAX,DWORD PTR DS:[EDI+0x8]
# 005D3D72   53               PUSH EBX
# 005D3D73   56               PUSH ESI
# 005D3D74   50               PUSH EAX
# 005D3D75   E8 D69A0C00      CALL .0069D850    ; jichi: hooked here, and pattern starts here
# 005D3D7A   83C4 0C          ADD ESP,0xC
# 005D3D7D   B0 01            MOV AL,0x1
# 005D3D7F   5F               POP EDI
# 005D3D80   5E               POP ESI
# 005D3D81   5B               POP EBX
# 005D3D82   C2 0400          RETN 0x4
# 005D3D85   CC               INT3
# 005D3D86   CC               INT3
# 005D3D87   CC               INT3
# 005D3D88   CC               INT3

# Here's the second function that matches the pattern
# 005D3D8E   CC               INT3
# 005D3D8F   CC               INT3
# 005D3D90   53               PUSH EBX
# 005D3D91   56               PUSH ESI
# 005D3D92   8B7424 0C        MOV ESI,DWORD PTR SS:[ESP+0xC]
# 005D3D96   57               PUSH EDI
# 005D3D97   8BF9             MOV EDI,ECX
# 005D3D99   837E 0C 00       CMP DWORD PTR DS:[ESI+0xC],0x0
# 005D3D9D   74 1C            JE SHORT .005D3DBB
# 005D3D9F   8B56 08          MOV EDX,DWORD PTR DS:[ESI+0x8]
# 005D3DA2   85D2             TEST EDX,EDX
# 005D3DA4   74 15            JE SHORT .005D3DBB
# 005D3DA6   8D4A 01          LEA ECX,DWORD PTR DS:[EDX+0x1]
# 005D3DA9   8DA424 00000000  LEA ESP,DWORD PTR SS:[ESP]
# 005D3DB0   8A02             MOV AL,BYTE PTR DS:[EDX]
# 005D3DB2   42               INC EDX
# 005D3DB3   84C0             TEST AL,AL
# 005D3DB5  ^75 F9            JNZ SHORT .005D3DB0
# 005D3DB7   2BD1             SUB EDX,ECX
# 005D3DB9   EB 02            JMP SHORT .005D3DBD
# 005D3DBB   33D2             XOR EDX,EDX
# 005D3DBD   8D5A 01          LEA EBX,DWORD PTR DS:[EDX+0x1]
# 005D3DC0   3B5F 0C          CMP EBX,DWORD PTR DS:[EDI+0xC]
# 005D3DC3   76 1A            JBE SHORT .005D3DDF
# 005D3DC5   53               PUSH EBX
# 005D3DC6   8D4F 04          LEA ECX,DWORD PTR DS:[EDI+0x4]
# 005D3DC9   C747 0C 00000000 MOV DWORD PTR DS:[EDI+0xC],0x0
# 005D3DD0   E8 DB700700      CALL .0064AEB0
# 005D3DD5   84C0             TEST AL,AL
# 005D3DD7   75 06            JNZ SHORT .005D3DDF
# 005D3DD9   5F               POP EDI
# 005D3DDA   5E               POP ESI
# 005D3DDB   5B               POP EBX
# 005D3DDC   C2 0400          RETN 0x4
# 005D3DDF   837E 0C 00       CMP DWORD PTR DS:[ESI+0xC],0x0
# 005D3DE3   75 04            JNZ SHORT .005D3DE9
# 005D3DE5   33C9             XOR ECX,ECX
# 005D3DE7   EB 03            JMP SHORT .005D3DEC
# 005D3DE9   8B4E 08          MOV ECX,DWORD PTR DS:[ESI+0x8]
# 005D3DEC   837F 0C 00       CMP DWORD PTR DS:[EDI+0xC],0x0
# 005D3DF0   75 15            JNZ SHORT .005D3E07
# 005D3DF2   53               PUSH EBX
# 005D3DF3   33C0             XOR EAX,EAX
# 005D3DF5   51               PUSH ECX
# 005D3DF6   50               PUSH EAX
# 005D3DF7   E8 549A0C00      CALL .0069D850
# 005D3DFC   83C4 0C          ADD ESP,0xC
# 005D3DFF   B0 01            MOV AL,0x1
# 005D3E01   5F               POP EDI
# 005D3E02   5E               POP ESI
# 005D3E03   5B               POP EBX
# 005D3E04   C2 0400          RETN 0x4
# 005D3E07   8B47 08          MOV EAX,DWORD PTR DS:[EDI+0x8]
# 005D3E0A   53               PUSH EBX
# 005D3E0B   51               PUSH ECX
# 005D3E0C   50               PUSH EAX
# 005D3E0D   E8 3E9A0C00      CALL .0069D850
# 005D3E12   83C4 0C          ADD ESP,0xC
# 005D3E15   B0 01            MOV AL,0x1
# 005D3E17   5F               POP EDI
# 005D3E18   5E               POP ESI
# 005D3E19   5B               POP EBX
# 005D3E1A   C2 0400          RETN 0x4
# 005D3E1D   CC               INT3
# 005D3E1E   CC               INT3
# 005D3E1F   CC               INT3
class System4Engine(Engine):

  NAME = "System44" # str, override
  ENCODING = SJIS_ENCODING # str, override

  DLLS = {
    'AliceRunPatch44': 'AliceRunPatch.dll',
  }

  def match(self, pid): # override
    return bool(self.globAppDirectory('AliceStart.ini', pid))

  def inject(self, pid): # override
    from gamedebugger import GameDebugger
    dbg = GameDebugger(pid)
    ret = False
    if dbg.active():
      # There are actually two matches of this pattern.
      # The first one is used
      # 005D3D75   E8 D69A0C00      CALL .0069D850    ; jichi: hooked here
      # 005D3D7A   83C4 0C          ADD ESP,0xC
      # 005D3D7D   B0 01            MOV AL,0x1
      # 005D3D7F   5F               POP EDI
      # 005D3D80   5E               POP ESI
      # 005D3D81   5B               POP EBX
      # 005D3D82   C2 0400          RETN 0x4
      # 005D3D85   CC               INT3
      # 005D3D86   CC               INT3
      # 005D3D87   CC               INT3
      # 005D3D88   CC               INT3

      # btw, here's the pattern for System43, that is almost the same as System44.
      # // i.e. 83c40c5f5eb0015bc20400cccc without leading 0xe8
      # const BYTE bytes[] = {
      #   0xe8, XX4,          //   005506a9  |. e8 f2fb1600    call rance01.006c02a0 ; hook here
      #   0x83,0xc4, 0x0c,    //   005506ae  |. 83c4 0c        add esp,0xc
      #   0x5f,               //   005506b1  |. 5f             pop edi
      #   0x5e,               //   005506b2  |. 5e             pop esi
      #   0xb0, 0x01,         //   005506b3  |. b0 01          mov al,0x1
      #   0x5b,               //   005506b5  |. 5b             pop ebx
      #   0xc2, 0x04,0x00,    //   005506b6  \. c2 0400        retn 0x4
      #   0xcc, 0xcc // patching a few int3 to make sure that this is at the end of the code block
      # };

      # Use 4 dots to represent the 8-bit calling address after e8
      pattern = re.compile(r'\xe8....\x83\xc4\x0c\xb0\x01\x5f\x5e\x5b\xc2\x04\x00\xcc\xcc')
      addr = dbg.search_module_memory(pattern)
      if addr > 0:
        ret = self._hook(addr, self.NAME)

      if ret:
        for name,dll in self.DLLS.iteritems():
          if self.globAppDirectory(dll, pid):
            addr = dbg.search_module_memory(pattern, dll)
            if addr > 0:
              self._hook(addr, name)
    dprint(ret)
    return ret

  def _hook(self, addr, name):
    """
    @param  addr  ulong
    @param  name  str
    @return  bool
    """
    code = "/HSN4:-14@%x" % addr # for system43, pick text from arg1 on the stack
    #code = "/HSN-1c:-14@%x" % addr # for system44, pick text from registers
    return self.addHook(code, self.NAME)

# 11/22/2015
# Sample game: 凍京NECRO 体験版
# Debug step:
# 1. find the text location that does not change
# 2. Use Ollydbg to find where the text is modified
# 3. Backtrack the stack to find proper caller.
#
#  Issues: It cannot extract character name.
#
# File pattern: *.npk for new "Nitroplus" (p is lower case)
# btw, *.npa for old "Nitroplus"
#
# 00CF0E6A   CC               INT3
# 00CF0E6B   CC               INT3
# 00CF0E6C   CC               INT3
# 00CF0E6D   CC               INT3
# 00CF0E6E   CC               INT3
# 00CF0E6F   CC               INT3
# 00CF0E70   55               PUSH EBP	; jichi: text in arg1
# 00CF0E71   8BEC             MOV EBP,ESP
# 00CF0E73   6A FF            PUSH -0x1
# 00CF0E75   68 184BDC00      PUSH .00DC4B18
# 00CF0E7A   64:A1 00000000   MOV EAX,DWORD PTR FS:[0]
# 00CF0E80   50               PUSH EAX
# 00CF0E81   64:8925 00000000 MOV DWORD PTR FS:[0],ESP
# 00CF0E88   83EC 1C          SUB ESP,0x1C
# 00CF0E8B   8B55 08          MOV EDX,DWORD PTR SS:[EBP+0x8]
# 00CF0E8E   53               PUSH EBX
# 00CF0E8F   56               PUSH ESI
# 00CF0E90   8BC2             MOV EAX,EDX
# 00CF0E92   57               PUSH EDI
# 00CF0E93   8BD9             MOV EBX,ECX
# 00CF0E95   C745 EC 0F000000 MOV DWORD PTR SS:[EBP-0x14],0xF
# 00CF0E9C   C745 E8 00000000 MOV DWORD PTR SS:[EBP-0x18],0x0
# 00CF0EA3   C645 D8 00       MOV BYTE PTR SS:[EBP-0x28],0x0
# 00CF0EA7   8D70 01          LEA ESI,DWORD PTR DS:[EAX+0x1]
# 00CF0EAA   8D9B 00000000    LEA EBX,DWORD PTR DS:[EBX]
# 00CF0EB0   8A08             MOV CL,BYTE PTR DS:[EAX]
# 00CF0EB2   40               INC EAX
# 00CF0EB3   84C9             TEST CL,CL
# 00CF0EB5  ^75 F9            JNZ SHORT .00CF0EB0
# 00CF0EB7   2BC6             SUB EAX,ESI
# 00CF0EB9   52               PUSH EDX
# 00CF0EBA   8BF8             MOV EDI,EAX
# 00CF0EBC   8D75 D8          LEA ESI,DWORD PTR SS:[EBP-0x28]
# 00CF0EBF   E8 0C0DF5FF      CALL .00C41BD0
# 00CF0EC4   C745 FC 00000000 MOV DWORD PTR SS:[EBP-0x4],0x0	; jichi: pattern start
# 00CF0ECB   8B8B 84030000    MOV ECX,DWORD PTR DS:[EBX+0x384]
# 00CF0ED1   8B01             MOV EAX,DWORD PTR DS:[ECX]
# 00CF0ED3   8B40 60          MOV EAX,DWORD PTR DS:[EAX+0x60]
# 00CF0ED6   8BD6             MOV EDX,ESI
# 00CF0ED8   52               PUSH EDX
# 00CF0ED9   FFD0             CALL EAX   ;jichi: called here  .00CAEF00
# 00CF0EDB   837D EC 10       CMP DWORD PTR SS:[EBP-0x14],0x10
# 00CF0EDF   5F               POP EDI
# 00CF0EE0   5E               POP ESI
# 00CF0EE1   5B               POP EBX
# 00CF0EE2   72 0C            JB SHORT .00CF0EF0
# 00CF0EE4   8B4D D8          MOV ECX,DWORD PTR SS:[EBP-0x28]
# 00CF0EE7   51               PUSH ECX
# 00CF0EE8   E8 ED060B00      CALL .00DA15DA
# 00CF0EED   83C4 04          ADD ESP,0x4
# 00CF0EF0   8B4D F4          MOV ECX,DWORD PTR SS:[EBP-0xC]
# 00CF0EF3   64:890D 00000000 MOV DWORD PTR FS:[0],ECX
# 00CF0EFA   8BE5             MOV ESP,EBP
# 00CF0EFC   5D               POP EBP
# 00CF0EFD   C2 0400          RETN 0x4
# 00CF0F00   8B89 84030000    MOV ECX,DWORD PTR DS:[ECX+0x384]
# 00CF0F06   8B01             MOV EAX,DWORD PTR DS:[ECX]
# 00CF0F08   8B50 64          MOV EDX,DWORD PTR DS:[EAX+0x64]
# 00CF0F0B   FFE2             JMP EDX
# 00CF0F0D   CC               INT3
# 00CF0F0E   CC               INT3
# 00CF0F0F   CC               INT3
# 00CF0F10   55               PUSH EBP
# 00CF0F11   8BEC             MOV EBP,ESP
# 00CF0F13   83EC 10          SUB ESP,0x10
# 00CF0F16   8B89 84030000    MOV ECX,DWORD PTR DS:[ECX+0x384]
# 00CF0F1C   8B01             MOV EAX,DWORD PTR DS:[ECX]
# 00CF0F1E   8B80 A0000000    MOV EAX,DWORD PTR DS:[EAX+0xA0]
# 00CF0F24   8D55 F0          LEA EDX,DWORD PTR SS:[EBP-0x10]
# 00CF0F27   52               PUSH EDX
# 00CF0F28   FFD0             CALL EAX
# 00CF0F2A   8D4D F8          LEA ECX,DWORD PTR SS:[EBP-0x8]
# 00CF0F2D   FF15 7482DC00    CALL DWORD PTR DS:[0xDC8274]                                                          ; _1nput1_.1007E880
# 00CF0F33   66:0F6E45 F0     MOVD MM0,DWORD PTR SS:[EBP-0x10]
# 00CF0F38   66:0F6E4D F4     MOVD MM1,DWORD PTR SS:[EBP-0xC]
# 00CF0F3D   8B0D E046E000    MOV ECX,DWORD PTR DS:[0xE046E0]
# 00CF0F43   0F5B             ???                                                                                   ; Unknown command
# 00CF0F45   C0F3 0F          SAL BL,0xF
# 00CF0F48   1145 F8          ADC DWORD PTR SS:[EBP-0x8],EAX
# 00CF0F4B   0F5B             ???                                                                                   ; Unknown command
# 00CF0F4D   C9               LEAVE
# 00CF0F4E   F3:0F114D FC     MOVSS DWORD PTR SS:[EBP-0x4],XMM1
# 00CF0F53   8B41 54          MOV EAX,DWORD PTR DS:[ECX+0x54]
# 00CF0F56   F3:0F1180 500100>MOVSS DWORD PTR DS:[EAX+0x150],XMM0
# 00CF0F5E   F3:0F1045 FC     MOVSS XMM0,DWORD PTR SS:[EBP-0x4]
# 00CF0F63   F3:0F1180 540100>MOVSS DWORD PTR DS:[EAX+0x154],XMM0
# 00CF0F6B   0F57C0           XORPS XMM0,XMM0
# 00CF0F6E   F3:0F1180 580100>MOVSS DWORD PTR DS:[EAX+0x158],XMM0
# 00CF0F76   F3:0F1180 5C0100>MOVSS DWORD PTR DS:[EAX+0x15C],XMM0
# 00CF0F7E   8BE5             MOV ESP,EBP
# 00CF0F80   5D               POP EBP
# 00CF0F81   C3               RETN
# 00CF0F82   CC               INT3
# 00CF0F83   CC               INT3
# 00CF0F84   CC               INT3
# 00CF0F85   CC               INT3
# 00CF0F86   CC               INT3
# 00CF0F87   CC               INT3
# 00CF0F88   CC               INT3
# 00CF0F89   CC               INT3
# 00CF0F8A   CC               INT3
# 00CF0F8B   CC               INT3
# 00CF0F8C   CC               INT3
#
# If the function does not work, here's the common function that performing strcpy
# 00DA8E8A   CC               INT3
# 00DA8E8B   CC               INT3
# 00DA8E8C   CC               INT3
# 00DA8E8D   CC               INT3
# 00DA8E8E   CC               INT3
# 00DA8E8F   CC               INT3
# 00DA8E90   55               PUSH EBP
# 00DA8E91   8BEC             MOV EBP,ESP
# 00DA8E93   57               PUSH EDI
# 00DA8E94   56               PUSH ESI
# 00DA8E95   8B75 0C          MOV ESI,DWORD PTR SS:[EBP+0xC]
# 00DA8E98   8B4D 10          MOV ECX,DWORD PTR SS:[EBP+0x10]
# 00DA8E9B   8B7D 08          MOV EDI,DWORD PTR SS:[EBP+0x8]
# 00DA8E9E   8BC1             MOV EAX,ECX
# 00DA8EA0   8BD1             MOV EDX,ECX
# 00DA8EA2   03C6             ADD EAX,ESI
# 00DA8EA4   3BFE             CMP EDI,ESI
# 00DA8EA6   76 08            JBE SHORT .00DA8EB0
# 00DA8EA8   3BF8             CMP EDI,EAX
# 00DA8EAA   0F82 A0010000    JB .00DA9050
# 00DA8EB0   81F9 80000000    CMP ECX,0x80
# 00DA8EB6   72 1C            JB SHORT .00DA8ED4
# 00DA8EB8   833D D470E000 00 CMP DWORD PTR DS:[0xE070D4],0x0
# 00DA8EBF   74 13            JE SHORT .00DA8ED4
# 00DA8EC1   57               PUSH EDI
# 00DA8EC2   56               PUSH ESI
# 00DA8EC3   83E7 0F          AND EDI,0xF
# 00DA8EC6   83E6 0F          AND ESI,0xF
# 00DA8EC9   3BFE             CMP EDI,ESI
# 00DA8ECB   5E               POP ESI
# 00DA8ECC   5F               POP EDI
# 00DA8ECD   75 05            JNZ SHORT .00DA8ED4
# 00DA8ECF  ^E9 0E9FFFFF      JMP .00DA2DE2
# 00DA8ED4   F7C7 03000000    TEST EDI,0x3
# 00DA8EDA   75 14            JNZ SHORT .00DA8EF0
# 00DA8EDC   C1E9 02          SHR ECX,0x2
# 00DA8EDF   83E2 03          AND EDX,0x3
# 00DA8EE2   83F9 08          CMP ECX,0x8
# 00DA8EE5   72 29            JB SHORT .00DA8F10
# 00DA8EE7   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]	; jichi: modified here
# 00DA8EE9   FF2495 0090DA00  JMP DWORD PTR DS:[EDX*4+0xDA9000]
# 00DA8EF0   8BC7             MOV EAX,EDI
# 00DA8EF2   BA 03000000      MOV EDX,0x3
# 00DA8EF7   83E9 04          SUB ECX,0x4
# 00DA8EFA   72 0C            JB SHORT .00DA8F08
# 00DA8EFC   83E0 03          AND EAX,0x3
# 00DA8EFF   03C8             ADD ECX,EAX
# 00DA8F01   FF2485 148FDA00  JMP DWORD PTR DS:[EAX*4+0xDA8F14]
# 00DA8F08   FF248D 1090DA00  JMP DWORD PTR DS:[ECX*4+0xDA9010]
# 00DA8F0F   90               NOP
# 00DA8F10   FF248D 948FDA00  JMP DWORD PTR DS:[ECX*4+0xDA8F94]
# 00DA8F17   90               NOP
# 00DA8F18   24 8F            AND AL,0x8F
# 00DA8F1A   DA00             FIADD DWORD PTR DS:[EAX]
# 00DA8F1C   50               PUSH EAX
# 00DA8F1D   8F               ???                                                                                   ; Unknown command
# 00DA8F1E   DA00             FIADD DWORD PTR DS:[EAX]
# 00DA8F20  ^74 8F            JE SHORT .00DA8EB1
# 00DA8F22   DA00             FIADD DWORD PTR DS:[EAX]
# 00DA8F24   23D1             AND EDX,ECX
# 00DA8F26   8A06             MOV AL,BYTE PTR DS:[ESI]
# 00DA8F28   8807             MOV BYTE PTR DS:[EDI],AL
# 00DA8F2A   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
# 00DA8F2D   8847 01          MOV BYTE PTR DS:[EDI+0x1],AL
# 00DA8F30   8A46 02          MOV AL,BYTE PTR DS:[ESI+0x2]
# 00DA8F33   C1E9 02          SHR ECX,0x2
# 00DA8F36   8847 02          MOV BYTE PTR DS:[EDI+0x2],AL
# 00DA8F39   83C6 03          ADD ESI,0x3
# 00DA8F3C   83C7 03          ADD EDI,0x3
# 00DA8F3F   83F9 08          CMP ECX,0x8
# 00DA8F42  ^72 CC            JB SHORT .00DA8F10
# 00DA8F44   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]
# 00DA8F46   FF2495 0090DA00  JMP DWORD PTR DS:[EDX*4+0xDA9000]
# 00DA8F4D   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
# 00DA8F50   23D1             AND EDX,ECX
# 00DA8F52   8A06             MOV AL,BYTE PTR DS:[ESI]
# 00DA8F54   8807             MOV BYTE PTR DS:[EDI],AL
# 00DA8F56   8A46 01          MOV AL,BYTE PTR DS:[ESI+0x1]
# 00DA8F59   C1E9 02          SHR ECX,0x2
# 00DA8F5C   8847 01          MOV BYTE PTR DS:[EDI+0x1],AL
# 00DA8F5F   83C6 02          ADD ESI,0x2
# 00DA8F62   83C7 02          ADD EDI,0x2
# 00DA8F65   83F9 08          CMP ECX,0x8
# 00DA8F68  ^72 A6            JB SHORT .00DA8F10
# 00DA8F6A   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]
# 00DA8F6C   FF2495 0090DA00  JMP DWORD PTR DS:[EDX*4+0xDA9000]
# 00DA8F73   90               NOP
# 00DA8F74   23D1             AND EDX,ECX
# 00DA8F76   8A06             MOV AL,BYTE PTR DS:[ESI]
# 00DA8F78   8807             MOV BYTE PTR DS:[EDI],AL
# 00DA8F7A   83C6 01          ADD ESI,0x1
# 00DA8F7D   C1E9 02          SHR ECX,0x2
# 00DA8F80   83C7 01          ADD EDI,0x1
# 00DA8F83   83F9 08          CMP ECX,0x8
# 00DA8F86  ^72 88            JB SHORT .00DA8F10
# 00DA8F88   F3:A5            REP MOVS DWORD PTR ES:[EDI],DWORD PTR DS:[ESI]
# 00DA8F8A   FF2495 0090DA00  JMP DWORD PTR DS:[EDX*4+0xDA9000]
# 00DA8F91   8D49 00          LEA ECX,DWORD PTR DS:[ECX]
# 00DA8F94   F7               ???                                                                                   ; Unknown command
# 00DA8F95   8F               ???                                                                                   ; Unknown command
# 00DA8F96   DA00             FIADD DWORD PTR DS:[EAX]
# 00DA8F98   E4 8F            IN AL,0x8F                                                                            ; I/O command
# 00DA8F9A   DA00             FIADD DWORD PTR DS:[EAX]
# 00DA8F9C   DC8F DA00D48F    FMUL QWORD PTR DS:[EDI+0x8FD400DA]
# 00DA8FA2   DA00             FIADD DWORD PTR DS:[EAX]
# 00DA8FA4   CC               INT3
# 00DA8FA5   8F               ???                                                                                   ; Unknown command
# 00DA8FA6   DA00             FIADD DWORD PTR DS:[EAX]
# 00DA8FA8   C48F DA00BC8F    LES ECX,FWORD PTR DS:[EDI+0x8FBC00DA]                                                 ; Modification of segment register
# 00DA8FAE   DA00             FIADD DWORD PTR DS:[EAX]
# 00DA8FB0   B4 8F            MOV AH,0x8F
class NitroplusEngine(Engine):

  NAME = "Nitroplus2" # str, override
  ENCODING = SJIS_ENCODING # str, override

  def match(self, pid): # override
    return bool(self.globAppDirectory('*.npk', pid))

  def inject(self, pid): # override
    from gamedebugger import GameDebugger
    dbg = GameDebugger(pid)
    ret = False
    if dbg.active():
      # 00CF0EC4   C745 FC 00000000 MOV DWORD PTR SS:[EBP-0x4],0x0	; jichi: pattern start
      # 00CF0ECB   8B8B 84030000    MOV ECX,DWORD PTR DS:[EBX+0x384]
      # 00CF0ED1   8B01             MOV EAX,DWORD PTR DS:[ECX]
      # 00CF0ED3   8B40 60          MOV EAX,DWORD PTR DS:[EAX+0x60]
      # 00CF0ED6   8BD6             MOV EDX,ESI
      # 00CF0ED8   52               PUSH EDX
      # 00CF0ED9   FFD0             CALL EAX   ;jichi: called here  .00CAEF00
      pattern = 0xc745fc000000008b8b840300008b018b40608bd652ffd0

      addr = dbg.search_module_memory(pattern)
      if addr > 0:
        # Should use find enclosing function, which is more stable then using a fixed offset
        addr += 0x00CF0E70 - 0x00CF0EC4
        # type: NO_CONTEXT (N) | USING_STRING(S) | FIXING_SPLIT(F) | NO_ASCII(J)
        # offset: 4 (arg1)
        code = "/HSNFJ4@%x" % addr
        ret = self.addHook(code)
    dprint(ret)
    return ret

# EOF

# 4/27/2015
# See also GXP comments in engine.cc
#
# Sample game: ウルスラグナ
# Debug step:
# 1. find the following location
#    00A78144   66:833C70 00     CMP WORD PTR DS:[EAX+ESI*2],0x0
#    i.e. 0x66833C7000
#    There are several matches, the first one is used.
# 2. Use Ollydbg to debug step by step until the first function call is encountered
#    Then, the text character is directly on the stack
#
#  Issues: It cannot extract character name.
#
#  00A7883A   24 3C            AND AL,0x3C
#  00A7883C   50               PUSH EAX
#  00A7883D   C74424 4C 000000>MOV DWORD PTR SS:[ESP+0x4C],0x0
#  00A78845   0F5B             ???                                      ; Unknown command
#  00A78847   C9               LEAVE
#  00A78848   F3:0F114424 44   MOVSS DWORD PTR SS:[ESP+0x44],XMM0
#  00A7884E   F3:0F114C24 48   MOVSS DWORD PTR SS:[ESP+0x48],XMM1
#  00A78854   E8 37040000      CALL .00A78C90  ; jichi: here's the target function to hook to, text char on the stack[0]
#  00A78859   A1 888EDD00      MOV EAX,DWORD PTR DS:[0xDD8E88]
#  00A7885E   A8 01            TEST AL,0x1
#  00A78860   75 30            JNZ SHORT .00A78892
#  00A78862   83C8 01          OR EAX,0x1
#  00A78865   A3 888EDD00      MOV DWORD PTR DS:[0xDD8E88],EAX
#
# 5/2/2015: Alternative H-code for the full game: /HWN-4@48806:verethragna.exe
# Try this one if GXP2 fails.
#class GXPEngine(Engine):
#
#  NAME = "GXP2" # str, override
#  ENCODING = UTF16_ENCODING # str, override
#
#  def match(self, pid): # override
#    return bool(self.globAppDirectory('*.gxp', pid))
#
#  def inject(self, pid): # override
#    from gamedebugger import GameDebugger
#    dbg = GameDebugger(pid)
#    ret = False
#    if dbg.active():
#      #  00A78845   0F5B             ???                                      ; Unknown command
#      #  00A78847   C9               LEAVE
#      #  00A78848   F3:0F114424 44   MOVSS DWORD PTR SS:[ESP+0x44],XMM0
#      #  00A7884E   F3:0F114C24 48   MOVSS DWORD PTR SS:[ESP+0x48],XMM1
#      #  00A78854   E8 37040000      CALL .00A78C90  ; jichi: here's the target function to hook to, text char on the stack[0]
#      pattern = 0x0f5bc9f30f11442444f30f114c2448e8
#      addr = dbg.search_module_memory(pattern)
#      if addr > 0:
#        addr += 0x00A78854 - 0x00A78845
#        # type: USING_UNICODE(W) | NO_CONTEXT (N) | DATA_INDIRECT(*) | FIXING_SPLIT(F)
#        # length_offset: 1
#        code = "/HWNF*@%x" % addr
#        ret = self.addHook(code)
#    dprint(ret)
#    return ret

# 5/8/2015
# Sample game: イブニクル version 1.0.1
# It is basically the same System43 engine but code moved to AliceRunPatch.dll
#
# See System43 in engine.cc
#   // 9/25/2014 TODO: I should use matchBytes and replace the part after e8 with XX4
#   // i.e. 83c40c5f5eb0015bc20400cccc without leading 0xe8
#   const BYTE ins[] = {  //   005506a9  |. e8 f2fb1600    call rance01.006c02a0 ; hook here
#     0x83,0xc4, 0x0c,    //   005506ae  |. 83c4 0c        add esp,0xc
#     0x5f,               //   005506b1  |. 5f             pop edi
#     0x5e,               //   005506b2  |. 5e             pop esi
#     0xb0, 0x01,         //   005506b3  |. b0 01          mov al,0x1
#     0x5b,               //   005506b5  |. 5b             pop ebx
#     0xc2, 0x04,0x00,    //   005506b6  \. c2 0400        retn 0x4
#     0xcc, 0xcc // patching a few int3 to make sure that this is at the end of the code block
#   };
#   enum { hook_offset = -5 }; // the function call before the ins
#
#   HookParam hp = {};
#   hp.addr = addr;
#   hp.off = 4;
#   hp.split = -0x18;
#   hp.type = NO_CONTEXT|USING_SPLIT|USING_STRING;
#
# TODO: Add alternative hook with character name
# See: http://capita.tistory.com/m/post/256
#   004EEB30   8BCF             MOV ECX,EDI
#   004EEB32   881E             MOV BYTE PTR DS:[ESI],BL
#   004EEB34   E8 67CB0100      CALL .0050B6A0  ; jichi: hook here
#   004EEB39   396C24 28        CMP DWORD PTR SS:[ESP+0x28],EBP
#   004EEB3D   72 0D            JB SHORT .004EEB4C
#class System43Engine(Engine):
#
#  NAME = "AliceRunPatch" # str, override
#  ENCODING = SJIS_ENCODING # str, override
#
#  DLL = 'AliceRunPatch.dll'
#  def match(self, pid): # override
#    return bool(self.exists(self.DLL, pid))
#
#  def inject(self, pid): # override
#    from gamedebugger import GameDebugger
#    dbg = GameDebugger(pid)
#    ret = False
#    if dbg.active():
#      # Use 4 dots to represent the 8-bit calling address after e8
#      pattern = re.compile(r'\xe8....\x83\xc4\x0c\x5f\x5e\xb0\x01\x5b\xc2\x04\x00\xcc\xcc')
#      addr = dbg.search_module_memory(pattern, self.DLL)
#      if addr > 0:
#        code = "/HSN4:-14@%x" % addr
#        ret = self.addHook(code)
#    dprint(ret)
#    return ret

# jichi 10/4/2013: Unity3D
# See (ok123): http://9baka.com/read.php?tid=411756
#class UnityEngine(Engine):
#
#  NAME = "Unity" # str
#
#  def match(self, pid): # override
#    return bool(self.globAppDirectory(pid,
#        '*/Managed/UnityEngine.dll'))
#
#  def inject(self, pid): # override
#    from gamedebugger import GameDebugger
#    dbg = GameDebugger(pid)
#    ret = False
#    if dbg.active():
#      #pattern = 0x90, 0xff, 0x50, 0x3c, 0x83, 0xc4, 0x20, 0x8b, 0x45, 0xec
#      #addr = dbg.searchbytes(pattern)
#      pattern = 0x90ff503c83c4208b45ec
#      length = 0x15000000   # it is usually around 0x7000000. larger enough to cover BALDRSKY ZERO
#      addr = dbg.searchhex(pattern, length=length)
#      if addr > 0:
#        code = "/HQN4@%x" % addr
#        from texthook import texthook
#        th = texthook.global_()
#        ret = th.addHook(code, name=self.NAME)
#    dprint(ret)
#    return ret

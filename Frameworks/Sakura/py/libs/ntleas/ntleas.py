# coding: utf8
# ntleas.py
# 8/17/2014
# See http://ntlea.codeplex.com/

# See: ntleas/Tools/ntlea/ntleas/ntleas.c
#
# if (argv && argc > 1) {
#   ret = CreateProcessBeginW(&ntproc, (pApplicationName=argv[1]));
#   for (int i = 2; i < argc; ++i) {
#     switch (argv[i][0]) {
#     case 'P': ntproc.dwCompOption = GetParameterValue(argv[i] + 1); break;
#     case 'C': ntproc.dwCodePage = GetParameterValue(argv[i] + 1); break;
#     case 'L': ntproc.dwLCID = GetParameterValue(argv[i] + 1); break;
#     case 'T': ntproc.dwTimeZone = GetParameterValue(argv[i] + 1); break;
#     case 'S': ntproc.dwSpApp = GetParameterValue(argv[i] + 1); break;
#     case 'F': WideCharToMultiByte(CP_ACP, 0, GetParameterString(argv[i] + 1, FALSE), -1,
#       (LPSTR)ntproc.FontFaceName, sizeof(ntproc.FontFaceName), NULL, NULL); break; // only ansi string accept ??
#     case 'A': pCommandLine = MkCommandLine(argv[1], GetParameterString(argv[i] + 1, TRUE), TRUE); break;
#     // ----- inner ----- //
#     case 'M': rcpHookDll[1 + 5] = (argv[i] + 1)[0]; break;
#     case 'D': dbg = GetParameterValue(argv[i] + 1); break;
#     case 'W': dir = GetParameterValue(argv[i] + 1); break;
#     case 'Q': qit = GetParameterValue(argv[i] + 1); break;
#     default: /* unknown indicator ! */ break;
#     }
#   }
# }

# The following code is currently exactly the same as ntleas.exe.
# Example: ntleas.exe "d:\test\game.exe" "A-G 123 -B 456" "P0" "C932" "L1041" "T-540" "FMS Gothic" "S200"
def params(
    path=None,      # unicode, process path
    args=None,      # [unicode], process parameters
    compat=None,    # int, P parameter, windows compatibility level
    codepage=932,   # int, C parameter
    locale=0x411,   # int, L parameter, locale (0x411 = 1041)
    timezone=-540,  # int, T parameter
    font="MS Gothic",   # unicode, F parameter, font family
    size=None,      # int, S parameter, resize percentage
  ):
  """
  @return  [unicode]
  """
  ret = []
  if path is not None:
    #try: path = win32api.GetShortPathName(path)
    #except Exception, e: dwarn(e) # path does not exist
    ret.append(path)
  if args is not None:
    ret.append('A"%s"' % '" "'.join(args)) # quoted
  if compat is not None:    ret.append("P%i" % compat)
  if codepage is not None:  ret.append("C%i" % codepage)
  if locale is not None:    ret.append("L%i" % locale)
  if timezone is not None:  ret.append("T%i" % timezone)
  if font is not None:      ret.append("F%s" % font)
  if size is not None:      ret.append("S%i" % size)
  return ret

# EOF

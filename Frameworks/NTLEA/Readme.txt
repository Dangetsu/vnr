Product Name :

NT Locale Emulator Advance (NT全域通)  short for NTLEA


Component Description:

NtleaGUI.exe			-	NTLEA GUI shell and shortcut launcher
NTLEA_Menu.dll			-	NTLEA GUI Shell Extension module
NtleaManager.dll		-	NTLEA GUI runtime library
Interop.IWshRuntimeLibrary.dll	-	Microsoft .NET ActiveX runtime library
RegAsm.com			-	Microsoft .NET Assembly Registration Utility
Uninstall.com			-	Expeditious uninstaller
ntleac.exe			-	NTLEA core launcher
ntleah.dll			-	NTLEA remote injection DLL


注意事项:
1、如果出现了无法启动任何exe之类的严重问题，请双击Uninstall.com来紧急卸载
2、如果系统开启了UAC，那么安装和卸载、以及设置是否自动托管.exe文件的时候，需要右键选择“以管理员身份运行”，其他时候不需要


Version & Update History :

NTLEA Core & GUI 0.92  2011.06.09  by magami
1、修正快捷方式的右键菜单所有选项失效的问题
2、修正了开启UAC的环境下无法以管理员身份使用Uninstall.com卸载的问题

NTLEA Core & GUI 0.91b  2011.05.12  by magami
1、因为.bat批处理文件还是无法干净的卸载程序，于是把紧急卸载程序改为了Uninstall.com
2、修正了0.91a在winXP下会导致窗口卡死CPU占用100%的情况，已经出了问题的请先运行新的Uninstall.com卸载一次

NTLEA Core & GUI 0.91a  2011.05.10  by magami
修正『通常模式』的一个BUG，大幅提升了兼容性
现在穢翼のユースティア、神採りアルケミーマイスター(包括防弹窗补丁)等都能使用默认的通常模式直接启动了

NTLEA Core & GUI 0.91  2011.05.09  by magami
新增特性:
1、自动接管.exe的启动改为了可选选项，在非托管的情况下，选择.exe文件右键菜单中的 ntlea 为使用预选或自动识别的语言来启动程序
2、修正了64位系统下无法正常安装的问题
3、修正了右键启动路径中含有空格的文件时异常报错的问题
4、修正了右键无法以预设语言启动非执行文件的问题
5、提高了兼容性，支持更多的程序了
6、启动文件分为了高兼容性的『通常模式』(默认)与针对特殊程序使用的『强制模式』两种模式，当通常『通常模式』无法正常启动文件时请尝试在文件区域设置界面中选择『强制模式』
注意:如果系统开启了UAC，那么安装和卸载、以及设置是否自动托管.exe文件的时候，需要右键选择“以管理员身份运行”，其他时候不需要

NTLEA Core & GUI 0.90  2011.05.08  by magami
主要为了解决VISTA和win7下的兼容问题而更新，使用了.net 3.5重写了GUI
支持64位操作系统下的32位程序，但不支持64位程序
如果winXP系统用户要使用，需要安装.net framework 3.5
新增特性:
1、双击exe会自动判断是否采用NTLEA加载程序
2、能自动识别exe语言(可能会误判，误判大多发生在汉化的程序或游戏)，也就是说多数情况下不用设置NTLEA，直接双击要启动的程序就可以了
3、如果误判或无法自动识别，请使用右键菜单 NTLEA->创建或修改"xxx"的区域语言设置 来设置exe的语言，设置后会在当前目录生成一个和exe同名的.ntconfig文件，以后双击这个exe就会以设置的语言来运行了，此功能只会出现在exe文件的右键菜单中
4、右键菜单中的 在指定语言区域中加载 "xxx"... 为临时的打开方式，不会影响下次双击启动的语言，此菜单的下级菜单中能选择的语言列表请直接运行NtleaGUI.exe来管理
5、如果路径中有所选择的语言不支持的字符，会自动提示
6、若要不托管给NTLEA，直接启动程序，请单击右键菜单里的 打开(O)
7、界面语言为自动识别当前系统的语言，如果没有找到对应当前系统语言的语言文件则会加载en-us.xml，如果也没有找到en-us.xml则会启用内置的语言。要增加界面语言，请按照其他语言文件的格式编写好语言文件后放入Language目录，文件命名规则为 "语言代号缩写-国家代号缩写.xml"
重要:如果出现了无法启动任何exe之类的严重问题，请双击Uninstall.bat来紧急卸载

NTLEA Core 0.87 Beta  09.7.24  by LOVEHINA-AVC
临时增加对Windows7的支持

注意：开启UAC（用户帐户控制）将影响NTLEA的部分功能

Windows7 x86下，使用GUI需要手动注册galstars.dll
Windows7 x64下，GUI无法正常工作

NTLEA Core 0.86 Beta  07.6.13  by LOVEHINA-AVC
增加对GetSystemDefaultUILanguage及GetUserDefaultUILanguage函数的挂钩
改善了Computer-based Training钩子的挂钩方式
修正了其他一些细小的BUG

NTLEA Core 0.85 Beta  07.6.9  by LOVEHINA-AVC
增加让NTLEA加载的应用程序不受系统SDB补丁机制影响的功能
修正了其他一些细小的BUG

NTLEA Core 0.83 Beta  07.6.8  by LOVEHINA-AVC
修正了之前的版本不能让含有特殊字符路径的应用程序正常工作的问题
修正了其他一些细小的BUG

NTLEA GUI Launcher 1.0 Final  07.6.7  by magami
增加多语系界面支持与对应的区码（目前支持简体中文、繁体中文及英文）

NTLEA Core 0.82 Beta  07.6.7  by LOVEHINA-AVC
修正了在一部分程序下执行会发生初始化失败的问题
完善了跨进程跟踪注入的功能
增加直接打开任意扩展名文件的功能（注：若系统中启用了Microsoft Applocale，msi安装程序将无法被NTLEA正确加载）

0.80 beta  07.6.4

中文名称更改为“NT全域通”
修正了对话框处理函数不能被正确挂钩的问题
修正了因错误地址传递导致应用程序启动失败的问题
修正了一部分程序不能使用IME标准输入法的问题
修正了0.72~0.75版不能在Windows 2000及Windows XP SP0 SP1下运行的问题
增加WM_CHAR及WM_IME_CHAR消息的处理模块，修正了输入框文字不能被正确显示及文字不能被正确输入的问题
消除了数个读零地址非法操作的诱发因素
改进了消息钩子的处理方式
增加应用程序参数指定的支持（详见命令行选项说明）
增加重新指定字体大小的功能（详见命令行选项说明）
修正了Core Launcher（NTLEAC）不能引导一部分程序的问题
修正了多个细小的BUG

0.75 beta  07.1.10
修正了0.73版不能支持某些Unicode/ANSI混合型应用程序的问题
ntleac命令行模式“F”选项实装（注：若要强制指定应用程序所使用的字体，则至少需追加“P4”选项）
增加LB_GETTEXTLEN消息的处理模块（感谢Yoxola提供兼容性问题报告）

0.73 beta  06.12.16
修正了一部分程序在通过系统模版创建窗口时无法被正确挂钩的问题

0.72 beta  06.12.4
修正了在Visual C++ MFC框架程序中会产生乱码的兼容性问题
修正了在调用对话框模版函数后程序运行不正常的问题
增加对kernel32!CreateProcessW函数的挂勾

0.70 beta  06.11.30
增加以下针对窗口及消息处理函数的挂钩：
user32!SetWindowTextA
user32!GetWindowTextA
user32!SendMessageA
user32!SendMessageTimeoutA
user32!SendMessageCallbackA
user32!SendNotifyMessageA
user32!PostMessageA
user32!GetWindowLongA
user32!SetWindowLongA
user32!DefDlgProcA
user32!DefFrameProcA
user32!DefMDIChildProcA
user32!DialogBoxParamA
user32!DialogBoxIndirectParamA
user32!CreateDialogParamA
user32!CreateDialogIndirectParamA

增加其它的一些函数的挂钩：
user32!GetMenuStringA
user32!GetMenuItemInfoA
user32!SetMenuItemInfoA
kernel32!CharPrevA
kernel32!CharNextA
kernel32!IsDBCSLeadByte
gdi32!EnumFontFamiliesExA
gdi32!CreateFontIndirectA

增加自定义右键启动菜单的功能
增加指定预设字体的功能

0.52 beta  06.10.14
增加对user32!CreateWindowExA函数的挂钩
增加对user32!DefWindowProcA函数的挂钩
修正了VerQueryValueA挂钩函数在Windows XP SP0及SP1下会导致无效内存访问异常的问题

0.50 beta  06.10.12
增加对kernel32!GetCommandLineA函数的挂钩
修正了ntdll!RtlUnicodeToMultibyteN挂钩函数中一个重大的BUG，解决了大部分程序的兼容性问题

0.20 beta  06.10.9
增加针对特定应用程序的支持选项
重写部分函数，提高了挂勾程序的兼容性
修正数个小BUG

0.17 beta  06.9.30
再次（？）完善了kernel32!CreateProcessA挂钩函数的功能

0.16 beta  06.9.28
修正在目标程序调用version!VerQueryValueA时可能构成死循环的BUG

0.15 beta  06.9.27
增加对kernel32!GetTimeZoneInformation函数的挂钩，新增时区修正参数
增加对version!VerQueryValueA函数的挂勾
增加对Windows XP SP0操作系统的支持
新增一个兼容性选项
去除了不必要的语言ID参数
完善了kernel32!CreateProcessA挂钩函数的功能

0.11 beta  06.9.25
启动程序ntleac.exe与挂钩程序ntleah.dll由ANSI版本转变为Unicode版

注：如果在使用NTLEA外壳时发现程序无法启动，可尝试直接运行ntleac.exe


附：ntleac参数说明（第一个参数必须包含双引号）：

1. "x:\xxxxx\xxx.exe"
说明：目标程序路径。该参数必须位于第一项。

2. "Px"
说明：指定兼容性选项。x为描述兼容性开关的数值，每一个位域指定一个选项（注）。例如，当x为1时，第1个兼容性选项将被开启；当x为8时，第4个兼容性选将被开启；当x为7时，前3个兼容性选项均被开启（1 | 2 | 4 = 7）。

注：这里所说的位域是指二进制数的数位，一个整数最多拥有32个位域，第x位域的值等于2的x次方。

3. "Cx"
说明：指定页码。x为页码ID。

4. "Lx"
说明：指定语言。x为语言区域ID。

5. "Tx"
说明：指定时区修正。x为UTC时区修正数值，单位是分钟。

6. "Fxxx"
说明：指定预设字体，xxx为字体名称。

7. "Axxx"
说明：指定将要传给目标应用程序的参数，xxx为参数内容。

8. "Sx"
说明：指定字体的收放比率，x为比值，单位是百分率。

示例：

ntleac.exe "d:\test\game.exe" "A-G 123 -B 456" "P0" "C932" "L1041" "T-540" "FMS Gothic" "S200"

执行结果为启动“d:\test\game.exe -G 123 -B 456”，并设置页码为932（日文Shift-JIS），语言区域为日本，字体为“MS Gothic”，以两倍的大小显示，时区为东9区（GMT + 9:00或UTC - 9:00）。

（注：如果参数中包含双引号，则可用单引号来代替。如上例的"A-G 123 -B 456"，追加双引号后可书写为"A'-G 123' '-B 456'"）


0.10 beta  06.9.25
正式更名为NT Locale Emulator Advance
增加具有图形界面的外壳程序
增加跨进程跟踪功能

0.05 beta  06.9.24
修正了0.04 beta无法在Windows 2000及XP SP1下运行的问题

0.04 beta  06.9.24
增加对kernel32!CompareStringA函数的挂钩
增加对ntdll!RtlUnicodeToMultibyteN函数的挂钩

0.03 beta  06.9.24
增加对kernel32!CreateFileA函数的本地化支持
修正了前一个版本在多处理器系统中可能出现的兼容性问题

0.02 beta  06.9.23
修正了无法在Windows XP SP1下运行的问题

0.01 beta  06.9.22
最初的版本


FAQs

Q：这个工具能够做什么？
A：区域模拟，以及内码转换。一些应用程序可能无法在其它的区域模拟软件下正常运行，因此我编写了这个工具，以避免手工转换系统语言区域所带来的麻烦。

Q：它的兼容性如何？
A：该程序能够在Windows 2000 SP4/XP及2003 SP1下正常工作，但它很可能不支持Windows 2000 SP3及更低的版本。（注意，当前的版本不支持Windows 20003 Gold、即SP0）

目前已测试可以支持的操作系统详细列表：

Windows 2000 SP4
Windows XP
Windows XP SP1
Windows XP SP2
Windows Server 2003 SP1
Windows XP x64 Edition
Windows Vista

Q：使用这个工具时需要安装额外的软件吗？
A：不需要。同时这个程序也是绿色软件。

Q：我看到了两个可执行文件，应该怎样使用它们？
A：直接运行ntleac.exe，或者为它建立一个快捷方式，并在命令行的末尾填上目标程序的全路径名。关于参数的详细说明请参考附录，在新的版本中您还可以使用名为NTLEAGUI的外壳程序。

Q：我可以与他人分享这个软件吗？
A：是的，您可以自由转载这个程序，但请务必保持其完整，且不要修改任何内容。


About :

NTLEA Core Launcher & Core DLL

NTLEA GUI Launcher Simple

by  LOVEHINA-AVC  All rights reserved

NTLEA GUI Launcher Deluxe (Locale Switch Master for SoraApp & NTLEA)

by  magami  All rights reserved


Email : ilovehina@hotmail.com    magami_nanaya@hotmail.com
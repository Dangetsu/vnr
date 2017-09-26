' update.vbs
' jichi 3/1/2014
'
' Examples:
' http://msdn.microsoft.com/ja-jp/library/cc364428.aspx

Const APP = "update.hta"

'Dim shell
Set shell = WScript.CreateObject("WScript.Shell")

title = "Software Update"

' Multiple string: http://msdn.microsoft.com/en-us/library/5chcthbw%28v=vs.90%29.aspx
text = "Do you want to update VNR? (Internet access is needed)"
' FIXME: UTF-8 string is not supported in VBS?
'       "VNRを更新しますか？（インターネット接続が必要です）" & VbCrLf & _
'       "要現在更新VNR嗎？（需要網絡連接）" & VbCrLf & _
'       "要现在更新VNR吗？（需要网络连接）"

' 0: Wait for 0 seconds
' 4 + 32: Yes|No + '?' icon
sel = shell.Popup(text, 0, title, 4 + 32)

Select Case sel
  'Case 7 ' no
  '  WScript.Echo "No"
  Case 6 ' yes
    ' Run: http://msdn.microsoft.com/en-us/library/d5fk67ky%28v=vs.84%29.aspx
    'shell.Run(APP), 1, True ' True: wait
    shell.Run(APP), 1
End Select

'shell.Quit

' EOF

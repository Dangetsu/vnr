// update.js
// jichi 3/1/2014
// Examples:
// http://sugamasao.hatenablog.com/entry/20081130/1228066957

var APP_PATH = "update.hta";
var fso = WScript.CreateObject("Scripting.FileSystemObject");
var shell = WScript.CreateObject("WScript.Shell");

function chcwd() {
  // http://blogs.technet.com/b/heyscriptingguy/archive/2006/04/05/how-can-i-determine-the-path-to-the-folder-where-a-script-is-running.aspx
  var file = fso.GetFile(WScript.ScriptFullName);
  var pwd = fso.GetParentFolderName(file);
  //var pwd = shell.CurrentDirectory;
  shell.CurrentDirectory = pwd;
}
chcwd();

function check() { // -> bool
  if (fso.FileExists(APP_PATH))
    return true;
  WScript.Echo("Error: File does not exist!\n\n" + APP_PATH);
  return false;
}
if (!check())
  WScript.Quit();

function prompt() { // -> bool
  var title = "Software Update";
  var text = "Do you want to update VNR? (Internet access is needed)";
  // FIXME: UTF-8 string is not supported in WSH?
  //       "VNRを更新しますか？（インターネット接続が必要です）"
  //       "要現在更新VNR嗎？（需要網絡連接）"
  //       "要现在更新VNR吗？（需要网络连接）"

  // 0: Wait for 0 seconds
  // 4 + 32: Yes|No + '?' icon
  var POPUP_YES = 6;
  var POPUP_NO = 7;
  var sel = shell.Popup(text, 0, title, 4 + 32);
  return sel == POPUP_YES;
}
if (prompt())
  shell.Run(APP_PATH, 1); // http://msdn.microsoft.com/en-us/library/d5fk67ky%28v=vs.84%29.aspx

// EOF

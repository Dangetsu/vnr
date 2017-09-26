You can find some helper scripts in this directory.
You can double-click the file to run the script.

你可以雙擊腳本文件來執行它的。
击脚本文件来执行它的。

* Visual Novel Reader (Debug).cmd
Run VNR with debug output.
If VNR crashes or malfunctions, this might output the error causing the issue.

運行VNR並顯示調試信息。
如果VNR崩潰了或者出處了，在這裡也許可以找到原因的。

* Update (Debug).cmd
Update VNR with debug output.
更新VNR并显示调试信息。

* Kill Python.cmd
Kill all python instances, including VNR's.
關閉包括VNR在內的所有Python的程序。

* Remove VNR Profiles.cmd
Delete VNR's user profiles as follows.
Local game settings, text settings, voice settings, and caches will be deleted.

    %APPDATA%/org.sakuradite.*

刪除上面路徑中VNR的配置文件。
本地保存的遊戲情報，文本設定，語音設定之類的都會被完全刪除。

* Remove VNR Settings.reg
Reset VNR's Preferences. The following registry engtry will be deleted:

    HKEY_CURRENT_USER\Software\sakuradite.org

刪除上面註冊表中VNR的設定。VNR的使用偏好會被重置。

* ld2db.cmd (Windows), ld2db.sh (UNIX)
Convert Lingoes LD2 dictionary file to SQLite.
將Lingoes的LD2字典文件轉換為SQLite數據庫。

* sublint.cmd (Windows), sublint.sh (UNIX)
Check the integrity of VNR's offline subtitles in YAML format.
檢測VNR的YAML格式的離線字幕的語法錯誤。

* subx2y.cmd (Windows), subx2y.sh (UNIX)
Convert VNR's offline subtitles in old XML format to new YAML format.
將VNR的以前的XML格式的離線字幕轉換為新的YAML格式。

* tahcompile.cmd (Windows), tahcompile.sh (UNIX)
Generate TAH script. See examples in Libary/Examples/TAHScript.
用於生成TAH翻譯腳本。參看例子：Libary/Examples/TAHScript

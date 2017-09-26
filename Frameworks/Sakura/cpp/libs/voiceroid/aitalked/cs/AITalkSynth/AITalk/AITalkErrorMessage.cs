namespace AITalk
{
    using System;
    using System.Collections.Generic;

    public class AITalkErrorMessage
    {
        protected static Dictionary<AITalkResultCode, string> _messages = new Dictionary<AITalkResultCode, string>();

        static AITalkErrorMessage()
        {
            _messages.Add(AITalkResultCode.AITALKERR_ALREADY_INITIALIZED, "音声合成エンジンは既に初期化されています。");
            _messages.Add(AITalkResultCode.AITALKERR_ALREADY_LOADED, "既にロードされています。");
            _messages.Add(AITalkResultCode.AITALKERR_FILE_NOT_FOUND, "ファイルが見つかりません。");
            _messages.Add(AITalkResultCode.AITALKERR_INVALID_ARGUMENT, "不正なパラメータが指定されました。");
            _messages.Add(AITalkResultCode.AITALKERR_LICENSE_ABSENT, "ライセンス情報がありません。");
            _messages.Add(AITalkResultCode.AITALKERR_LICENSE_EXPIRED, "ライセンスの有効期限が切れました。");
            _messages.Add(AITalkResultCode.AITALKERR_LICENSE_REJECTED, "ライセンスの許可がありません。");
            _messages.Add(AITalkResultCode.AITALKERR_NOT_INITIALIZED, "音声合成エンジンが初期化されていません。");
            _messages.Add(AITalkResultCode.AITALKERR_NOT_LOADED, "初期化されていません。");
            _messages.Add(AITalkResultCode.AITALKERR_PATH_NOT_FOUND, "パスが見つかりません。");
            _messages.Add(AITalkResultCode.AITALKERR_READ_FAULT, "不正なファイル形式です。");
            _messages.Add(AITalkResultCode.AITALKERR_USERDIC_NOENTRY, "ユーザ辞書に有効なエントリがありません。");
        }

        public static string GetErrorMessage(AITalkResultCode key)
        {
            try
            {
                return _messages[key];
            }
            catch
            {
                return "";
            }
        }
    }
}


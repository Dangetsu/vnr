namespace AITalk
{
    using System;
    using System.Collections.Generic;

    public class AIAudioErrorMessage
    {
        protected static Dictionary<AIAudioResultCode, string> _messages = new Dictionary<AIAudioResultCode, string>();

        static AIAudioErrorMessage()
        {
            _messages.Add(AIAudioResultCode.AIAUDIOERR_ALREADY_OPENED, "音声デバイスは既に初期化されています。");
            _messages.Add(AIAudioResultCode.AIAUDIOERR_DEVICE_INVALIDATED, "音声デバイスが使用できない状態になりました。");
            _messages.Add(AIAudioResultCode.AIAUDIOERR_INTERNAL_ERROR, "内部エラーが発生しました。");
            _messages.Add(AIAudioResultCode.AIAUDIOERR_INVALID_ARGUMENT, "不正なパラメータが指定されました。");
            _messages.Add(AIAudioResultCode.AIAUDIOERR_INVALID_EVENT_ORDINAL, "渡されたイベントの順番が間違っています。");
            _messages.Add(AIAudioResultCode.AIAUDIOERR_NO_AUDIO_HARDWARE, "音声デバイスを利用できません。");
            _messages.Add(AIAudioResultCode.AIAUDIOERR_NOT_INITIALIZED, "音声デバイスが初期化されていません。");
            _messages.Add(AIAudioResultCode.AIAUDIOERR_NOT_OPENED, "音声デバイスの準備が完了していません。");
            _messages.Add(AIAudioResultCode.AIAUDIOERR_WRITE_FAULT, "指定されたパスに書き込めません。");
        }

        public static string GetErrorMessage(AIAudioResultCode key)
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


namespace AITalk
{
    using System;
    using System.Collections.Generic;
    using System.ComponentModel;
    using System.Runtime.CompilerServices;
    using System.Runtime.InteropServices;
    using System.Text;
    using System.Threading;
    using System.Windows.Forms;

    public class AITalkUtil : IDisposable
    {
        protected AIAudioProcNotify _AIAudioProcNotify;
        protected AITalkProcEventTTS _AITalkProcEventTTS;
        protected AITalkProcRawBuf _AITalkProcRawBuf;
        protected AITalkProcTextBuf _AITalkProcTextBuf;
        protected Control _associatedControl;
        protected bool _busy;
        protected bool _disposed = true;
        protected int _getStatusInterval = 100;
        protected static AITalkUtil _instance;
        protected StringBuilder _kanaBuf;
        protected bool _playing;
        protected int _voiceSamplesPerSec = 0x5622;
        protected short[] _waveBuf;

        [Description("ログを出力するときに発生します。")]
        public event LogEventHandler WriteLog;

        protected AITalkUtil()
        {
            this._AITalkProcTextBuf = new AITalkProcTextBuf(this.MyAITalkProcTextBuf);
            this._AITalkProcRawBuf = new AITalkProcRawBuf(this.MyAITalkProcRawBuf);
            this._AITalkProcEventTTS = new AITalkProcEventTTS(this.MyAITalkProcEventTTS);
            this._AIAudioProcNotify = new AIAudioProcNotify(this.MyAIAudioProcNotify);
        }

        public AITalkResultCode BLoadWordDic()
        {
            AITalkResultCode code = AITalkAPI.BLoadWordDic();
            this.OnWriteLog("[AITalkAPI_BLoadWordDic] " + code);
            return code;
        }

        public AIAudioResultCode CloseAudio()
        {
            AIAudioResultCode code = AIAudioAPI.Close();
            this.OnWriteLog("[AIAudioAPI_Close] " + code);
            this._playing = false;
            return code;
        }

        public void Dispose()
        {
            this.Dispose(true);
            GC.SuppressFinalize(this);
        }

        protected virtual void Dispose(bool disposing)
        {
            lock (this)
            {
                if (!this._disposed)
                {
                    this._disposed = true;
                    this.CloseAudio();
                    this.End();
                }
            }
        }

        public AITalkResultCode End()
        {
            AITalkResultCode code = AITalkAPI.End();
            this.OnWriteLog("[AITalkAPI_End] " + code);
            this._busy = false;
            this._playing = false;
            return code;
        }

        ~AITalkUtil()
        {
            this.Dispose(false);
            _instance = null;
        }

        public static AITalkUtil GetInstance()
        {
            if (_instance == null)
            {
                _instance = new AITalkUtil();
            }
            return _instance;
        }

        public AITalkResultCode GetParam(ref AITalk_TTtsParam param)
        {
            uint num;
            AITalkResultCode code = AITalkAPI.GetParam(IntPtr.Zero, out num);
            this.OnWriteLog("[AITalkAPI_GetParam] " + code);
            if (code == AITalkResultCode.AITALKERR_INSUFFICIENT)
            {
                IntPtr ptr = Marshal.AllocCoTaskMem((int) num);
                Marshal.WriteInt32(ptr, (int) num);
                code = AITalkAPI.GetParam(ptr, out num);
                this.OnWriteLog("[AITalkAPI_GetParam] " + code);
                if (code != AITalkResultCode.AITALKERR_SUCCESS)
                {
                    Marshal.FreeCoTaskMem(ptr);
                    return code;
                }
                param = AITalkMarshal.IntPtrToTTtsParam(ptr);
                Marshal.FreeCoTaskMem(ptr);
            }
            return code;
        }

        public AITalkResultCode GetStatus(int jobID, out AITalkStatusCode status)
        {
            return AITalkAPI.GetStatus(jobID, out status);
        }

        public AITalkResultCode Init(AITalk_TConfig config)
        {
            AITalkResultCode code = AITalkAPI.Init(ref config);
            this.OnWriteLog("[AITalkAPI_Init] " + code);
            if (code == AITalkResultCode.AITALKERR_SUCCESS)
            {
                this._disposed = false;
            }
            this._voiceSamplesPerSec = config.hzVoiceDB;
            this._kanaBuf = new StringBuilder(0x4000);
            this._waveBuf = new short[config.hzVoiceDB * 4];
            return code;
        }

        public AITalkResultCode JeitaToWave(string jeita, out short[] wave)
        {
            AITalk_TJobParam param;
            param.modeInOut = AITalkJobInOut.AITALKIOMODE_JEITA_TO_WAVE;
            param.userData = IntPtr.Zero;
            string kana = null;
            return this.SynthSync(ref param, jeita, out kana, out wave);
        }

        public AITalkResultCode KanaToJeita(string kana, string jeita)
        {
            AITalk_TJobParam param;
            param.modeInOut = AITalkJobInOut.AITALKIOMODE_AIKANA_TO_JEITA;
            param.userData = IntPtr.Zero;
            short[] wave = null;
            return this.SynthSync(ref param, kana, out jeita, out wave);
        }

        public AITalkResultCode KanaToSpeech(string kana)
        {
            AITalk_TJobParam param;
            param.modeInOut = AITalkJobInOut.AITALKIOMODE_AIKANA_TO_WAVE;
            param.userData = IntPtr.Zero;
            return this.SynthAsync(ref param, kana);
        }

        public AITalkResultCode KanaToWave(string kana, out short[] wave)
        {
            AITalk_TJobParam param;
            param.modeInOut = AITalkJobInOut.AITALKIOMODE_AIKANA_TO_WAVE;
            param.userData = IntPtr.Zero;
            string str = null;
            return this.SynthSync(ref param, kana, out str, out wave);
        }

        public AITalkResultCode LangClear()
        {
            AITalkResultCode code = AITalkAPI.LangClear();
            this.OnWriteLog("[AITalkAPI_LangClear] " + code);
            return code;
        }

        public AITalkResultCode LangLoad(string dirLang)
        {
            AITalkResultCode code = AITalkAPI.LangLoad(dirLang);
            this.OnWriteLog("[AITalkAPI_LangLoad] " + code);
            return code;
        }

        protected virtual void MyAIAudioProcNotify(ulong tick, IntPtr userData)
        {
            this.OnWriteLog(string.Concat(new object[] { "Callback [AIAudioProcNotify] ", tick, " : ", (AudioNotifyEventType) ((int) userData) }));
            if (((int) userData) == 3)
            {
                this._playing = false;
            }
        }

        protected virtual int MyAITalkProcEventTTS(AITalkEventReasonCode reasonCode, int jobID, ulong tick, string name, IntPtr userData)
        {
            this.OnWriteLog(string.Concat(new object[] { "Callback [AITalkProcEventTTS] ", jobID, " : ", reasonCode.ToString(), " : ", tick, " : ", name, " : ", (int) userData }));
            if (reasonCode == AITalkEventReasonCode.AITALKEVENT_BOOKMARK)
            {
                this.PushEvent(tick, (IntPtr) 0L);
            }
            else if (reasonCode == AITalkEventReasonCode.AITALKEVENT_PH_LABEL)
            {
                this.PushEvent(tick, (IntPtr) 1L);
            }
            return 0;
        }

        protected virtual int MyAITalkProcRawBuf(AITalkEventReasonCode reasonCode, int jobID, ulong tick, IntPtr userData)
        {
            short[] wave = null;
            uint size = 0;
            if ((reasonCode == AITalkEventReasonCode.AITALKEVENT_RAWBUF_FLUSH) || (reasonCode == AITalkEventReasonCode.AITALKEVENT_RAWBUF_FULL))
            {
                AITalkResultCode code = AITalkAPI.GetData(jobID, this._waveBuf, (uint) this._waveBuf.Length, out size);
                this.OnWriteLog(string.Concat(new object[] { "[AITalkAPI_GetData] ", code, " : ", size }));
                if ((code == AITalkResultCode.AITALKERR_SUCCESS) && (size > 0))
                {
                    wave = this._waveBuf;
                    if (reasonCode == AITalkEventReasonCode.AITALKEVENT_RAWBUF_FLUSH)
                    {
                        this.PushEvent(tick, (IntPtr) 2L);
                    }
                    this.PushData(wave, (int) size, 0);
                }
            }
            else if (reasonCode == AITalkEventReasonCode.AITALKEVENT_RAWBUF_CLOSE)
            {
                this.PushEvent(tick, (IntPtr) 3L);
                this.PushData(new short[0], 0, 1);
            }
            this.OnWriteLog(string.Concat(new object[] { "Callback [AITalkProcRawBuf] ", jobID, " : ", reasonCode.ToString(), " : ", tick, " : ", (int) userData, " : ", (wave != null) ? ((size * 2)).ToString() : "NODATA" }));
            return 0;
        }

        protected virtual int MyAITalkProcTextBuf(AITalkEventReasonCode reasonCode, int jobID, IntPtr userData)
        {
            uint size = 0;
            uint pos = 0;
            string str = "";
            if ((reasonCode == AITalkEventReasonCode.AITALKEVENT_TEXTBUF_FLUSH) || (reasonCode == AITalkEventReasonCode.AITALKEVENT_TEXTBUF_FULL))
            {
                AITalkResultCode code = AITalkAPI.GetKana(jobID, this._kanaBuf, (uint) this._kanaBuf.Capacity, out size, out pos);
                this.OnWriteLog(string.Concat(new object[] { "[AITalkAPI_GetKana] ", code, " : ", size }));
                str = this._kanaBuf.ToString();
            }
            this.OnWriteLog(string.Concat(new object[] { "Callback [AITalkProcTextBuf] ", jobID, " : ", reasonCode.ToString(), " : ", (int) userData, " : ", str }));
            return 0;
        }

        protected void OnWriteLog(object obj)
        {
            MethodInvoker method = null;
            if (this.WriteLog != null)
            {
                if ((this.AssociatedControl != null) && this.AssociatedControl.InvokeRequired)
                {
                    if (method == null)
                    {
                        method = () => this.WriteLog(this, new LogEventArgs(obj));
                    }
                    this.AssociatedControl.BeginInvoke(method);
                }
                else
                {
                    this.WriteLog(this, new LogEventArgs(obj));
                }
            }
        }

        public AIAudioResultCode OpenAudio(ref AIAudio_TConfig param)
        {
            AIAudio_TConfig config = param;
            config.procNotify = this._AIAudioProcNotify;
            AIAudioResultCode code = AIAudioAPI.Open(ref config);
            this.OnWriteLog("[AIAudioAPI_Open] " + code);
            return code;
        }

        public AIAudioResultCode PauseAudio()
        {
            AIAudioResultCode code = AIAudioAPI.Suspend();
            this.OnWriteLog("[AIAudioAPI_Suspend] " + code);
            return code;
        }

        public AIAudioResultCode PlayAudio(short[] wave)
        {
            if (this._playing)
            {
                return AIAudioResultCode.AIAUDIOERR_INVALID_CALL;
            }
            this._playing = true;
            ulong tick = (ulong) ((wave.Length * 0x3e8L) / ((long) this._voiceSamplesPerSec));
            this.PushEvent(tick, (IntPtr) 3L);
            return this.PushData(wave, wave.Length, 1);
        }

        public AIAudioResultCode PushData(short[] wave, int size, int stop)
        {
            if (!this._playing)
            {
                return AIAudioResultCode.AIAUDIOERR_NO_PLAYING;
            }
            if (wave == null)
            {
                return AIAudioResultCode.AIAUDIOERR_INVALID_ARGUMENT;
            }
            byte[] dst = new byte[size * 2];
            Buffer.BlockCopy(wave, 0, dst, 0, dst.Length);
            AIAudioResultCode code = AIAudioAPI.PushData(dst, (uint) dst.Length, stop);
            this.OnWriteLog(string.Concat(new object[] { "[AIAudioAPI_PushData] ", code, " : ", dst.Length }));
            if (code != AIAudioResultCode.AIAUDIOERR_SUCCESS)
            {
                this._playing = false;
            }
            return code;
        }

        public AIAudioResultCode PushEvent(ulong tick, IntPtr userData)
        {
            if (!this._playing)
            {
                return AIAudioResultCode.AIAUDIOERR_NO_PLAYING;
            }
            AIAudioResultCode code = AIAudioAPI.PushEvent(tick, userData);
            this.OnWriteLog(string.Concat(new object[] { "[AIAudioAPI_PushEvent] ", code, " : ", tick }));
            if (code != AIAudioResultCode.AIAUDIOERR_SUCCESS)
            {
                this._playing = false;
            }
            return code;
        }

        public AITalkResultCode ReloadPhraseDic(string pathDic)
        {
            AITalkResultCode code = AITalkAPI.ReloadPhraseDic(pathDic);
            this.OnWriteLog("[AITalkAPI_ReloadPhraseDic] " + code);
            return code;
        }

        public AITalkResultCode ReloadSymbolDic(string pathDic)
        {
            AITalkResultCode code = AITalkAPI.ReloadSymbolDic(pathDic);
            this.OnWriteLog("[AITalkAPI_ReloadSymbolDic] " + code);
            return code;
        }

        public AITalkResultCode ReloadWordDic(string pathDic)
        {
            AITalkResultCode code = AITalkAPI.ReloadWordDic(pathDic);
            this.OnWriteLog("[AITalkAPI_ReloadWordDic] " + code);
            return code;
        }

        public AIAudioResultCode ResumeAudio()
        {
            AIAudioResultCode code = AIAudioAPI.Resume();
            this.OnWriteLog("[AIAudioAPI_Resume] " + code);
            return code;
        }

        public AIAudioResultCode SaveWave(string path, ref AIAudio_TWaveFormat format, short[] wave)
        {
            byte[] dst = new byte[wave.Length * 2];
            Buffer.BlockCopy(wave, 0, dst, 0, dst.Length);
            AIAudioResultCode code = AIAudioAPI.SaveWave(path, ref format, dst, (uint) dst.Length);
            this.OnWriteLog("[AIAudioAPI_SaveWave] " + code);
            return code;
        }

        public AITalkResultCode SetParam(ref AITalk_TTtsParam param)
        {
            IntPtr pParam = AITalkMarshal.TTtsParamToIntPtr(ref param);
            AITalkResultCode code = AITalkAPI.SetParam(pParam);
            this.OnWriteLog("[AITalkAPI_SetParam] " + code);
            Marshal.FreeCoTaskMem(pParam);
            if (code == AITalkResultCode.AITALKERR_SUCCESS)
            {
                this._kanaBuf = new StringBuilder((int) param.lenTextBufBytes);
                this._waveBuf = new short[param.lenRawBufBytes / 2];
            }
            return code;
        }

        public AIAudioResultCode StopAudio()
        {
            AIAudioResultCode code = AIAudioAPI.ClearData();
            this.OnWriteLog("[AIAudioAPI_ClearData] " + code);
            this._playing = false;
            return code;
        }

        public virtual AITalkResultCode SynthAsync(ref AITalk_TJobParam jobparam, string text)
        {
            int jobID;
            if (this._busy || this._playing)
            {
                return AITalkResultCode.AITALKERR_TOO_MANY_JOBS;
            }
            this._busy = true;
            this._playing = true;
            AITalk_TTtsParam param = new AITalk_TTtsParam();
            AITalkResultCode res = this.GetParam(ref param);
            this.OnWriteLog("[AITalkAPI_GetParam] " + res);
            if (res != AITalkResultCode.AITALKERR_SUCCESS)
            {
                this._busy = false;
                this._playing = false;
                return res;
            }
            param.procTextBuf = this._AITalkProcTextBuf;
            param.procRawBuf = this._AITalkProcRawBuf;
            param.procEventTts = this._AITalkProcEventTTS;
            res = this.SetParam(ref param);
            this.OnWriteLog("[AITalkAPI_SetParam] " + res);
            if (res != AITalkResultCode.AITALKERR_SUCCESS)
            {
                this._busy = false;
                this._playing = false;
                return res;
            }
            this.OnWriteLog("[AIAuidoAPI_ClearData] " + AIAudioAPI.ClearData());
            res = AITalkAPI.TextToSpeech(out jobID, ref jobparam, text);
            this.OnWriteLog("[AITalkAPI_TextToSpeech] " + res);
            if (res != AITalkResultCode.AITALKERR_SUCCESS)
            {
                this._busy = false;
                this._playing = false;
                return res;
            }
            new Thread(delegate {
                AITalkStatusCode code;
                do
                {
                    Thread.Sleep(this.GetStatusInterval);
                    res = this.GetStatus(jobID, out code);
                }
                while ((this._playing && (res == AITalkResultCode.AITALKERR_SUCCESS)) && (code != AITalkStatusCode.AITALKSTAT_DONE));
                AITalkAPI.CloseSpeech(jobID, 0);
                this.OnWriteLog("[AITalkAPI_CloseSpeech] " + res);
                this._busy = false;
            }) { IsBackground = true }.Start();
            return res;
        }

        public AITalkResultCode SynthSync(ref AITalk_TJobParam jobparam, string text, out string kana, out short[] wave)
        {
            int num;
            AITalkStatusCode code3;
            kana = null;
            wave = null;
            if (this._busy)
            {
                return AITalkResultCode.AITALKERR_TOO_MANY_JOBS;
            }
            this._busy = true;
            AITalk_TTtsParam param = new AITalk_TTtsParam();
            AITalkResultCode status = this.GetParam(ref param);
            this.OnWriteLog("[AITalkAPI_GetParam] " + status);
            if (status != AITalkResultCode.AITALKERR_SUCCESS)
            {
                this._busy = false;
                return status;
            }
            param.procTextBuf = null;
            param.procRawBuf = null;
            param.procEventTts = null;
            status = this.SetParam(ref param);
            this.OnWriteLog("[AITalkAPI_SetParam] " + status);
            if (status != AITalkResultCode.AITALKERR_SUCCESS)
            {
                this._busy = false;
                return status;
            }
            if ((jobparam.modeInOut == AITalkJobInOut.AITALKIOMODE_PLAIN_TO_AIKANA) || (jobparam.modeInOut == AITalkJobInOut.AITALKIOMODE_AIKANA_TO_JEITA))
            {
                status = AITalkAPI.TextToKana(out num, ref jobparam, text);
                this.OnWriteLog(string.Concat(new object[] { "[AITalkAPI_TextToKana] ", status, " : ", num }));
            }
            else
            {
                status = AITalkAPI.TextToSpeech(out num, ref jobparam, text);
                this.OnWriteLog(string.Concat(new object[] { "[AITalkAPI_TextToSpeech] ", status, " : ", num }));
            }
            if (status != AITalkResultCode.AITALKERR_SUCCESS)
            {
                this._busy = false;
                return status;
            }
            StringBuilder textBuf = new StringBuilder((int) param.lenTextBufBytes);
            short[] rawBuf = new short[param.lenRawBufBytes / 2];
            List<short[]> list = new List<short[]>();
            AITalkResultCode code2 = AITalkResultCode.AITALKERR_SUCCESS;
        Label_0166:
            Thread.Sleep(this.GetStatusInterval);
            status = AITalkAPI.GetStatus(num, out code3);
            if (status != AITalkResultCode.AITALKERR_SUCCESS)
            {
                code2 = status;
            }
            else
            {
                switch (code3)
                {
                    case AITalkStatusCode.AITALKSTAT_WRONG_STATE:
                        code2 = status;
                        goto Label_02F4;

                    case AITalkStatusCode.AITALKSTAT_INPROGRESS:
                        goto Label_0166;
                }
                uint size = 0;
                uint num3 = 0;
                if (((jobparam.modeInOut == AITalkJobInOut.AITALKIOMODE_PLAIN_TO_WAVE) || (jobparam.modeInOut == AITalkJobInOut.AITALKIOMODE_PLAIN_TO_AIKANA)) || (jobparam.modeInOut == AITalkJobInOut.AITALKIOMODE_AIKANA_TO_JEITA))
                {
                    uint num4;
                    status = AITalkAPI.GetKana(num, textBuf, (uint) textBuf.Capacity, out size, out num4);
                    this.OnWriteLog(string.Concat(new object[] { "[AITalkAPI_GetKana] ", status, " : ", size }));
                    if ((status != AITalkResultCode.AITALKERR_NOMORE_DATA) && (status != AITalkResultCode.AITALKERR_SUCCESS))
                    {
                        code2 = status;
                        goto Label_02F4;
                    }
                    if (size > 0)
                    {
                        if (kana == null)
                        {
                            kana = textBuf.ToString();
                        }
                        else
                        {
                            kana = kana + textBuf.ToString();
                        }
                    }
                }
                if (((jobparam.modeInOut == AITalkJobInOut.AITALKIOMODE_PLAIN_TO_WAVE) || (jobparam.modeInOut == AITalkJobInOut.AITALKIOMODE_AIKANA_TO_WAVE)) || (jobparam.modeInOut == AITalkJobInOut.AITALKIOMODE_JEITA_TO_WAVE))
                {
                    status = AITalkAPI.GetData(num, rawBuf, (uint) rawBuf.Length, out num3);
                    this.OnWriteLog(string.Concat(new object[] { "[AITalkAPI_GetData] ", status, " : ", num3 }));
                    if (status == AITalkResultCode.AITALKERR_NOMORE_DATA)
                    {
                        goto Label_02F4;
                    }
                    if (status != AITalkResultCode.AITALKERR_SUCCESS)
                    {
                        code2 = status;
                        goto Label_02F4;
                    }
                    short[] dst = new short[num3];
                    Buffer.BlockCopy(rawBuf, 0, dst, 0, (int) (num3 * 2));
                    list.Add(dst);
                }
                if (((code3 != AITalkStatusCode.AITALKSTAT_DONE) || (size != 0)) || (num3 != 0))
                {
                    goto Label_0166;
                }
            }
        Label_02F4:
            if ((jobparam.modeInOut == AITalkJobInOut.AITALKIOMODE_PLAIN_TO_AIKANA) || (jobparam.modeInOut == AITalkJobInOut.AITALKIOMODE_AIKANA_TO_JEITA))
            {
                status = AITalkAPI.CloseKana(num, 0);
                this.OnWriteLog("[AITalkAPI_CloseKana] " + status);
            }
            else
            {
                status = AITalkAPI.CloseSpeech(num, 0);
                this.OnWriteLog("[AITalkAPI_CloseSpeech] " + status);
            }
            if (list.Count > 0)
            {
                int num5 = 0;
                foreach (short[] numArray3 in list)
                {
                    num5 += numArray3.Length;
                }
                wave = new short[num5];
                int dstOffset = 0;
                foreach (short[] numArray4 in list)
                {
                    Buffer.BlockCopy(numArray4, 0, wave, dstOffset, numArray4.Length * 2);
                    dstOffset += numArray4.Length * 2;
                }
            }
            this._busy = false;
            if (code2 == AITalkResultCode.AITALKERR_SUCCESS)
            {
                return status;
            }
            return code2;
        }

        public AITalkResultCode TextToKana(string text, out string kana)
        {
            AITalk_TJobParam param;
            param.modeInOut = AITalkJobInOut.AITALKIOMODE_PLAIN_TO_AIKANA;
            param.userData = IntPtr.Zero;
            short[] wave = null;
            return this.SynthSync(ref param, text, out kana, out wave);
        }

        public AITalkResultCode TextToSpeech(string text)
        {
            AITalk_TJobParam param;
            param.modeInOut = AITalkJobInOut.AITALKIOMODE_PLAIN_TO_WAVE;
            param.userData = IntPtr.Zero;
            return this.SynthAsync(ref param, text);
        }

        public AITalkResultCode TextToWave(string text, out short[] wave)
        {
            AITalk_TJobParam param;
            param.modeInOut = AITalkJobInOut.AITALKIOMODE_PLAIN_TO_WAVE;
            param.userData = IntPtr.Zero;
            string kana = null;
            return this.SynthSync(ref param, text, out kana, out wave);
        }

        public AITalkResultCode TextToWave(string text, out string kana, out short[] wave)
        {
            AITalk_TJobParam param;
            param.modeInOut = AITalkJobInOut.AITALKIOMODE_PLAIN_TO_WAVE;
            param.userData = IntPtr.Zero;
            return this.SynthSync(ref param, text, out kana, out wave);
        }

        protected void ThrowExceptionIfDisposed()
        {
            if (this._disposed)
            {
                throw new ObjectDisposedException(base.GetType().ToString());
            }
        }

        public AITalkResultCode VersionInfo(int verbose, out string str)
        {
            uint num2;
            int capacity = 0x400;
            StringBuilder sjis = new StringBuilder(capacity);
            AITalkResultCode code = AITalkAPI.VersionInfo(verbose, sjis, (uint) capacity, out num2);
            this.OnWriteLog("[AITalkAPI_VersionInfo] " + code);
            str = sjis.ToString();
            return code;
        }

        public AITalkResultCode VoiceClear()
        {
            AITalkResultCode code = AITalkAPI.VoiceClear();
            this.OnWriteLog("[AITalkAPI_VoiceClear] " + code);
            return code;
        }

        public AITalkResultCode VoiceLoad(string voiceName)
        {
            AITalkResultCode code = AITalkAPI.VoiceLoad(voiceName);
            this.OnWriteLog("[AITalkAPI_VoiceLoad] " + code);
            return code;
        }

        [Description("ログ出力イベントの送り先となるコントロールを取得または設定します。")]
        public Control AssociatedControl
        {
            get
            {
                return this._associatedControl;
            }
            set
            {
                this._associatedControl = value;
            }
        }

        [Description("合成時にAITalk SDK ライブラリの状態をチェックする間隔を取得または設定します。")]
        public int GetStatusInterval
        {
            get
            {
                return this._getStatusInterval;
            }
            set
            {
                this._getStatusInterval = value;
            }
        }

        public enum AudioNotifyEventType
        {
            Bookmark,
            Phoneme,
            Sentence,
            Complete
        }

        public class LogEventArgs : EventArgs
        {
            private string _text = "";

            public LogEventArgs(object obj)
            {
                this._text = obj.ToString();
            }

            [Description("ログを取得します。")]
            public string Text
            {
                get
                {
                    return this._text;
                }
            }
        }

        public delegate void LogEventHandler(object sender, AITalkUtil.LogEventArgs e);
    }
}


namespace AITalk
{
    using System;
    using System.Runtime.CompilerServices;
    using System.Runtime.InteropServices;
    using System.Threading;
    using System.Windows.Forms;

    public class AITalkUtilEx : AITalkUtil
    {
        private int _beginPause;
        private JobInfo _jobInfo;
        private int _termPause;
        public static readonly char[] TerminalSymbolList = new char[] { '\n', '。', '？', '！', '｡', '!', '?' };

        public event ErrorEventHandler ErrorOccured;

        public event JobCompleteEventHandler JobComplete;

        public event AudioEventHandler PlayBookmark;

        public event AudioEventHandler PlayComplete;

        public event PhonemeLabelEventHandler PlayPhonemeLabel;

        public event AudioEventHandler PlaySentence;

        public event SynthesizingEventHandler SynthesizingProgress;

        public event TextProcessingEventHandler TextProcessingComplete;

        public event TextProcessingEventHandler TextProcessingProgress;

        public event TTSEventHandler TTSBookmark;

        public event TTSEventHandler TTSPhonemeLabel;

        private AITalkUtilEx()
        {
        }

        public void Abort()
        {
            if (base._busy)
            {
                this._jobInfo.Aborted = true;
            }
        }

        public AITalkResultCode Do(AITalk.SynthMode synthMode, string text, AITalk.SynthOption synthOption)
        {
            AITalk_TJobParam param2;
            if (base._busy || base._playing)
            {
                return AITalkResultCode.AITALKERR_TOO_MANY_JOBS;
            }
            this.SynthMode = synthMode;
            this.SynthOption = synthOption;
            base._busy = true;
            int jobID = -1;
            AITalkResultCode code = AITalkResultCode.AITALKERR_SUCCESS;
            AITalk_TTtsParam param = new AITalk_TTtsParam();
            code = base.GetParam(ref param);
            base.OnWriteLog("[AITalkAPI_GetParam] " + code);
            if (code != AITalkResultCode.AITALKERR_SUCCESS)
            {
                base._busy = false;
                return code;
            }
            param.pauseBegin = ((synthOption & AITalk.SynthOption.UseBeginPause) == AITalk.SynthOption.UseBeginPause) ? this._beginPause : 0;
            param.pauseTerm = ((synthOption & AITalk.SynthOption.UseTermPause) == AITalk.SynthOption.UseTermPause) ? this._termPause : 0;
            param.procTextBuf = base._AITalkProcTextBuf;
            param.procRawBuf = base._AITalkProcRawBuf;
            param.procEventTts = base._AITalkProcEventTTS;
            code = base.SetParam(ref param);
            base.OnWriteLog("[AITalkAPI_SetParam] " + code);
            if (code != AITalkResultCode.AITALKERR_SUCCESS)
            {
                base._busy = false;
                return code;
            }
            if ((this.SynthMode & AITalk.SynthMode.TextProcess) == AITalk.SynthMode.TextProcess)
            {
                this._jobInfo = new JobInfo(this.SynthMode, text, this.SynthOption, param.lenTextBufBytes, param.lenRawBufBytes);
            }
            else
            {
                this._jobInfo = new JobInfo(this.SynthMode, text, this.SynthOption, param.lenTextBufBytes, param.lenRawBufBytes);
                this._jobInfo.TextBlockList.Add(new JobInfo.TextBlock(0, text, text, "", 1f, 1f, 1f, 1f));
            }
            param2.userData = IntPtr.Zero;
            if (this.SynthMode == AITalk.SynthMode.TextProcess)
            {
                param2.modeInOut = AITalkJobInOut.AITALKIOMODE_PLAIN_TO_AIKANA;
            }
            else if ((this.SynthMode == AITalk.SynthMode.Synthesize) || (this.SynthMode == AITalk.SynthMode.KanaToSpeech))
            {
                param2.modeInOut = AITalkJobInOut.AITALKIOMODE_AIKANA_TO_WAVE;
            }
            else if ((this.SynthMode == AITalk.SynthMode.TextToWave) || (this.SynthMode == AITalk.SynthMode.TextToSpeech))
            {
                param2.modeInOut = AITalkJobInOut.AITALKIOMODE_PLAIN_TO_WAVE;
            }
            else
            {
                base._busy = false;
                return code;
            }
            if ((this.SynthMode & AITalk.SynthMode.Play) == AITalk.SynthMode.Play)
            {
                AIAudioResultCode errorCode = AIAudioAPI.ClearData();
                base.OnWriteLog("[AIAuidoAPI_ClearData] " + errorCode);
                if ((errorCode != AIAudioResultCode.AIAUDIOERR_SUCCESS) && (errorCode != AIAudioResultCode.AIAUDIOERR_NO_PLAYING))
                {
                    this.InvokeUserEventHandler<ErrorEventArgs>(new EventInVoker<ErrorEventArgs>(this.OnErrorOccured), new ErrorEventArgs("ClearData", errorCode, ""));
                    base._busy = false;
                    return code;
                }
                base._playing = true;
            }
            if ((this.SynthMode & AITalk.SynthMode.Synthesize) != AITalk.SynthMode.Synthesize)
            {
                code = AITalkAPI.TextToKana(out jobID, ref param2, this._jobInfo.SynthText);
                base.OnWriteLog(string.Concat(new object[] { "[AITalkAPI_TextToKana] ", code, " : ", jobID }));
            }
            else
            {
                code = AITalkAPI.TextToSpeech(out jobID, ref param2, this._jobInfo.SynthText);
                base.OnWriteLog(string.Concat(new object[] { "[AITalkAPI_TextToSpeech] ", code, " : ", jobID }));
            }
            if (code != AITalkResultCode.AITALKERR_SUCCESS)
            {
                base._playing = false;
                base._busy = false;
                return code;
            }
            this._jobInfo.JobID = jobID;
            new Thread(new ThreadStart(this.DoJob)) { IsBackground = true }.Start();
            return code;
        }

        protected void DoJob()
        {
            AITalkResultCode errorCode = AITalkResultCode.AITALKERR_SUCCESS;
            AITalkStatusCode status = AITalkStatusCode.AITALKSTAT_DONE;
        Label_0005:
            Thread.Sleep(base.GetStatusInterval);
            errorCode = base.GetStatus(this._jobInfo.JobID, out status);
            if ((errorCode != AITalkResultCode.AITALKERR_SUCCESS) || (status == AITalkStatusCode.AITALKSTAT_WRONG_STATE))
            {
                this.InvokeUserEventHandler<ErrorEventArgs>(new EventInVoker<ErrorEventArgs>(this.OnErrorOccured), new ErrorEventArgs("GetStatus", errorCode, ""));
            }
            else if (!this._jobInfo.Aborted)
            {
                if (this._jobInfo.TextProcessingDone && (this._jobInfo.TextBlockList.Count == 0))
                {
                    if (base._playing)
                    {
                        AudioEventArgs e = new AudioEventArgs(0, "", "", 0L);
                        this.InvokeUserEventHandler<AudioEventArgs>(new EventInVoker<AudioEventArgs>(this.OnPlayComplete), e);
                        base._playing = false;
                    }
                }
                else if ((((this.SynthMode & AITalk.SynthMode.Play) != AITalk.SynthMode.Play) || base._playing) && (((this.SynthMode & AITalk.SynthMode.Play) == AITalk.SynthMode.Play) || (status != AITalkStatusCode.AITALKSTAT_DONE)))
                {
                    goto Label_0005;
                }
            }
            if ((this.SynthMode & AITalk.SynthMode.Synthesize) != AITalk.SynthMode.Synthesize)
            {
                AITalkResultCode code3 = AITalkAPI.CloseKana(this._jobInfo.JobID, 0);
                base.OnWriteLog("[AITalkAPI_CloseKana] " + code3);
                if (code3 != AITalkResultCode.AITALKERR_SUCCESS)
                {
                    this.InvokeUserEventHandler<ErrorEventArgs>(new EventInVoker<ErrorEventArgs>(this.OnErrorOccured), new ErrorEventArgs("CloseKana", code3, ""));
                }
            }
            else
            {
                AITalkResultCode code4 = AITalkAPI.CloseSpeech(this._jobInfo.JobID, 0);
                base.OnWriteLog("[AITalkAPI_CloseSpeech] " + code4);
                if (code4 != AITalkResultCode.AITALKERR_SUCCESS)
                {
                    this.InvokeUserEventHandler<ErrorEventArgs>(new EventInVoker<ErrorEventArgs>(this.OnErrorOccured), new ErrorEventArgs("CloseSpeech", code4, ""));
                }
            }
            if (base._playing)
            {
                base.StopAudio();
                base._playing = false;
            }
            this._jobInfo = null;
            base._busy = false;
            this.InvokeUserEventHandler<EventArgs>(new EventInVoker<EventArgs>(this.OnJobComplete), new EventArgs());
        }

        ~AITalkUtilEx()
        {
        }

        public static AITalkUtilEx GetInstance()
        {
            if (AITalkUtil._instance == null)
            {
                AITalkUtil._instance = new AITalkUtilEx();
            }
            return (AITalkUtilEx) AITalkUtil._instance;
        }

        private void InvokeUserEventHandler<EventArgsType>(EventInVoker<EventArgsType> invoker, EventArgsType e) where EventArgsType: EventArgs
        {
            MethodInvoker method = null;
            if ((base.AssociatedControl != null) && base.AssociatedControl.InvokeRequired)
            {
                if (method == null)
                {
                    method = () => invoker(e);
                }
                base.AssociatedControl.BeginInvoke(method);
            }
            else
            {
                invoker(e);
            }
        }

        protected override void MyAIAudioProcNotify(ulong tick, IntPtr userData)
        {
            AudioEventParam param = AudioEventParam.ToStruct(userData);
            AudioEventParam.Free(userData);
            base.OnWriteLog(string.Concat(new object[] { "Callback [AIAudioProcNotify] ", param.EventCode, " : ", tick, " : ", param.Pos, " : ", param.Text, " : ", param.Kana }));
            if (param.EventCode == AudioEventCode.Bookmark)
            {
                AudioEventArgs e = new AudioEventArgs(param.Pos, param.Text, param.Kana, tick);
                this.InvokeUserEventHandler<AudioEventArgs>(new EventInVoker<AudioEventArgs>(this.OnPlayBookmark), e);
            }
            else if (param.EventCode == AudioEventCode.PhonemeLabel)
            {
                PhonemeLabelEventArgs args2 = new PhonemeLabelEventArgs(param.Text, param.Tick);
                this.InvokeUserEventHandler<PhonemeLabelEventArgs>(new EventInVoker<PhonemeLabelEventArgs>(this.OnPlayPhonemeLabel), args2);
            }
            else if (param.EventCode == AudioEventCode.Sentence)
            {
                AudioEventArgs args3 = new AudioEventArgs(param.Pos, param.Text, param.Kana, tick);
                this.InvokeUserEventHandler<AudioEventArgs>(new EventInVoker<AudioEventArgs>(this.OnPlaySentence), args3);
            }
            else if (param.EventCode == AudioEventCode.Complete)
            {
                AudioEventArgs args4 = new AudioEventArgs(param.Pos, param.Text, param.Kana, tick);
                this.InvokeUserEventHandler<AudioEventArgs>(new EventInVoker<AudioEventArgs>(this.OnPlayComplete), args4);
                base._playing = false;
            }
        }

        protected override int MyAITalkProcEventTTS(AITalkEventReasonCode reasonCode, int jobID, ulong tick, string name, IntPtr userData)
        {
            base.OnWriteLog(string.Concat(new object[] { "Callback [AITalkProcEventTTS] ", jobID, " : ", reasonCode.ToString(), " : ", tick, " : ", name, " : ", (int) userData }));
            TTSEventArgs e = new TTSEventArgs(tick, name);
            if (reasonCode == AITalkEventReasonCode.AITALKEVENT_BOOKMARK)
            {
                int num;
                string text = this._jobInfo.ProgressBookMark(name, out num);
                if (text == null)
                {
                    return 0;
                }
                if ((this.SynthMode & AITalk.SynthMode.Play) == AITalk.SynthMode.Play)
                {
                    AudioEventParam item = new AudioEventParam(AudioEventCode.Bookmark, num, text, "", tick);
                    this._jobInfo.AudioEventQueue.Enqueue(item);
                }
                this.InvokeUserEventHandler<TTSEventArgs>(new EventInVoker<TTSEventArgs>(this.OnTTSBookmark), e);
            }
            else if (reasonCode == AITalkEventReasonCode.AITALKEVENT_PH_LABEL)
            {
                if ((this.SynthMode & AITalk.SynthMode.Play) == AITalk.SynthMode.Play)
                {
                    AudioEventParam param2 = new AudioEventParam(AudioEventCode.PhonemeLabel, 0, name, "", tick);
                    this._jobInfo.AudioEventQueue.Enqueue(param2);
                }
                this.InvokeUserEventHandler<TTSEventArgs>(new EventInVoker<TTSEventArgs>(this.OnTTSPhonemeLabel), e);
            }
            return 0;
        }

        protected override int MyAITalkProcRawBuf(AITalkEventReasonCode reasonCode, int jobID, ulong tick, IntPtr userData)
        {
            uint size = 0;
            short[] wave = null;
            if ((reasonCode == AITalkEventReasonCode.AITALKEVENT_RAWBUF_FLUSH) || (reasonCode == AITalkEventReasonCode.AITALKEVENT_RAWBUF_FULL))
            {
                AITalkResultCode errorCode = AITalkAPI.GetData(jobID, this._jobInfo.WaveBuffer, (uint) this._jobInfo.WaveBuffer.Length, out size);
                base.OnWriteLog(string.Concat(new object[] { "[AITalkAPI_GetData] ", errorCode, " : ", size }));
                if (errorCode != AITalkResultCode.AITALKERR_SUCCESS)
                {
                    this.InvokeUserEventHandler<ErrorEventArgs>(new EventInVoker<ErrorEventArgs>(this.OnErrorOccured), new ErrorEventArgs("GetData", errorCode, ""));
                }
                if ((errorCode == AITalkResultCode.AITALKERR_SUCCESS) && (size > 0))
                {
                    wave = this._jobInfo.WaveBuffer;
                    if (this._jobInfo.NextSentenceStartTick >= 0L)
                    {
                        JobInfo.TextBlock block = this._jobInfo.TextBlockList[this._jobInfo.CurrentIndex];
                        block.Tick = this._jobInfo.NextSentenceStartTick;
                        if ((this.SynthMode & AITalk.SynthMode.Play) == AITalk.SynthMode.Play)
                        {
                            AIAudioResultCode code2 = base.PushEvent((ulong) block.Tick, new AudioEventParam(AudioEventCode.Sentence, block.Pos, block.Text, block.Kana, (ulong) block.Tick).ToIntPtr());
                            if ((code2 != AIAudioResultCode.AIAUDIOERR_SUCCESS) && (code2 != AIAudioResultCode.AIAUDIOERR_NO_PLAYING))
                            {
                                this.InvokeUserEventHandler<ErrorEventArgs>(new EventInVoker<ErrorEventArgs>(this.OnErrorOccured), new ErrorEventArgs("PushEvent_Progress", code2, ""));
                            }
                        }
                        this._jobInfo.NextSentenceStartTick = -1L;
                    }
                    this.PushQueuedEvents();
                    if ((this.SynthMode & AITalk.SynthMode.Play) == AITalk.SynthMode.Play)
                    {
                        AIAudioResultCode code3 = base.PushData(wave, (int) size, 0);
                        if ((code3 != AIAudioResultCode.AIAUDIOERR_SUCCESS) && (code3 != AIAudioResultCode.AIAUDIOERR_NO_PLAYING))
                        {
                            this.InvokeUserEventHandler<ErrorEventArgs>(new EventInVoker<ErrorEventArgs>(this.OnErrorOccured), new ErrorEventArgs("PushData_Progress", code3, ""));
                        }
                    }
                }
                if ((reasonCode == AITalkEventReasonCode.AITALKEVENT_RAWBUF_FLUSH) && ((this.SynthMode & AITalk.SynthMode.TextProcess) == AITalk.SynthMode.TextProcess))
                {
                    this._jobInfo.GrowSynthesizingProgress(this._jobInfo.TextBlockList[this._jobInfo.CurrentIndex]);
                    this._jobInfo.NextSentenceStartTick = (long) tick;
                    this._jobInfo.CurrentIndex++;
                }
                int progress = ((this.SynthMode & AITalk.SynthMode.TextProcess) == AITalk.SynthMode.TextProcess) ? this._jobInfo.GetSynthesizeingProgressPercentage() : 0;
                SynthesizingEventArgs e = new SynthesizingEventArgs(tick, wave, (int) size, reasonCode == AITalkEventReasonCode.AITALKEVENT_RAWBUF_FLUSH, progress);
                this.InvokeUserEventHandler<SynthesizingEventArgs>(new EventInVoker<SynthesizingEventArgs>(this.OnSynthesizingProgress), e);
            }
            else
            {
                if ((this.SynthMode & AITalk.SynthMode.Play) == AITalk.SynthMode.Play)
                {
                    AIAudioResultCode code4 = base.PushEvent(tick, new AudioEventParam(AudioEventCode.Complete, 0, "", "", tick).ToIntPtr());
                    if (code4 == AIAudioResultCode.AIAUDIOERR_SUCCESS)
                    {
                        code4 = base.PushData(new short[1], 1, 1);
                        if ((code4 != AIAudioResultCode.AIAUDIOERR_SUCCESS) && (code4 != AIAudioResultCode.AIAUDIOERR_NO_PLAYING))
                        {
                            this.InvokeUserEventHandler<ErrorEventArgs>(new EventInVoker<ErrorEventArgs>(this.OnErrorOccured), new ErrorEventArgs("PushData_Complete", code4, ""));
                        }
                    }
                    else if (code4 != AIAudioResultCode.AIAUDIOERR_NO_PLAYING)
                    {
                        this.InvokeUserEventHandler<ErrorEventArgs>(new EventInVoker<ErrorEventArgs>(this.OnErrorOccured), new ErrorEventArgs("PushEvent_Complete", code4, ""));
                    }
                }
                SynthesizingEventArgs args2 = new SynthesizingEventArgs(tick, null, 0, false, 100);
                this.InvokeUserEventHandler<SynthesizingEventArgs>(new EventInVoker<SynthesizingEventArgs>(this.OnSynthesizingComplete), args2);
                this._jobInfo.SynthesizingDone = true;
            }
            base.OnWriteLog(string.Concat(new object[] { "Callback [AITalkProcRawBuf] ", jobID, " : ", reasonCode.ToString(), " : ", tick, " : ", (int) userData, " : ", (wave != null) ? ((size * 2)).ToString() : "NODATA" }));
            return 0;
        }

        protected override int MyAITalkProcTextBuf(AITalkEventReasonCode reasonCode, int jobID, IntPtr userData)
        {
            uint size = 0;
            uint pos = 0;
            string kana = "";
            if ((reasonCode == AITalkEventReasonCode.AITALKEVENT_TEXTBUF_FLUSH) || (reasonCode == AITalkEventReasonCode.AITALKEVENT_TEXTBUF_FULL))
            {
                AITalkResultCode errorCode = AITalkAPI.GetKana(jobID, this._jobInfo.KanaBuffer, (uint) this._jobInfo.KanaBuffer.Capacity, out size, out pos);
                base.OnWriteLog(string.Concat(new object[] { "[AITalkAPI_GetKana] ", errorCode, " : ", size }));
                if (errorCode != AITalkResultCode.AITALKERR_SUCCESS)
                {
                    this.InvokeUserEventHandler<ErrorEventArgs>(new EventInVoker<ErrorEventArgs>(this.OnErrorOccured), new ErrorEventArgs("GetKana", errorCode, ""));
                }
                kana = this._jobInfo.KanaBuffer.ToString();
                JobInfo.TextBlock textBlock = this._jobInfo.AddTextBlock((int) pos, kana);
                this._jobInfo.GrowTextProcessingProgress(textBlock);
                int textProcessingProgressPercentage = this._jobInfo.GetTextProcessingProgressPercentage();
                TextProcessingEventArgs e = new TextProcessingEventArgs(textBlock.Pos, textBlock.Text, kana, textProcessingProgressPercentage);
                this.InvokeUserEventHandler<TextProcessingEventArgs>(new EventInVoker<TextProcessingEventArgs>(this.OnTextProcessingProgress), e);
            }
            else if (reasonCode == AITalkEventReasonCode.AITALKEVENT_TEXTBUF_CLOSE)
            {
                TextProcessingEventArgs args2 = new TextProcessingEventArgs(0, "", "", 100);
                this.InvokeUserEventHandler<TextProcessingEventArgs>(new EventInVoker<TextProcessingEventArgs>(this.OnTextProcessingComplete), args2);
                this._jobInfo.TextProcessingDone = true;
                base.OnWriteLog("[JobInfo] " + this._jobInfo.ToString());
            }
            base.OnWriteLog(string.Concat(new object[] { "Callback [AITalkProcTextBuf] ", jobID, " : ", reasonCode.ToString(), " : ", (int) userData, " : ", kana }));
            return 0;
        }

        protected virtual void OnErrorOccured(ErrorEventArgs e)
        {
            if (this.ErrorOccured != null)
            {
                this.ErrorOccured(this, e);
            }
        }

        protected virtual void OnJobComplete(EventArgs e)
        {
            if (this.JobComplete != null)
            {
                this.JobComplete(this, e);
            }
        }

        protected virtual void OnPlayBookmark(AudioEventArgs e)
        {
            if (this.PlayBookmark != null)
            {
                this.PlayBookmark(this, e);
            }
        }

        protected virtual void OnPlayComplete(AudioEventArgs e)
        {
            if (this.PlayComplete != null)
            {
                this.PlayComplete(this, e);
            }
        }

        protected virtual void OnPlayPhonemeLabel(PhonemeLabelEventArgs e)
        {
            if (this.PlayPhonemeLabel != null)
            {
                this.PlayPhonemeLabel(this, e);
            }
        }

        protected virtual void OnPlaySentence(AudioEventArgs e)
        {
            if (this.PlaySentence != null)
            {
                this.PlaySentence(this, e);
            }
        }

        protected virtual void OnSynthesizingComplete(SynthesizingEventArgs e)
        {
            if (this.SynthesizingComplete != null)
            {
                this.SynthesizingComplete(this, e);
            }
        }

        protected virtual void OnSynthesizingProgress(SynthesizingEventArgs e)
        {
            if (this.SynthesizingProgress != null)
            {
                this.SynthesizingProgress(this, e);
            }
        }

        protected virtual void OnTextProcessingComplete(TextProcessingEventArgs e)
        {
            if (this.TextProcessingComplete != null)
            {
                this.TextProcessingComplete(this, e);
            }
        }

        protected virtual void OnTextProcessingProgress(TextProcessingEventArgs e)
        {
            if (this.TextProcessingProgress != null)
            {
                this.TextProcessingProgress(this, e);
            }
        }

        protected virtual void OnTTSBookmark(TTSEventArgs e)
        {
            if (this.TTSBookmark != null)
            {
                this.TTSBookmark(this, e);
            }
        }

        protected virtual void OnTTSPhonemeLabel(TTSEventArgs e)
        {
            if (this.TTSPhonemeLabel != null)
            {
                this.TTSPhonemeLabel(this, e);
            }
        }

        private void PushQueuedEvents()
        {
            while (this._jobInfo.AudioEventQueue.Count > 0)
            {
                AudioEventParam param = this._jobInfo.AudioEventQueue.Dequeue();
                AIAudioResultCode errorCode = base.PushEvent(param.Tick, param.ToIntPtr());
                if ((errorCode != AIAudioResultCode.AIAUDIOERR_SUCCESS) && (errorCode != AIAudioResultCode.AIAUDIOERR_NO_PLAYING))
                {
                    this.InvokeUserEventHandler<ErrorEventArgs>(new EventInVoker<ErrorEventArgs>(this.OnErrorOccured), new ErrorEventArgs("PushEvent_PushQueuedEvents", errorCode, ""));
                }
            }
        }

        public int BeginPause
        {
            get
            {
                return this._beginPause;
            }
            set
            {
                if (value != this._beginPause)
                {
                    if (value > 0x2710)
                    {
                        this._beginPause = 0x2710;
                    }
                    else if (value < -1)
                    {
                        this._beginPause = -1;
                    }
                    else
                    {
                        this._beginPause = value;
                    }
                }
            }
        }

        public SynthesizingEventHandler SynthesizingComplete { get; set; }

        public AITalk.SynthMode SynthMode { get; private set; }

        public AITalk.SynthOption SynthOption { get; private set; }

        public int TermPause
        {
            get
            {
                return this._termPause;
            }
            set
            {
                if (value != this._termPause)
                {
                    if (value > 0x2710)
                    {
                        this._termPause = 0x2710;
                    }
                    else if (value < -1)
                    {
                        this._termPause = -1;
                    }
                    else
                    {
                        this._termPause = value;
                    }
                }
            }
        }

        public class AudioEventArgs : EventArgs
        {
            public AudioEventArgs(int pos, string text, string kana, ulong tick)
            {
                this.Pos = pos;
                this.Text = text;
                this.Kana = kana;
                this.Tick = tick;
            }

            public string Kana { get; private set; }

            public int Pos { get; private set; }

            public string Text { get; private set; }

            public ulong Tick { get; private set; }
        }

        internal enum AudioEventCode
        {
            Bookmark,
            PhonemeLabel,
            Sentence,
            Complete
        }

        public delegate void AudioEventHandler(object sender, AITalkUtilEx.AudioEventArgs e);

        [StructLayout(LayoutKind.Sequential)]
        internal struct AudioEventParam
        {
            public AITalkUtilEx.AudioEventCode EventCode;
            public int Pos;
            public string Text;
            public string Kana;
            public ulong Tick;
            public AudioEventParam(AITalkUtilEx.AudioEventCode eventCode, int pos, string text, string kana, ulong tick)
            {
                this.EventCode = eventCode;
                this.Pos = pos;
                this.Text = text;
                this.Kana = kana;
                this.Tick = tick;
            }

            public IntPtr ToIntPtr()
            {
                IntPtr ptr = Marshal.AllocHGlobal(Marshal.SizeOf(typeof(AITalkUtilEx.AudioEventParam)));
                Marshal.StructureToPtr(this, ptr, false);
                return ptr;
            }

            public static void Free(IntPtr ptr)
            {
                Marshal.FreeHGlobal(ptr);
            }

            public static AITalkUtilEx.AudioEventParam ToStruct(IntPtr ptr)
            {
                return (AITalkUtilEx.AudioEventParam) Marshal.PtrToStructure(ptr, typeof(AITalkUtilEx.AudioEventParam));
            }
        }

        public class ErrorEventArgs : EventArgs
        {
            public ErrorEventArgs(string name, AIAudioResultCode errorCode, string message = "")
            {
                this.Name = name;
                this.Type = AITalkUtilEx.ErrorType.AIAudio;
                this.ErrorCode = (int) errorCode;
                this.Message = message;
            }

            public ErrorEventArgs(string name, AITalkResultCode errorCode, string message = "")
            {
                this.Name = name;
                this.Type = AITalkUtilEx.ErrorType.AITalk;
                this.ErrorCode = (int) errorCode;
                this.Message = message;
            }

            public int ErrorCode { get; private set; }

            public string Message { get; private set; }

            public string Name { get; private set; }

            public AITalkUtilEx.ErrorType Type { get; private set; }
        }

        public delegate void ErrorEventHandler(object sender, AITalkUtilEx.ErrorEventArgs e);

        public enum ErrorType
        {
            AITalk,
            AIAudio
        }

        private delegate void EventInVoker<EventArgsType>(EventArgsType e) where EventArgsType: EventArgs;

        public delegate void JobCompleteEventHandler(object sender, EventArgs e);

        public class PhonemeLabelEventArgs : EventArgs
        {
            public PhonemeLabelEventArgs(string label, ulong tick)
            {
                this.Label = label;
                this.Tick = tick;
            }

            public string Label { get; private set; }

            public ulong Tick { get; private set; }
        }

        public delegate void PhonemeLabelEventHandler(object sender, AITalkUtilEx.PhonemeLabelEventArgs e);

        public class SynthesizingEventArgs : EventArgs
        {
            public SynthesizingEventArgs(ulong tick, short[] wave, int size, bool flush, int progress)
            {
                this.Tick = tick;
                if (wave != null)
                {
                    this.Wave = new short[size];
                    Buffer.BlockCopy(wave, 0, this.Wave, 0, size * 2);
                }
                else
                {
                    this.Wave = null;
                }
                this.Flush = flush;
                this.Progress = progress;
            }

            public bool Flush { get; private set; }

            public int Progress { get; private set; }

            public ulong Tick { get; private set; }

            public short[] Wave { get; private set; }
        }

        public delegate void SynthesizingEventHandler(object sender, AITalkUtilEx.SynthesizingEventArgs e);

        public class TextProcessingEventArgs : EventArgs
        {
            public TextProcessingEventArgs(int pos, string text, string kana, int progress)
            {
                this.Pos = pos;
                this.Text = text;
                this.Kana = kana;
                this.Progress = progress;
            }

            public string Kana { get; private set; }

            public int Pos { get; private set; }

            public int Progress { get; private set; }

            public string Text { get; private set; }
        }

        public delegate void TextProcessingEventHandler(object sender, AITalkUtilEx.TextProcessingEventArgs e);

        public class TTSEventArgs : EventArgs
        {
            public TTSEventArgs(ulong tick, string name)
            {
                this.Tick = tick;
                this.Name = name;
            }

            public string Name { get; private set; }

            public ulong Tick { get; private set; }
        }

        public delegate void TTSEventHandler(object sender, AITalkUtilEx.TTSEventArgs e);
    }
}


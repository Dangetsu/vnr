namespace AITalk
{
    using System;
    using System.Runtime.InteropServices;
    using System.Text;
    using System.Threading;

    public class AITalkAPI
    {
        public static int MaxTries = 10;
        public static int SleepTime = 100;

        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_CloseKana")]
        private static extern AITalkResultCode _CloseKana(int jobID, int useEvent = 0);
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_CloseSpeech")]
        private static extern AITalkResultCode _CloseSpeech(int jobID, int useEvent = 0);
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_End")]
        private static extern AITalkResultCode _End();
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_GetData")]
        private static extern AITalkResultCode _GetData(int jobID, short[] rawBuf, uint lenBuf, out uint size);
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_GetJeitaControl")]
        private static extern AITalkResultCode _GetJeitaControl(int jobID, string ctrl);
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_GetKana")]
        private static extern AITalkResultCode _GetKana(int jobID, StringBuilder textBuf, uint lenBuf, out uint size, out uint pos);
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_GetStatus")]
        private static extern AITalkResultCode _GetStatus(int jobID, out AITalkStatusCode status);
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_LangClear")]
        private static extern AITalkResultCode _LangClear();
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_LangLoad")]
        private static extern AITalkResultCode _LangLoad(string dirLang);
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_TextToKana")]
        private static extern AITalkResultCode _TextToKana(out int jobID, ref AITalk_TJobParam param, string text);
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_TextToSpeech")]
        private static extern AITalkResultCode _TextToSpeech(out int jobID, ref AITalk_TJobParam param, string text);
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_VersionInfo")]
        private static extern AITalkResultCode _VersionInfo(int verbose, StringBuilder sjis, uint len, out uint size);
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_VoiceClear")]
        private static extern AITalkResultCode _VoiceClear();
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_VoiceLoad")]
        private static extern AITalkResultCode _VoiceLoad(string voiceName);
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_BLoadWordDic")]
        public static extern AITalkResultCode BLoadWordDic();
        public static AITalkResultCode CloseKana(int jobID, int useEvent = 0)
        {
            int num = 1;
            while (true)
            {
                AITalkResultCode code = _CloseKana(jobID, useEvent);
                if ((code != AITalkResultCode.AITALKERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }

        public static AITalkResultCode CloseSpeech(int jobID, int useEvent = 0)
        {
            int num = 1;
            while (true)
            {
                AITalkResultCode code = _CloseSpeech(jobID, useEvent);
                if ((code != AITalkResultCode.AITALKERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }

        public static AITalkResultCode End()
        {
            int num = 1;
            while (true)
            {
                AITalkResultCode code = _End();
                if ((code != AITalkResultCode.AITALKERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }

        public static AITalkResultCode GetData(int jobID, short[] rawBuf, uint lenBuf, out uint size)
        {
            int num = 1;
            while (true)
            {
                AITalkResultCode code = _GetData(jobID, rawBuf, lenBuf, out size);
                if ((code != AITalkResultCode.AITALKERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }

        public static AITalkResultCode GetJeitaControl(int jobID, string ctrl)
        {
            int num = 1;
            while (true)
            {
                AITalkResultCode code = _GetJeitaControl(jobID, ctrl);
                if ((code != AITalkResultCode.AITALKERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }

        public static AITalkResultCode GetKana(int jobID, StringBuilder textBuf, uint lenBuf, out uint size, out uint pos)
        {
            int num = 1;
            while (true)
            {
                AITalkResultCode code = _GetKana(jobID, textBuf, lenBuf, out size, out pos);
                if ((code != AITalkResultCode.AITALKERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }

        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_GetParam")]
        public static extern AITalkResultCode GetParam(IntPtr pParam, out uint size);
        public static AITalkResultCode GetStatus(int jobID, out AITalkStatusCode status)
        {
            int num = 1;
            while (true)
            {
                AITalkResultCode code = _GetStatus(jobID, out status);
                if ((code != AITalkResultCode.AITALKERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }

        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_Init")]
        public static extern AITalkResultCode Init(ref AITalk_TConfig config);
        public static AITalkResultCode LangClear()
        {
            int num = 1;
            while (true)
            {
                AITalkResultCode code = _LangClear();
                if ((code != AITalkResultCode.AITALKERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }

        public static AITalkResultCode LangLoad(string dirLang)
        {
            int num = 1;
            while (true)
            {
                AITalkResultCode code = _LangLoad(dirLang);
                if ((code != AITalkResultCode.AITALKERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }

        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_ReloadPhraseDic")]
        public static extern AITalkResultCode ReloadPhraseDic(string pathDic);
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_ReloadSymbolDic")]
        public static extern AITalkResultCode ReloadSymbolDic(string pathDic);
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_ReloadWordDic")]
        public static extern AITalkResultCode ReloadWordDic(string pathDic);
        [DllImport("aitalked.dll", EntryPoint="AITalkAPI_SetParam")]
        public static extern AITalkResultCode SetParam(IntPtr pParam);
        public static AITalkResultCode TextToKana(out int jobID, ref AITalk_TJobParam param, string text)
        {
            int num = 1;
            while (true)
            {
                AITalkResultCode code = _TextToKana(out jobID, ref param, text);
                if ((code != AITalkResultCode.AITALKERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }

        public static AITalkResultCode TextToSpeech(out int jobID, ref AITalk_TJobParam param, string text)
        {
            int num = 1;
            while (true)
            {
                AITalkResultCode code = _TextToSpeech(out jobID, ref param, text);
                if ((code != AITalkResultCode.AITALKERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }

        public static AITalkResultCode VersionInfo(int verbose, StringBuilder sjis, uint len, out uint size)
        {
            int num = 1;
            while (true)
            {
                AITalkResultCode code = _VersionInfo(verbose, sjis, len, out size);
                if ((code != AITalkResultCode.AITALKERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }

        public static AITalkResultCode VoiceClear()
        {
            int num = 1;
            while (true)
            {
                AITalkResultCode code = _VoiceClear();
                if ((code != AITalkResultCode.AITALKERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }

        public static AITalkResultCode VoiceLoad(string voiceName)
        {
            int num = 1;
            while (true)
            {
                AITalkResultCode code = _VoiceLoad(voiceName);
                if ((code != AITalkResultCode.AITALKERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }
    }
}


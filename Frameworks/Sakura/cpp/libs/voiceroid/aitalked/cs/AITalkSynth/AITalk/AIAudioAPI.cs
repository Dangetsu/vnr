namespace AITalk
{
    using System;
    using System.Runtime.InteropServices;
    using System.Threading;

    public class AIAudioAPI
    {
        public static int MaxTries = 10;
        public static int SleepTime = 100;

        [DllImport("aitalked.dll", EntryPoint="AIAudioAPI_ClearData")]
        private static extern AIAudioResultCode _ClearData();
        [DllImport("aitalked.dll", EntryPoint="AIAudioAPI_Close")]
        private static extern AIAudioResultCode _Close();
        [DllImport("aitalked.dll", EntryPoint="AIAudioAPI_Open")]
        private static extern AIAudioResultCode _Open(ref AIAudio_TConfig config);
        public static AIAudioResultCode ClearData()
        {
            int num = 1;
            while (true)
            {
                AIAudioResultCode code = _ClearData();
                if ((code != AIAudioResultCode.AIAUDIOERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }

        public static AIAudioResultCode Close()
        {
            int num = 1;
            while (true)
            {
                AIAudioResultCode code = _Close();
                if ((code != AIAudioResultCode.AIAUDIOERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }

        public static AIAudioResultCode Open(ref AIAudio_TConfig config)
        {
            int num = 1;
            while (true)
            {
                AIAudioResultCode code = _Open(ref config);
                if ((code != AIAudioResultCode.AIAUDIOERR_WAIT_TIMEOUT) || (num >= MaxTries))
                {
                    return code;
                }
                Thread.Sleep(SleepTime);
                num++;
            }
        }

        [DllImport("aitalked.dll", EntryPoint="AIAudioAPI_PushData")]
        public static extern AIAudioResultCode PushData(byte[] buf, uint len, int stop);
        [DllImport("aitalked.dll", EntryPoint="AIAudioAPI_PushEvent")]
        public static extern AIAudioResultCode PushEvent(ulong tick, IntPtr userData);
        [DllImport("aitalked.dll", EntryPoint="AIAudioAPI_Resume")]
        public static extern AIAudioResultCode Resume();
        [DllImport("aitalked.dll", EntryPoint="AIAudioAPI_SaveWave")]
        public static extern AIAudioResultCode SaveWave(string path, ref AIAudio_TWaveFormat format, byte[] buf, uint len);
        [DllImport("aitalked.dll", EntryPoint="AIAudioAPI_Suspend")]
        public static extern AIAudioResultCode Suspend();
    }
}


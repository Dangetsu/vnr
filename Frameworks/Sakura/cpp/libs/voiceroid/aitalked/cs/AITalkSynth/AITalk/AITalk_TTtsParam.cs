namespace AITalk
{
    using System;
    using System.Runtime.InteropServices;

    [StructLayout(LayoutKind.Sequential)]
    public struct AITalk_TTtsParam
    {
        public const int MAX_VOICENAME_ = 80;
        public uint size;
        public AITalkProcTextBuf procTextBuf;
        public AITalkProcRawBuf procRawBuf;
        public AITalkProcEventTTS procEventTts;
        public uint lenTextBufBytes;
        public uint lenRawBufBytes;
        public float volume;
        public int pauseBegin;
        public int pauseTerm;
        public string voiceName;
        public TJeitaParam Jeita;
        public uint numSpeakers;
        public int __reserved__;
        public TSpeakerParam[] Speaker;
        [StructLayout(LayoutKind.Sequential)]
        public struct TJeitaParam
        {
            public string femaleName;
            public string maleName;
            public int pauseMiddle;
            public int pauseLong;
            public int pauseSentence;
            public string control;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct TSpeakerParam
        {
            public string voiceName;
            public float volume;
            public float speed;
            public float pitch;
            public float range;
            public int pauseMiddle;
            public int pauseLong;
            public int pauseSentence;
        }
    }
}


namespace AITalk
{
    using System;
    using System.Runtime.InteropServices;

    [StructLayout(LayoutKind.Sequential)]
    public struct AIAudio_TConfig
    {
        public AIAudioProcNotify procNotify;
        public uint msecLatency;
        public uint lenBufferBytes;
        public int hzSamplesPerSec;
        public AIAudioFormatType formatTag;
        public int __reserved__;
    }
}


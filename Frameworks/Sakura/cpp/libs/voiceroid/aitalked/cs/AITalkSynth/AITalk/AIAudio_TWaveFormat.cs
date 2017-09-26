namespace AITalk
{
    using System;
    using System.Runtime.InteropServices;

    [StructLayout(LayoutKind.Sequential)]
    public struct AIAudio_TWaveFormat
    {
        public int header;
        public int hzSamplesPerSec;
        public AIAudioFormatType formatTag;
    }
}


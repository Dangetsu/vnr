namespace AITalk
{
    using System;
    using System.Runtime.InteropServices;

    [StructLayout(LayoutKind.Sequential)]
    public struct AITalk_TConfig
    {
        public int hzVoiceDB;
        public string dirVoiceDBS;
        public uint msecTimeout;
        public string pathLicense;
        public string codeAuthSeed;
        public uint lenAuthSeed;
    }
}


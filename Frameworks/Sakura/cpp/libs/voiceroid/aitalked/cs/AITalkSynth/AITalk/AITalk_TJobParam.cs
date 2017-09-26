namespace AITalk
{
    using System;
    using System.Runtime.InteropServices;

    [StructLayout(LayoutKind.Sequential)]
    public struct AITalk_TJobParam
    {
        public AITalkJobInOut modeInOut;
        public IntPtr userData;
    }
}


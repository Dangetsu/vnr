namespace AITalk
{
    using System;
    using System.Runtime.CompilerServices;

    public delegate int AITalkProcEventTTS(AITalkEventReasonCode reasonCode, int jobID, ulong tick, string name, IntPtr userData);
}


namespace AITalk
{
    using System;
    using System.Runtime.CompilerServices;

    public delegate int AITalkProcRawBuf(AITalkEventReasonCode reasonCode, int jobID, ulong tick, IntPtr userData);
}


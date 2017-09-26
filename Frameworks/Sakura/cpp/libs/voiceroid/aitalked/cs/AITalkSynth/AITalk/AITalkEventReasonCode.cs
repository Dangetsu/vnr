namespace AITalk
{
    using System;

    public enum AITalkEventReasonCode
    {
        AITALKEVENT_BOOKMARK = 0x12e,
        AITALKEVENT_PH_LABEL = 0x12d,
        AITALKEVENT_RAWBUF_CLOSE = 0xcb,
        AITALKEVENT_RAWBUF_FLUSH = 0xca,
        AITALKEVENT_RAWBUF_FULL = 0xc9,
        AITALKEVENT_TEXTBUF_CLOSE = 0x67,
        AITALKEVENT_TEXTBUF_FLUSH = 0x66,
        AITALKEVENT_TEXTBUF_FULL = 0x65
    }
}


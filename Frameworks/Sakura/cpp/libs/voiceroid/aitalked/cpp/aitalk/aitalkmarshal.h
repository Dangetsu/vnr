#pragma once

// aitalkmarshal.h
// 10/11/2014 jichi
#include "aitalk/aitalkdef.h"
#include <sal.h>

namespace AITalk {

namespace AITalkMarshal
{
// AITalkMarshal.cs: public static AITalk_TTtsParam IntPtrToTTtsParam(IntPtr pParam)
const void *ReadTtsParam(_Out_ AITalk_TTtsParam *param, const void *data);

// AITalkMarshal.cs: public static IntPtr TTtsParamToIntPtr(ref AITalk_TTtsParam param)
void *WriteTtsParam(_Out_ void *data, const AITalk_TTtsParam &param);

} // namespace AITalkMarshal

} // namespace AITalk

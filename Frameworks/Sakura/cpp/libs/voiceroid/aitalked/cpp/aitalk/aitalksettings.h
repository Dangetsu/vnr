#pragma once

// aitalksettings.h
// 10/12/2014 jichi
// This class is not part of the original AITalk module.

namespace AITalk {

struct AITalkSettings
{
  float volume;
  unsigned int audioBufferSize; // maximum size of the audio buffer

  AITalkSettings() : volume(1.0), audioBufferSize(0) {}
};

} // namespace AITalk

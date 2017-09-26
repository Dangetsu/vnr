#pragma once

// aitalkconf.h
// 10/11/2014 jichi

#define AITALK_DLL      "aitalked.dll"
#define AITALK_ENCODING "SHIFT-JIS"

#define AITALK_MAX_NAME 80 // maximum length of the voice name string. 80 is used in AITalkMarshal.cs


// SoundOutputSettings.cs:
// if (this.rad8KHzMuLaw.Checked || this.rad8KHz.Checked)
//   args.SamplePerSec = 0x1f40;
// else if (this.rad11KHz.Checked)
//   args.SamplePerSec = 0x2b11;
// else if (this.rad16KHz.Checked)
//   args.SamplePerSec = 0x3e80;
// else
//   args.SamplePerSec = 0x5622;
// Talk API config
// These values are got by debugging AITalkAPI_Init using OllyDbg at runtime
#define AITALK_CONFIG_FREQUENCY     0x5622          // = 22050 Hz, AITalk_TConfig::hzVoiceDB, AITalkUtil::voiceSamplesPerSec
#define AITALK_CONFIG_TIMEOUT       1000            // = 1000 msec, AITalk_TConfig::msecTimeout
#define AITALK_CONFIG_CODEAUTHSEED  "NqKN148elpuO2tmdCMCU" // AITalk_TConfig::codeAuthSeed, see: zunko.cs
#define AITALK_CONFIG_LENAUTHSEED   0               // AITalk_TConfig::lenAuthSeed
#define AITALK_CONFIG_LICENSE       "aitalk.lic"    // relative path of the license file
#define AITALK_CONFIG_VOICENAME     "zunko_22"      // directory "voice/zunko_22"

#define AITALK_CONFIG_BUFFERLENGTH  0x158880        // AITalk_TConfig::lenRawBufBytes, this value comes from AITalkEditor/MainPresenter.cs, default is 176400

// Audio api config, see:  AITalkEditorCore/AITalkEditor/AppSettings.cs
#define AIAUDIO_CONFIG_BUFFERLATENCY    50  // AppSettings.SoundBufferLatency
#define AIAUDIO_CONFIG_BUFFERLENGTH     4   // AppSettings.SoundBufferLength

// EOF

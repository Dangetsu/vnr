#pragma once

// wintts.h
// 4/7/2013 jichi

#ifdef _MSC_VER
# include <cstddef> // for wchar_t
#endif // _MSC_VER

// - Types -

struct ISpVoice;
typedef ISpVoice wintts_t; // opaque handle

// - Constants -

enum {
  WINTTS_DEFAULT = 0,       // = SPF_DEFAULT
  WINTTS_ASYNC = 1L << 0,   // = SPF_ASYNC, won't wait for speak to accomplish
  WINTTS_PURGE = 1L << 1,   // = SPF_PURGEBEFORESPEAK, clear unfinished voice
  WINTTS_PUNCT = 1L << 6    // = SPF_NLP_SPEAK_PUNC, speak out punctuation
};

// - Functions -

wintts_t *wintts_create();
void wintts_destroy(wintts_t *voice);

// Example reg: L"HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Speech\\Voices\\Tokens\\VW Misaki"
bool wintts_set_voice(wintts_t *voice, const wchar_t *reg);

bool wintts_speak(wintts_t *voice, const wchar_t *text, unsigned long flags = 0);

// EOF

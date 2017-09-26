#pragma once

// keyboardhook.h
// 7/20/2011
#include <functional>

// Global instance

void kbhook_start();
void kbhook_stop();
void kbhook_restart();
bool kbhook_active();

///  Return true if eat the event
typedef std::function<bool (unsigned char)> kbhook_fun_t; // byte
extern const kbhook_fun_t kbhook_fun_null;

void kbhook_onkeydown(kbhook_fun_t callback);
void kbhook_onkeyup(kbhook_fun_t callback);

// EOF

#pragma once

// mousehook.h
// 11/26/2011
#include <functional>

// Global instance

void mousehook_start();
void mousehook_stop();
void mousehook_restart();
bool mousehook_active();

///  Return true if eat the event
typedef std::function<bool (int x, int y, void *hwnd)> mousehook_fun_t;
extern const mousehook_fun_t mousehook_fun_null;

void mousehook_onmove(mousehook_fun_t callback);
void mousehook_onlbuttonup(mousehook_fun_t callback);
void mousehook_onlbuttondown(mousehook_fun_t callback);

// EOF

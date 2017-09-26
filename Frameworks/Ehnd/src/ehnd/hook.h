#pragma once
bool hook();
bool hook_userdict();
bool hook_userdict2();
bool hook_getwordinfo();
void user_wordinfo();

bool GetRealWC2MB();
bool GetRealMB2WC();
void *fopen_patch(char *path, char *mode);
void userdict_patch();
void userdict_log(char *s);
void userdict_log2(int idx, int num);
bool userdict_check();
int userdict_proc(char *word_str, char *base, int cur, int total);
UINT calculate_hash(LPCSTR s, int n);
size_t strlen_inline(LPCSTR str);
int __stdcall _WideCharToMultiByte(UINT a, DWORD b, LPCWSTR c, int d, LPSTR e, int f, LPCSTR g, LPBOOL h);
int __stdcall _MultiByteToWideChar(UINT a, DWORD b, LPCSTR c, int d, LPWSTR e, int f);

// hijackmanager.cc
// 6/3/2015 jichi
#include "hijack/hijackmanager.h"
#include "hijack/hijackfuns.h"
#include "winhook/hookfun.h"
#include <windows.h>
#include <unordered_map>

#define DEBUG "hijackmanager"
#include "sakurakit/skdebug.h"

/** Private data */

class HijackManagerPrivate
{
public:
  struct FunctionInfo {
    const char *name; // for debugging purpose
    ulong *oldFunction,
          newFunction;
    bool attached,
         translated;

    explicit FunctionInfo(const char *name = "", ulong *oldFunction = nullptr, ulong newFunction = 0,
        bool attached = false, bool translated = false)
      : name(name), oldFunction(oldFunction), newFunction(newFunction)
      , attached(attached), translated(translated)
    {}
  };
  std::unordered_map<ulong, FunctionInfo> funs; // attached functions


  HijackManagerPrivate();
};

HijackManagerPrivate::HijackManagerPrivate()
{
#define ADD_FUN(_f) funs[(ulong)::_f] = FunctionInfo(#_f, (ulong *)&Hijack::old##_f, (ulong)Hijack::new##_f);
  ADD_FUN(CreateFontA)
  ADD_FUN(CreateFontW)
  ADD_FUN(CreateFontIndirectA)
  ADD_FUN(CreateFontIndirectW)
  ADD_FUN(GetGlyphOutlineA)
  ADD_FUN(GetGlyphOutlineW)
  ADD_FUN(GetTextExtentPoint32A)
  ADD_FUN(GetTextExtentPoint32W)
  ADD_FUN(GetTextExtentExPointA)
  ADD_FUN(GetTextExtentExPointW)
  //ADD_FUN(GetCharABCWidthsA)
  //ADD_FUN(GetCharABCWidthsW)
  ADD_FUN(TextOutA)
  ADD_FUN(TextOutW)
  ADD_FUN(ExtTextOutA)
  ADD_FUN(ExtTextOutW)
  ADD_FUN(TabbedTextOutA)
  ADD_FUN(TabbedTextOutW)
  ADD_FUN(DrawTextA)
  ADD_FUN(DrawTextW)
  ADD_FUN(DrawTextExA)
  ADD_FUN(DrawTextExW)
  ADD_FUN(CharNextA)
  //ADD_FUN(CharNextW)
  //ADD_FUN(CharNextExA)
  //ADD_FUN(CharNextExW)
  ADD_FUN(CharPrevA)
  //ADD_FUN(CharPrevW)
  ADD_FUN(MultiByteToWideChar)
  ADD_FUN(WideCharToMultiByte)
#undef ADD_FUN
}

/** Public data */

HijackManager *HijackManager::instance() { static Self g; return &g; }

HijackManager::HijackManager() : d_(new D) {}
HijackManager::~HijackManager() { delete d_; }

bool HijackManager::isFunctionAttached(ulong addr) const
{
  auto p = d_->funs.find(addr);
  return p != d_->funs.end() && p->second.attached;
}

bool HijackManager::isFunctionTranslated(ulong addr) const
{
  auto p = d_->funs.find(addr);
  return p != d_->funs.end() && p->second.translated;
}

void HijackManager::setFunctionTranslated(ulong addr, bool t)
{
  auto p = d_->funs.find(addr);
  if (p != d_->funs.end())
    p->second.translated = t;
}

void HijackManager::attachFunction(ulong addr, bool translated)
{
  auto p = d_->funs.find(addr);
  if (p == d_->funs.end())
    return;
  auto &info = p->second;
  if (info.attached)
    return;
  DOUT(info.name << ", translated =" << translated);
  info.attached = true;
  info.translated = translated;
  *info.oldFunction = winhook::replace_fun(addr, info.newFunction);
}

void HijackManager::detachFunction(ulong addr)
{
  auto p = d_->funs.find(addr);
  if (p == d_->funs.end())
    return;
  auto &info = p->second;
  if (!info.attached)
    return;
  info.attached = false;
  *info.oldFunction = addr;
  winhook::restore_fun(addr);
}

// EOF

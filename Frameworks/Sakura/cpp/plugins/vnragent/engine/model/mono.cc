// mono.cc
// 7/27/2015 jichi
// https://github.com/mono/mono/blob/master/mono/metadata/object.h
#include "engine/model/mono.h"
#include "engine/enginecontroller.h"
#include "engine/enginedef.h"
#include "engine/enginehash.h"
#include "engine/engineutil.h"
//#include "util/textutil.h"
//#include "hijack/hijackmanager.h"
#include "cpputil/cppcstring.h"
#include "memdbg/memsearch.h"
#include "mono/monoobject.h"
//#include "mono/monotype.h"
#include "winhook/hookcode.h"
#include "unistr/unichar.h"
//#include "winhook/hookfun.h"
//#include "ntdll/ntdll.h"
#include <qt_windows.h>
#include <QtCore/QSet>
#include <cstdint>
#include <unordered_set>

#define DEBUG "model/mono"
#include "sakurakit/skdebug.h"

//#pragma intrinsic(_ReturnAddress)

namespace { // unnamed

//mono_object_get_domain_fun_t mono_object_get_domain;
//mono_string_new_utf16_fun_t mono_string_new_utf16;

namespace MonoHook {
namespace Private {

  ulong scenarioSplit_;
  ulong minimumSplit_,
        maximumSplit_;
  std::unordered_set<ulong> skippedSplits_;

  //void *allocate(size_t size) { return new uint8_t[size]; }
  //void deallocate(void *p) { delete[] (uint8_t *)p; }

  //void MonoStringFree(MonoString *p) { deallocate(p); }

  //MonoString *MonoStringFromQString(const QString &s)
  //{
  //  size_t size = sizeof(MonoString) + sizeof(wchar_t) * (s.size() - 1);
  //  MonoString *ret = (MonoString *)allocate(size);
  //  ret->length = s.size();
  //  s.toWCharArray(ret->chars);
  //  return ret;
  //}

  bool isBadText(const wchar_t *s, size_t size)
  {
    return size <= 1
      || s[0] <= 127 //|| s[size - 1] <= 127
      || unistr::ishangul(s[0]) || unistr::ishangul(s[1]) // avoid re-translating Korean
      || ::cpp_wcsnchr(s, size, '/');
  }

  bool before_mono_string(winhook::hook_stack *s)
  {
    static std::unordered_set<qint64> hashes_;
    //static std::unordered_set<const MonoString *> addresses_;
    auto p = (MonoString *)s->stack[1]; // string in arg1

    if (isBadText(p->chars, p->length)
        //|| addresses_.find(p) != addresses_.end()
        || hashes_.find(Engine::hashWCharArray(p->chars, p->length)) != hashes_.end())
      return true;

    auto role = Engine::OtherRole;

    ulong split = s->ecx;
    for (int i = 0; i < 0x10; i++) // traverse pointers until a non-readable address is met
      if (Engine::isAddressReadable(split))
        split = *(DWORD *)split;
      else
        break;

    if (minimumSplit_ && minimumSplit_ > split ||
        maximumSplit_ && maximumSplit_ < split)
      return true;

    if (!skippedSplits_.empty() && skippedSplits_.find(split) != skippedSplits_.end())
      return true;

    if (p->length > 2 && split == scenarioSplit_) // do not treat two kanji as scenario
      role = Engine::ScenarioRole;

    //auto sig = Engine::hashThreadSignature(role, split); // there is no need to hash role into sig
    QString oldText = QString::fromUtf16(p->chars, p->length),
            newText = EngineController::instance()->dispatchTextW(oldText, role, split);
    if (!newText.isEmpty() && newText != oldText) {
      if (newText.size() > oldText.size())
        newText = newText.left(oldText.size());
      else {
        hashes_.insert(Engine::hashString(newText));
        while (newText.size() < oldText.size())
          newText.push_back(' ');
      }
      newText.toWCharArray(p->chars);
      //addresses_.insert(p);
      hashes_.insert(Engine::hashWCharArray(p->chars, p->length));
    }
    return true;
  }

  void guessSplits()
  {
    if (Engine::globs("CM3D*.exe")) { // Custom Maid 3D 2
      scenarioSplit_ = 0x3;

      //minimumSplit_ = 2;
      minimumSplit_ = 3;

      //minimumSplit_ = 5; // failed
      //minimumSplit_ = 0x8; // work

      maximumSplit_ = 0x20;
      //maximumSplit_ = 0xff;
      //maximumSplit_ = 0xffff;
      //maximumSplit_ = 0xffffff;
      //skippedSplits_.insert(0x0); // could crash the game
      //skippedSplits_.insert(0x1); // could crash the game
      skippedSplits_.insert(0x4); // or position won't work
      skippedSplits_.insert(0x5); // or position won't work
      skippedSplits_.insert(0x6); // or position won't work

      skippedSplits_.insert(0x10); // could cause H-scene to be blackout
      skippedSplits_.insert(0x16); // optional, avoid retranslation
      skippedSplits_.insert(0x19); // optional, avoid retranslation
      //skippedSplits_.insert(0x74747542);  // could crash the game
      return;
    }
    //if (Engine::exists("PlayClub.exe")) // PlayClub
    //  scenarioSplit_ = 0;
  }

  //mono_string_to_utf8_fun_t old_mono_string_to_utf8;
  //char *new_mono_string_to_utf8(MonoString *s)
  //{
  //  if (s && !isBadText(s->chars, s->length)) {
  //    enum { role = Engine::OtherRole, sig = Engine::OtherThreadSignature };
  //    //auto split = (ulong)_ReturnAddress();
  //    //auto sig = Engine::hashThreadSignature(role, split);
  //
  //    QString oldText = QString::fromUtf16(s->chars, s->length),
  //            newText = EngineController::instance()->dispatchTextW(oldText, role, sig);
  //    if (!newText.isEmpty() && newText != oldText) {
  //      MonoDomain *domain = mono_object_get_domain(&s->object);
  //      MonoString *t = mono_string_new_utf16(domain, newText.utf16(), newText.size());
  //      t->object = s->object;
  //      auto ret = old_mono_string_to_utf8(t);
  //      s->object = t->object;
  //      return ret;
  //    }
  //  }
  //  return old_mono_string_to_utf8(s);
  //}

} // namespace Private

bool attach()
{
  ulong fun = Engine::getModuleFunction("mono.dll", "mono_string_to_utf8");
  if (!fun)
    return false;
  Private::guessSplits();
  return winhook::hook_before(fun, Private::before_mono_string);
  //return fun && (Private::old_mono_string_to_utf8 = (mono_string_to_utf8_fun_t)winhook::replace_fun(fun, (ulong)Private::new_mono_string_to_utf8));
}

} // namespace MonoHook
} // unnamed namespace

/** Public class */

bool MonoEngine::match() { return ::GetModuleHandleA("mono.dll"); }

bool MonoEngine::attach()
{
  //mono_object_get_domain = (mono_object_get_domain_fun_t)Engine::getModuleFunction("mono.dll", "mono_object_get_domain");
  //mono_string_new_utf16 = (mono_string_new_utf16_fun_t)Engine::getModuleFunction("mono.dll", "mono_string_new_utf16");

  return MonoHook::attach();
}

// EOF

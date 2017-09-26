// profile.cc
// 6/15/2014

#include "profile/d3dx.h"
//#include "profile/locale.h"

namespace Profile {

void destroy() {}

void load()
{
  //LocaleProfile::load();
  D3DXProfile::load();
}

} // namespace Profile

// EOF

#ifndef TRRENDER_H
#define TRRENDER_H

// trrender.h
// 9/20/2014 jichi
#include <string>

// Render a translation rule into a json href link. Complete controls whether inline target as json.
std::wstring tr_render_rule(const std::wstring &target, int id = 0);

#endif // TRRENDER_H

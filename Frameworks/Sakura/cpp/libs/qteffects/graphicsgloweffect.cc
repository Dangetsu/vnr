// graphicsglowweffect.cc
// 5/3/2012 jichi
// See: gui/effects/qgraphicseffect.cpp
#include "qteffects/graphicsgloweffect.h"
#include "qteffects/pixmapglowfilter_p.h"

QTEFFECTS_BEGIN_NAMESPACE

// - Construction -

GraphicsGlowEffect::GraphicsGlowEffect(QObject *parent)
  : Base(new PixmapGlowFilter, parent) {}

GraphicsGlowEffect::~GraphicsGlowEffect() {}

QTEFFECTS_END_NAMESPACE

// EOF

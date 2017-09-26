// graphicstextshadoweffect.cc
// 5/3/2012 jichi
// See: gui/effects/qgraphicseffect.cpp
#include "qteffects/graphicstextshadoweffect.h"
#include "qteffects/pixmaptextshadowfilter_p.h"

QTEFFECTS_BEGIN_NAMESPACE

// - Construction -

GraphicsTextShadowEffect::GraphicsTextShadowEffect(QObject *parent)
  : Base(new PixmapTextShadowFilter, parent) {}

GraphicsTextShadowEffect::~GraphicsTextShadowEffect() {}

QTEFFECTS_END_NAMESPACE

// EOF

#ifndef _QTEFFECTS_GRAPHICSTEXTSHADOWEFFECT_H
#define _QTEFFECTS_GRAPHICSTEXTSHADOWEFFECT_H

// graphicstextshadoweffect.h
// 5/3/2012 jichi
// See: qt/src/gui/effects/qgraphicseffect.h

#include "qteffects/graphicsabstractblureffect_p.h"

QTEFFECTS_BEGIN_NAMESPACE

class GraphicsTextShadowEffect: public GraphicsAbstractBlurEffect
{
  Q_OBJECT
  Q_DISABLE_COPY(GraphicsTextShadowEffect)
  typedef GraphicsTextShadowEffect Self;
  typedef GraphicsAbstractBlurEffect Base;

public:
  explicit GraphicsTextShadowEffect(QObject *parent = nullptr);
  ~GraphicsTextShadowEffect();
};

QTEFFECTS_END_NAMESPACE

#endif // _QTEFFECTS_GRAPHICSTEXTSHADOWEFFECT_H

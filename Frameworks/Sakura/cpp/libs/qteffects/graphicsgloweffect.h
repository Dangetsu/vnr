#ifndef _QTEFFECTS_GRAPHICSGLOWEFFECT_H
#define _QTEFFECTS_GRAPHICSGLOWEFFECT_H

// graphicsGloweffect.h
// 5/3/2012 jichi
// See: qt/src/gui/effects/qgraphicseffect.h

#include "qteffects/graphicsabstractblureffect_p.h"

QTEFFECTS_BEGIN_NAMESPACE

class GraphicsGlowEffect: public GraphicsAbstractBlurEffect
{
  Q_OBJECT
  Q_DISABLE_COPY(GraphicsGlowEffect)
  typedef GraphicsGlowEffect Self;
  typedef GraphicsAbstractBlurEffect Base;

public:
  explicit GraphicsGlowEffect(QObject *parent = nullptr);
  ~GraphicsGlowEffect();
};

QTEFFECTS_END_NAMESPACE

#endif // _QTEFFECTS_GRAPHICSGLOWEFFECT_H

// graphicsglowweffect2.cc
// 5/3/2012 jichi
// See: gui/effects/qgraphicseffect.cpp
#include "qteffects/graphicsgloweffect2.h"
#include "qteffects/pixmapglowfilter2_p.h"

#define D_F PixmapGlowFilter2 * const f = static_cast<PixmapGlowFilter2 *>(pixmapFilter())

QTEFFECTS_BEGIN_NAMESPACE

// - Construction -

GraphicsGlowEffect2::GraphicsGlowEffect2(QObject *parent)
  : Base(new PixmapGlowFilter2, parent) {}

GraphicsGlowEffect2::~GraphicsGlowEffect2() {}

// - Properties -

bool GraphicsGlowEffect2::isEnabled2() const
{
  D_F;
  return f->isEnabled2();
}

void GraphicsGlowEffect2::setEnabled2(bool t)
{
  D_F;
  if (f->isEnabled2() == t)
    return;

  f->setEnabled2(t);
  //updateBoundingRect();
  //if (t)
  update();
  emit enabled2Changed(t);
}


QPointF GraphicsGlowEffect2::offset2() const
{
  D_F;
  return f->offset();
}

void GraphicsGlowEffect2::setOffset2(const QPointF &offset)
{
  D_F;
  if (f->offset() == offset)
    return;

  f->setOffset2(offset);
  if (f->isEnabled2())
    update();
  //updateBoundingRect();
  emit offset2Changed(offset);
}

int GraphicsGlowEffect2::blurIntensity2() const
{
  D_F;
  return f->blurIntensity2();
}

void GraphicsGlowEffect2::setBlurIntensity2(int intensity)
{
  D_F;
  if (f->blurIntensity2() == intensity)
    return;

  f->setBlurIntensity2(intensity);
  if (f->isEnabled2())
    update();
  emit blurIntensity2Changed(intensity);
}

qreal GraphicsGlowEffect2::blurRadius2() const
{
  D_F;
  return f->blurRadius2();
}

void GraphicsGlowEffect2::setBlurRadius2(qreal radius)
{
  D_F;
  if (qFuzzyCompare(f->blurRadius2(), radius))
    return;

  f->setBlurRadius2(radius);
  if (f->isEnabled2())
    update();
  //updateBoundingRect();
  emit blurRadius2Changed(radius);
}

QColor GraphicsGlowEffect2::color2() const
{
  D_F;
  return f->color2();
}

void GraphicsGlowEffect2::setColor2(const QColor &color)
{
  D_F;
  if (f->color2() == color)
    return;

  f->setColor2(color);
  if (f->isEnabled2())
    update();
  emit color2Changed(color);
}

QTEFFECTS_END_NAMESPACE

// EOF

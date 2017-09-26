// pixmapabstractblurfilter_p.cc
// 5/3/2012 jichi
// See: gui/image/pixmapfilter_p.cpp

#include "qteffects/pixmapabstractblurfilter_p.h"
#include "qteffects/pixmapabstractblurfilter_p_p.h"

QTEFFECTS_BEGIN_NAMESPACE

// - Construction -

PixmapAbstractBlurFilter::PixmapAbstractBlurFilter(QObject *parent)
  : Base(*new PixmapAbstractBlurFilterPrivate, UserFilter, parent) {}

PixmapAbstractBlurFilter::PixmapAbstractBlurFilter(PixmapAbstractBlurFilterPrivate &d, FilterType type, QObject *parent)
  : Base(d, type, parent) {}

// - Properties -

int PixmapAbstractBlurFilter::blurIntensity() const
{
  Q_D(const PixmapAbstractBlurFilter);
  return d->intensity;
}
void PixmapAbstractBlurFilter::setBlurIntensity(int intensity)
{
  Q_D(PixmapAbstractBlurFilter);
  d->intensity = intensity;
}

qreal PixmapAbstractBlurFilter::blurRadius() const
{
  Q_D(const PixmapAbstractBlurFilter);
  return d->radius;
}
void PixmapAbstractBlurFilter::setBlurRadius(qreal radius)
{
  Q_D(PixmapAbstractBlurFilter);
  d->radius = radius;
}

QColor PixmapAbstractBlurFilter::color() const
{
  Q_D(const PixmapAbstractBlurFilter);
  return d->color;
}

void PixmapAbstractBlurFilter::setColor(const QColor &color)
{
  Q_D(PixmapAbstractBlurFilter);
  d->color = color;
}

QPointF PixmapAbstractBlurFilter::offset() const
{
  Q_D(const PixmapAbstractBlurFilter);
  return d->offset;
}

void PixmapAbstractBlurFilter::setOffset(const QPointF &offset)
{
  Q_D(PixmapAbstractBlurFilter);
  d->offset = offset;
}

// - Paint -

QRectF PixmapAbstractBlurFilter::boundingRectFor(const QRectF &rect) const
{
  Q_D(const PixmapAbstractBlurFilter);
  qreal radius = d->radius;
  return rect.united(
    rect.translated(d->offset).adjusted(-radius, -radius, radius, radius)
  );
}

QTEFFECTS_END_NAMESPACE

// EOF

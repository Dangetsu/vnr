// graphicsabstractblureffect.cc
// 5/3/2012 jichi
// See: gui/effects/qgraphicseffect.cpp
#include "qteffects/graphicsabstractblureffect_p.h"
#include "qteffects/pixmapabstractblurfilter_p.h"
#include <qt/src/gui/effects/qgraphicseffect_p.h>
#include <qt/src/gui/painting/qdrawhelper_p.h>
#include <QtGui/QPaintEngine>

QTEFFECTS_BEGIN_NAMESPACE

/** Private class */

class GraphicsAbstractBlurEffectPrivate : public QGraphicsEffectPrivate
{
  Q_DECLARE_PUBLIC(GraphicsAbstractBlurEffect)
public:
  GraphicsAbstractBlurEffectPrivate(PixmapAbstractBlurFilter *f)
    : filter(f), enabled(true), opacity(1.0) {}
  ~GraphicsAbstractBlurEffectPrivate() { delete filter; }

  PixmapAbstractBlurFilter *filter;
  bool enabled;
  qreal opacity;
};

/** Public class */

// - Construction -

GraphicsAbstractBlurEffect::GraphicsAbstractBlurEffect(PixmapAbstractBlurFilter *filter, QObject *parent)
  : Base(*new GraphicsAbstractBlurEffectPrivate(filter), parent) {}

GraphicsAbstractBlurEffect::~GraphicsAbstractBlurEffect() {}

// - Properties -

PixmapAbstractBlurFilter *GraphicsAbstractBlurEffect::pixmapFilter() const
{
  Q_D(const GraphicsAbstractBlurEffect);
  return d->filter;
}

bool GraphicsAbstractBlurEffect::isEnabled() const
{
  Q_D(const GraphicsAbstractBlurEffect);
  return d->enabled;
}

void GraphicsAbstractBlurEffect::setEnabled(bool t)
{
  Q_D(GraphicsAbstractBlurEffect);
  if (d->enabled == t)
    return;

  d->enabled = t;
  //if (t)
  updateBoundingRect();
  emit enabledChanged(t);
}


QPointF GraphicsAbstractBlurEffect::offset() const
{
  Q_D(const GraphicsAbstractBlurEffect);
  return d->filter->offset();
}

void GraphicsAbstractBlurEffect::setOffset(const QPointF &offset)
{
  Q_D(GraphicsAbstractBlurEffect);
  if (d->filter->offset() == offset)
    return;

  d->filter->setOffset(offset);
  if (d->enabled)
    updateBoundingRect();
  emit offsetChanged(offset);
}

int GraphicsAbstractBlurEffect::blurIntensity() const
{
  Q_D(const GraphicsAbstractBlurEffect);
  return d->filter->blurIntensity();
}

void GraphicsAbstractBlurEffect::setBlurIntensity(int intensity)
{
  Q_D(GraphicsAbstractBlurEffect);
  if (d->filter->blurIntensity() == intensity)
    return;

  d->filter->setBlurIntensity(intensity);
  if (d->enabled)
    update();
  emit blurIntensityChanged(intensity);
}

qreal GraphicsAbstractBlurEffect::blurRadius() const
{
  Q_D(const GraphicsAbstractBlurEffect);
  return d->filter->blurRadius();
}

void GraphicsAbstractBlurEffect::setBlurRadius(qreal radius)
{
  Q_D(GraphicsAbstractBlurEffect);
  if (qFuzzyCompare(d->filter->blurRadius(), radius))
    return;

  d->filter->setBlurRadius(radius);
  if (d->enabled)
    updateBoundingRect();
  emit blurRadiusChanged(radius);
}

QColor GraphicsAbstractBlurEffect::color() const
{
  Q_D(const GraphicsAbstractBlurEffect);
  return d->filter->color();
}

void GraphicsAbstractBlurEffect::setColor(const QColor &color)
{
  Q_D(GraphicsAbstractBlurEffect);
  if (d->filter->color() == color)
    return;

  d->filter->setColor(color);
  if (d->enabled)
    update();
  emit colorChanged(color);
}

qreal GraphicsAbstractBlurEffect::opacity() const
{
  Q_D(const GraphicsAbstractBlurEffect);
  return d->opacity;
}

void GraphicsAbstractBlurEffect::setOpacity(qreal opacity)
{
  Q_D(GraphicsAbstractBlurEffect);
  if (qFuzzyCompare(d->opacity, opacity))
    return;

  d->opacity = opacity;
  if (d->enabled)
    update();
  emit opacityChanged(opacity);
}

// - Methods -

QRectF GraphicsAbstractBlurEffect::boundingRectFor(const QRectF &rect) const
{
  Q_D(const GraphicsAbstractBlurEffect);
  if (!d->enabled)
    return rect;
  return d->filter->boundingRectFor(rect);
}

void GraphicsAbstractBlurEffect::draw(QPainter *painter)
{
  Q_ASSERT(painter);
  Q_ASSERT(painter->isActive());    // NOT true when rendering widgets on mac
#ifdef Q_OS_MAC
  if (!painter->isActive() || !painter->paintEngine()) {
    drawSource(painter);
    return;
  }
#endif // Q_OS_MAC
  Q_D(const GraphicsAbstractBlurEffect);
  if (!d->enabled) {
    drawSource(painter);
    return;
  }

  if (!qFuzzyCompare(d->opacity, 1))
    painter->setOpacity(d->opacity);
  if (d->filter->blurRadius() <= 0 && d->filter->offset().isNull()) {
    drawSource(painter);
    return;
  }

  PixmapPadMode mode = PadToEffectiveBoundingRect;
  Q_ASSERT(painter->paintEngine()); // NOT true when rendering widgets on mac
  if (painter->paintEngine()->type() == QPaintEngine::OpenGL2)
    mode = NoPad;

  // Draw pixmap in device coordinates to avoid pixmap scaling.
  QPoint offset;
  const QPixmap pixmap = sourcePixmap(Qt::DeviceCoordinates, &offset, mode);
  if (pixmap.isNull()) {
    drawSource(painter);
    return;
  }

  QTransform restoreTransform = painter->worldTransform();
  painter->setWorldTransform(QTransform());

  d->filter->draw(painter, offset, pixmap);

  painter->setWorldTransform(restoreTransform);
}

QTEFFECTS_END_NAMESPACE

// EOF

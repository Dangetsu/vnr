#ifndef _QTEFFECTS_GRAPHICSABSTRACTBLUREFFECT_H
#define _QTEFFECTS_GRAPHICSABSTRACTBLUREFFECT_H

// graphicsabstractblureffect_p.h
// 5/3/2012 jichi
// See: qt/src/gui/effects/qgraphicseffect.h

#include "qteffects/qteffects.h"
#include <QtGui/QGraphicsEffect>

QTEFFECTS_BEGIN_NAMESPACE

class PixmapAbstractBlurFilter;
class GraphicsAbstractBlurEffectPrivate;
class GraphicsAbstractBlurEffect: public QGraphicsEffect
{
  Q_OBJECT
  Q_PROPERTY(bool enabled READ isEnabled WRITE setEnabled NOTIFY enabledChanged)
  Q_PROPERTY(QPointF offset READ offset WRITE setOffset NOTIFY offsetChanged)
  Q_PROPERTY(qreal xOffset READ xOffset WRITE setXOffset NOTIFY offsetChanged)
  Q_PROPERTY(qreal yOffset READ yOffset WRITE setYOffset NOTIFY offsetChanged)
  Q_PROPERTY(qreal blurRadius READ blurRadius WRITE setBlurRadius NOTIFY blurRadiusChanged)
  Q_PROPERTY(int blurIntensity READ blurIntensity WRITE setBlurIntensity NOTIFY blurIntensityChanged)
  Q_PROPERTY(QColor color READ color WRITE setColor NOTIFY colorChanged)
  Q_PROPERTY(qreal opacity READ opacity WRITE setOpacity NOTIFY opacityChanged)
  Q_DECLARE_PRIVATE(GraphicsAbstractBlurEffect)
  Q_DISABLE_COPY(GraphicsAbstractBlurEffect)
  typedef GraphicsAbstractBlurEffect Self;
  typedef QGraphicsEffect Base;

public:
  explicit GraphicsAbstractBlurEffect(PixmapAbstractBlurFilter *filter, QObject *parent = nullptr);
  ~GraphicsAbstractBlurEffect();

  bool isEnabled() const;

  QRectF boundingRectFor(const QRectF &rect) const override;
  QPointF offset() const;
  qreal xOffset() const { return offset().x(); }
  qreal yOffset() const { return offset().y(); }

  int blurIntensity() const;
  qreal blurRadius() const;
  QColor color() const;

  qreal opacity() const;

public slots:
  void setEnabled(bool t);

  void setOffset(const QPointF &ofs);
  void setOffset(qreal dx, qreal dy) { setOffset(QPointF(dx, dy)); }
  void setOffset(qreal d) { setOffset(QPointF(d, d)); }

  void setXOffset(qreal dx) { setOffset(QPointF(dx, yOffset())); }
  void setYOffset(qreal dy) { setOffset(QPointF(xOffset(), dy)); }

  void setBlurIntensity(int intensity);
  void setBlurRadius(qreal radius);
  void setColor(const QColor &color);
  void setOpacity(qreal opacity);

signals:
  void enabledChanged(bool enabled);
  void offsetChanged(const QPointF &offset);
  void blurIntensityChanged(int intensity);
  void blurRadiusChanged(qreal radius);
  void colorChanged(const QColor &color);
  void opacityChanged(qreal opacity);

protected:
  PixmapAbstractBlurFilter *pixmapFilter() const;
  void draw(QPainter *painter) override;
};

QTEFFECTS_END_NAMESPACE

#endif // _QTEFFECTS_GRAPHICSABSTRACTBLUREFFECT_H

#ifndef _QTEFFECTS_PIXMAPABSTRACTBLURFILTER_P_H
#define _QTEFFECTS_PIXMAPABSTRACTBLURFILTER_P_H

// pixmapabstractblurfilter_p.h
// 5/3/2012 jichi
// See: gui/image/pixmapfilter_p.h

#include "qteffects/qteffects.h"
#include <qt/src/gui/image/qpixmapfilter_p.h>

QTEFFECTS_BEGIN_NAMESPACE

class PixmapAbstractBlurFilterPrivate;
class PixmapAbstractBlurFilter : public QPixmapFilter
{
  Q_OBJECT
  Q_DECLARE_PRIVATE(PixmapAbstractBlurFilter)
  Q_DISABLE_COPY(PixmapAbstractBlurFilter)
  typedef PixmapAbstractBlurFilter Self;
  typedef QPixmapFilter Base;

public:
  //enum { Type = UserFilter + DropShadowFilter }; ///< must be unique to all QPixMapFilter class
  explicit PixmapAbstractBlurFilter(QObject *parent = nullptr);
  PixmapAbstractBlurFilter(PixmapAbstractBlurFilterPrivate &d, FilterType type, QObject *parent);

  int blurIntensity() const; // default 1
  void setBlurIntensity(int count);

  qreal blurRadius() const;
  void setBlurRadius(qreal radius);

  QColor color() const;
  void setColor(const QColor &color);

  QPointF offset() const;
  void setOffset(const QPointF &offset);
  void setOffset(qreal dx, qreal dy) { setOffset(QPointF(dx, dy)); }

  QRectF boundingRectFor(const QRectF &rect) const override;
  //virtual void draw(QPainter *p, const QPointF &pos, const QPixmap &px, const QRectF &src = QRectF()) const override = 0;
};

QTEFFECTS_END_NAMESPACE

#endif // _QTEFFECTS_PIXMAPABSTRACTBLURFILTER_P_H

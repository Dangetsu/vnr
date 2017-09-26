#ifndef _QTEFFECTS_PIXMAPGLOWFILTER2_P_H
#define _QTEFFECTS_PIXMAPGLOWFILTER2_P_H

// pixmapglowfilter_p.h
// 5/3/2012 jichi
// See: gui/image/pixmapfilter_p.h

#include "qteffects/pixmapabstractblurfilter_p.h"

QTEFFECTS_BEGIN_NAMESPACE

class PixmapGlowFilter2Private;
class PixmapGlowFilter2 : public PixmapAbstractBlurFilter
{
  Q_OBJECT
  Q_DECLARE_PRIVATE(PixmapGlowFilter2)
  Q_DISABLE_COPY(PixmapGlowFilter2)
  typedef PixmapGlowFilter2 Self;
  typedef PixmapAbstractBlurFilter Base;

public:
  explicit PixmapGlowFilter2(QObject *parent = nullptr);
  ~PixmapGlowFilter2();

  bool isEnabled2() const;
  void setEnabled2(bool t);

  int blurIntensity2() const; // default 1
  void setBlurIntensity2(int count);

  qreal blurRadius2() const;
  void setBlurRadius2(qreal radius);

  QColor color2() const;
  void setColor2(const QColor &color);

  QPointF offset2() const;
  void setOffset2(const QPointF &offset);
  void setOffset2(qreal dx, qreal dy) { setOffset(QPointF(dx, dy)); }

  // This should be reimplemented
  //QRectF boundingRectFor(const QRectF &rect) const override;

  void draw(QPainter *p, const QPointF &pos, const QPixmap &px, const QRectF &src = QRectF()) const override;
};

QTEFFECTS_END_NAMESPACE

#endif // _QTEFFECTS_PIXMAPGLOWFILTER_P2_H

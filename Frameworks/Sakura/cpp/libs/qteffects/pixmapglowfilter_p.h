#ifndef _QTEFFECTS_PIXMAPGLOWFILTER_P_H
#define _QTEFFECTS_PIXMAPGLOWFILTER_P_H

// pixmapglowfilter_p.h
// 5/3/2012 jichi
// See: gui/image/pixmapfilter_p.h

#include "qteffects/pixmapabstractblurfilter_p.h"

QTEFFECTS_BEGIN_NAMESPACE

class PixmapGlowFilter : public PixmapAbstractBlurFilter
{
  Q_OBJECT
  Q_DISABLE_COPY(PixmapGlowFilter)
  typedef PixmapGlowFilter Self;
  typedef PixmapAbstractBlurFilter Base;

  PixmapAbstractBlurFilterPrivate *d_func() { return reinterpret_cast<PixmapAbstractBlurFilterPrivate *>(qGetPtrHelper(d_ptr)); } \
  const PixmapAbstractBlurFilterPrivate *d_func() const { return reinterpret_cast<const PixmapAbstractBlurFilterPrivate *>(qGetPtrHelper(d_ptr)); } \
public:
  explicit PixmapGlowFilter(QObject *parent = nullptr);
  ~PixmapGlowFilter();
  void draw(QPainter *p, const QPointF &pos, const QPixmap &px, const QRectF &src = QRectF()) const override;
};

QTEFFECTS_END_NAMESPACE

#endif // _QTEFFECTS_PIXMAPGLOWFILTER_P_H

// pixmapglowfilter_p.cc
// 5/3/2012 jichi

#include "qteffects/pixmapglowfilter_p.h"
#include "qteffects/pixmapabstractblurfilter_p_p.h"
#include "qteffects/imagefilters_q.h"
#include "qteffects/pixmapfilter_q.h"
#include <QtGui/QPainter>
#include <QtGui/QPaintEngine>

QTEFFECTS_BEGIN_NAMESPACE

PixmapGlowFilter::PixmapGlowFilter(QObject *parent): Base(parent) {}
PixmapGlowFilter::~PixmapGlowFilter() {}

void PixmapGlowFilter::draw(QPainter *p, const QPointF &pos, const QPixmap &px, const QRectF &src) const
{
  if (px.isNull())
    return;
  Q_D(const PixmapAbstractBlurFilter);
  if (QPaintEngine *e = p->paintEngine())
    if (e->isExtended())
      if (QPixmapFilter *filter = static_cast<QPaintEngineEx *>(e)->pixmapFilter(type(), this))
        if (Self *that = dynamic_cast<Self *>(filter)) {
          that->setColor(d->color);
          that->setBlurIntensity(d->intensity);
          that->setBlurRadius(d->radius);
          that->setOffset(d->offset);
          that->draw(p, pos, px, src);
          return;
        }

  // See: https://github.com/qtcn/tianchi/blob/master/src/gui/tcgloweffect.cpp
  qreal radius = d->radius;
  QImage img(px.size() + QSize(radius * 2, radius * 2), QImage::Format_ARGB32_Premultiplied);
  img.fill(0);
  QPainter imgPainter(&img);
  imgPainter.drawPixmap(d->offset, px);
  imgPainter.setCompositionMode(QPainter::CompositionMode_SourceIn);
  imgPainter.fillRect(img.rect(), d->color);
  imgPainter.end();
  qt_blurImage(img, radius, true);

  // FIXME: This is very inefficient
  for (int i = 0; i < d->intensity; i++)
    p->drawImage(pos, img);

  p->drawPixmap(pos, px);
}

QTEFFECTS_END_NAMESPACE

// EOF

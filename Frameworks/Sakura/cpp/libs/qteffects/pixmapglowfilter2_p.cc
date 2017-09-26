// pixmapglowfilter2_p.cc
// 5/3/2012 jichi

#include "qteffects/pixmapglowfilter2_p.h"
#include "qteffects/pixmapabstractblurfilter_p_p.h"
#include "qteffects/imagefilters_q.h"
#include "qteffects/pixmapfilter_q.h"
#include <QtGui/QPainter>
#include <QtGui/QPaintEngine>

QTEFFECTS_BEGIN_NAMESPACE

/** Private class **/

class PixmapGlowFilter2Private : public PixmapAbstractBlurFilterPrivate
{
  Q_DECLARE_PUBLIC(PixmapAbstractBlurFilter)

public:
  bool enabled2;
  int intensity2;
  QPointF offset2;
  QColor color2;
  qreal radius2;

  PixmapGlowFilter2Private():
    enabled2(true),
    intensity2(1),
    //offset2(0, 0), //offset(8, 8),
    //color2(Qt::black),
    radius2(1) {}
};

/** Public class **/

// - Constructors -

PixmapGlowFilter2::PixmapGlowFilter2(QObject *parent)
  : Base(*new PixmapGlowFilter2Private, UserFilter, parent) {}

PixmapGlowFilter2::~PixmapGlowFilter2() {}

// - Properties -

bool PixmapGlowFilter2::isEnabled2() const
{
  Q_D(const PixmapGlowFilter2);
  return d->enabled2;
}

void PixmapGlowFilter2::setEnabled2(bool t)
{
  Q_D(PixmapGlowFilter2);
  d->enabled2 = t;
}

int PixmapGlowFilter2::blurIntensity2() const
{
  Q_D(const PixmapGlowFilter2);
  return d->intensity2;
}

void PixmapGlowFilter2::setBlurIntensity2(int intensity)
{
  Q_D(PixmapGlowFilter2);
  d->intensity2 = intensity;
}

qreal PixmapGlowFilter2::blurRadius2() const
{
  Q_D(const PixmapGlowFilter2);
  return d->radius2;
}
void PixmapGlowFilter2::setBlurRadius2(qreal radius)
{
  Q_D(PixmapGlowFilter2);
  d->radius2 = radius;
}

QColor PixmapGlowFilter2::color2() const
{
  Q_D(const PixmapGlowFilter2);
  return d->color2;
}

void PixmapGlowFilter2::setColor2(const QColor &color)
{
  Q_D(PixmapGlowFilter2);
  d->color2 = color;
}

QPointF PixmapGlowFilter2::offset2() const
{
  Q_D(const PixmapGlowFilter2);
  return d->offset2;
}

void PixmapGlowFilter2::setOffset2(const QPointF &offset)
{
  Q_D(PixmapGlowFilter2);
  d->offset2 = offset;
}

// - Methods -

void PixmapGlowFilter2::draw(QPainter *p, const QPointF &pos, const QPixmap &px, const QRectF &src) const
{
  if (px.isNull())
    return;
  Q_D(const PixmapGlowFilter2);
  if (QPaintEngine *e = p->paintEngine())
    if (e->isExtended())
      if (QPixmapFilter *filter = static_cast<QPaintEngineEx *>(e)->pixmapFilter(type(), this))
        if (Self *that = dynamic_cast<Self *>(filter)) {
          that->setColor(d->color);
          that->setBlurIntensity(d->intensity);
          that->setBlurRadius(d->radius);
          that->setOffset(d->offset);
          that->setEnabled2(d->enabled2);
          that->setColor2(d->color2);
          that->setBlurIntensity2(d->intensity2);
          that->setBlurRadius2(d->radius2);
          that->setOffset2(d->offset2);
          that->draw(p, pos, px, src);
          return;
        }

  if (d->enabled2) {
    qreal radius = d->radius2;
    QImage img(px.size() + QSize(radius * 2, radius * 2),
            QImage::Format_ARGB32_Premultiplied);
    img.fill(0);
    QPainter imgPainter(&img);
    imgPainter.drawPixmap(d->offset2, px);
    imgPainter.setCompositionMode(QPainter::CompositionMode_SourceIn);
    imgPainter.fillRect(img.rect(), d->color2);
    imgPainter.end();
    qt_blurImage(img, radius, true);
    for (int i = 0; i < d->intensity2; i++)
      p->drawImage(pos, img);
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
  for (int i = 0; i < d->intensity; i++)
    p->drawImage(pos, img);

  p->drawPixmap(pos, px);
}

QTEFFECTS_END_NAMESPACE

// EOF

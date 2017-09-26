// contouredtextedit.cc
// 4/5/2014 jichi
#include "qmltext/contouredtextedit.h"
#include "qtimage/contour.h"
#include <qt/src/declarative/graphicsitems/qdeclarativetextedit_p_p.h>
#include <qt/src/gui/text/qtextcontrol_p.h>
#include <QtGui/QPainter>

#define D_ITEM(Class)   reinterpret_cast<Class##Private *>(QGraphicsItem::d_ptr.data())
#define D_BASE  D_ITEM(QDeclarativeTextEdit)

/** Private class */

class DeclarativeContouredTextEditPrivate
{
public:
  bool enabled;
  int radius;
  QColor color;
  QPoint offset;

  DeclarativeContouredTextEditPrivate() : enabled(true), radius(0) {}
};

/** Public class */

// Construction

DeclarativeContouredTextEdit::DeclarativeContouredTextEdit(QDeclarativeItem *parent)
  : Base(parent), d_(new D) {}

DeclarativeContouredTextEdit::~DeclarativeContouredTextEdit() { delete d_; }

// Properties

bool DeclarativeContouredTextEdit::isContourEnabled() const { return d_->enabled; }

void DeclarativeContouredTextEdit::setContourEnabled(bool v)
{
  if (d_->enabled != v) {
    //prepareGeometryChange();
    d_->enabled = v;
    emit contourEnabledChanged();
    update();
  }
}

QColor DeclarativeContouredTextEdit::contourColor() const { return d_->color; }

void DeclarativeContouredTextEdit::setContourColor(const QColor &v)
{
  if (d_->color != v) {
    d_->color = v;
    emit contourColorChanged();
    update();
  }
}

int DeclarativeContouredTextEdit::contourRadius() const { return d_->radius; }

void DeclarativeContouredTextEdit::setContourRadius(int v)
{
  if (d_->radius != v) {
    //prepareGeometryChange();
    d_->radius = v;
    emit contourRadiusChanged();
    update();
  }
}

QPoint DeclarativeContouredTextEdit::contourOffset() const { return d_->offset; }

void DeclarativeContouredTextEdit::setContourOffset(const QPoint &v)
{
  if (d_->offset != v) {
    //prepareGeometryChange();
    d_->offset = v;
    emit contourOffsetChanged();
    update();
  }
}

// Paint

// See: src/declarative/qgraphicsitems/qdeclarativetextedit.cpp
void DeclarativeContouredTextEdit::drawContents(QPainter *painter, const QRect &bounds)
{
  if (!d_->enabled) {
    Base::drawContents(painter, bounds);
    return;
  }
  auto d = D_BASE;

  painter->setRenderHint(QPainter::TextAntialiasing, true);
  painter->translate(0, d->yoff);

  QRect r = bounds.translated(0, -d->yoff);

  //QImage img(painter->device()->width(), painter->device()->height(), QImage::Format_ARGB32_Premultiplied); // slower to create image, faster to render
  QImage img(painter->device()->width(), painter->device()->height(), QImage::Format_ARGB32);
  img.fill(0);

  QPainter imgPainter(&img);
  d->control->document()->drawContents(&imgPainter, r);
  imgPainter.end();

  img = QtImage::contourImage(img, d_->color, d_->radius, d_->offset); // easingAlpha = true
  painter->drawImage(0, 0, img);

  d->control->drawContents(painter, r);

  painter->translate(0, -d->yoff);
}

// EOF

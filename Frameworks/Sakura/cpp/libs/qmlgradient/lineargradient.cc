// lineargradient.cc
// 9/14/2014 jichi
// See also: http://qt-project.org/forums/viewthread/25063
#include "qmlgradient/lineargradient.h"
#include <QtGui/QBrush>
#include <QtGui/QLinearGradient>
#include <QtGui/QPainter>

/** Private class */

class DeclarativeLinearGradientPrivate
{
public:
  bool visible;
  qreal opacity;
  QList<QColor> colors;
  QList<qreal> positions;
  QPointF startPoint;
  QPointF stopPoint;
  QBrush brush;
  bool brushDirty;

  DeclarativeLinearGradientPrivate() : visible(true), opacity(1.0), brushDirty(true) {}

  void invalidateBrush() { brushDirty = true; }
  bool updateBrush(int width, int height);
};

bool DeclarativeLinearGradientPrivate::updateBrush(int width, int height)
{
  if (width <= 0 || height <= 0 || colors.size() != positions.size())
    return false;

  qreal x1 = startPoint.x() * width,
        y1 = startPoint.y() * height,
        x2 = stopPoint.x() * width,
        y2 = stopPoint.y() * height;

  QLinearGradient grad(x1, y1, x2, y2);

  for (int i = 0; i < colors.size(); i++)
    grad.setColorAt(positions[i], colors[i]);

  brush = grad;
  brushDirty = false;
  return true;
}

/** Public class */

// Construction

DeclarativeLinearGradient::DeclarativeLinearGradient(QDeclarativeItem *parent)
  : Base(parent), d_(new D)
{
  connect(this, SIGNAL(heightChanged()), SLOT(refresh()));
  connect(this, SIGNAL(widthChanged()), SLOT(refresh()));

  setFlag(QGraphicsItem::ItemHasNoContents, false); // enable paint function
}

DeclarativeLinearGradient::~DeclarativeLinearGradient() { delete d_; }

// Properties

bool DeclarativeLinearGradient::isVisible() const { return d_->visible; }

QVariantList DeclarativeLinearGradient::colors() const
{
  QVariantList r;
  foreach (const QColor &it, d_->colors)
    r.append(it);
  return r;
}

QVariantList DeclarativeLinearGradient::positions() const
{
  QVariantList r;
  foreach (const QColor &it, d_->positions)
    r.append(it);
  return r;
}

qreal DeclarativeLinearGradient::opacity() const { return d_->opacity; }

QPointF DeclarativeLinearGradient::startPoint() const { return d_->startPoint; }
QPointF DeclarativeLinearGradient::stopPoint() const { return d_->stopPoint; }

void DeclarativeLinearGradient::setVisible(bool t)
{
  if (d_->visible != t) {
    d_->visible = t;
    if (d_->visible)
      update();
    emit visibleChanged();
  }
}

void DeclarativeLinearGradient::setOpacity(qreal v)
{
  if (qFuzzyCompare(d_->opacity, v))
    return;
  d_->opacity = v;
  if (d_->visible)
    update();
  emit opacityChanged();
}

void DeclarativeLinearGradient::setColors(const QVariantList &l)
{
  QList<QColor> v;
  foreach (const QVariant &it, l)
    v.append(it.value<QColor>());
  if (d_->colors != v) {
    d_->colors = v;
    d_->invalidateBrush();
    if (d_->visible)
      update();
    emit colorsChanged();
  }
}

void DeclarativeLinearGradient::setPositions(const QVariantList &l)
{
  QList<qreal> v;
  foreach (const QVariant &it, l)
    v.append(it.toReal());
  if (d_->positions != v) {
    d_->positions = v;
    d_->invalidateBrush();
    if (d_->visible)
      update();
    emit positionsChanged();
  }
}

void DeclarativeLinearGradient::setStartPoint(const QPointF &v)
{
  if (d_->startPoint != v) {
    d_->startPoint = v;
    d_->invalidateBrush();
    if (d_->visible)
      update();
    emit startPointChanged();
  }
}

void DeclarativeLinearGradient::setStopPoint(const QPointF &v)
{
  if (d_->stopPoint != v) {
    d_->stopPoint = v;
    d_->invalidateBrush();
    if (d_->visible)
      update();
    emit stopPointChanged();
  }
}

// Paint

void DeclarativeLinearGradient::refresh() { d_->invalidateBrush(); }

void DeclarativeLinearGradient::paint(QPainter *painter, const QStyleOptionGraphicsItem *option, QWidget *widget)
{
  Q_UNUSED(option);
  Q_UNUSED(widget);
  //painter->setRenderHints(QPainter::Antialiasing, true);
  if (d_->visible && (!d_->brushDirty || d_->updateBrush(width(), height()))) {
    painter->setOpacity(d_->opacity);
    painter->fillRect(boundingRect(), d_->brush);
  }
}

// EOF

#ifndef _QMLGRADIENT_LINEARGRADIENT_H
#define _QMLGRADIENT_LINEARGRADIENT_H

// lineargradient.h
// 9/14/2014 jichi
// See also: http://qt-project.org/forums/viewthread/25063

#include "sakurakit/skglobal.h"
#include <QtCore/QPointF>
#include <QtCore/QVariantList>
#include <QtDeclarative/QDeclarativeItem>

class DeclarativeLinearGradientPrivate;
class DeclarativeLinearGradient : public QDeclarativeItem
{
  Q_OBJECT
  SK_EXTEND_CLASS(DeclarativeLinearGradient, QDeclarativeItem)
  SK_DISABLE_COPY(DeclarativeLinearGradient)
  SK_DECLARE_PRIVATE(DeclarativeLinearGradientPrivate)
  Q_PROPERTY(bool visible READ isVisible WRITE setVisible NOTIFY visibleChanged)
  Q_PROPERTY(qreal opacity READ opacity WRITE setOpacity NOTIFY opacityChanged)
  Q_PROPERTY(QVariantList colors READ colors WRITE setColors NOTIFY colorsChanged)
  Q_PROPERTY(QVariantList positions READ positions WRITE setPositions NOTIFY positionsChanged)
  Q_PROPERTY(QPointF startPoint READ startPoint WRITE setStartPoint NOTIFY startPointChanged)
  Q_PROPERTY(QPointF stopPoint READ stopPoint WRITE setStopPoint NOTIFY stopPointChanged)
public:
  explicit DeclarativeLinearGradient(QDeclarativeItem *parent = nullptr);
  ~DeclarativeLinearGradient();

public:
  bool isVisible() const;
  qreal opacity() const;

  QVariantList colors() const;
  QVariantList positions() const;
  QPointF startPoint() const;
  QPointF stopPoint() const;

  void paint(QPainter *painter, const QStyleOptionGraphicsItem *option, QWidget *widget = nullptr) override;

public slots:
  void setVisible(bool visible);
  void setOpacity(qreal opacity);

  void setColors(const QVariantList &l);
  void setPositions(const QVariantList &l);
  void setStartPoint(const QPointF &pt);
  void setStopPoint(const QPointF &pt);

  void refresh();

signals:
  void visibleChanged();
  void opacityChanged();
  void colorsChanged();
  void positionsChanged();
  void startPointChanged();
  void stopPointChanged();
};

QML_DECLARE_TYPE(DeclarativeLinearGradient)

#endif // _QMLGRADIENT_LINEARGRADIENT_H

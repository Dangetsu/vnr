#ifndef _QTEFFECTS_GRAPHICSGLOWEFFECT2_H
#define _QTEFFECTS_GRAPHICSGLOWEFFECT2_H

// graphicsgloweffect.h
// 5/3/2012 jichi
// See: qt/src/gui/effects/qgraphicseffect.h

#include "qteffects/graphicsabstractblureffect_p.h"

QTEFFECTS_BEGIN_NAMESPACE

// Now: I assume the boundingrect of the second effect is within the first one
// The second will be painted before the first.
class GraphicsGlowEffect2: public GraphicsAbstractBlurEffect
{
  Q_OBJECT
  Q_PROPERTY(bool enabled2 READ isEnabled2 WRITE setEnabled2 NOTIFY enabled2Changed)
  Q_PROPERTY(QPointF offset2 READ offset2 WRITE setOffset2 NOTIFY offset2Changed)
  Q_PROPERTY(qreal xOffset2 READ xOffset2 WRITE setXOffset2 NOTIFY offset2Changed)
  Q_PROPERTY(qreal yOffset2 READ yOffset2 WRITE setYOffset2 NOTIFY offset2Changed)
  Q_PROPERTY(qreal blurRadius2 READ blurRadius2 WRITE setBlurRadius2 NOTIFY blurRadius2Changed)
  Q_PROPERTY(int blurIntensity2 READ blurIntensity2 WRITE setBlurIntensity2 NOTIFY blurIntensity2Changed)
  Q_PROPERTY(QColor color2 READ color2 WRITE setColor2 NOTIFY color2Changed)
  Q_DISABLE_COPY(GraphicsGlowEffect2)
  typedef GraphicsGlowEffect2 Self;
  typedef GraphicsAbstractBlurEffect Base;

public:
  explicit GraphicsGlowEffect2(QObject *parent = nullptr);
  ~GraphicsGlowEffect2();

  bool isEnabled2() const;

  QPointF offset2() const;
  qreal xOffset2() const { return offset2().x(); }
  qreal yOffset2() const { return offset2().y(); }

  int blurIntensity2() const;
  qreal blurRadius2() const;
  QColor color2() const;

public slots:
  void setEnabled2(bool t);

  void setOffset2(const QPointF &ofs);
  void setOffset2(qreal dx, qreal dy) { setOffset2(QPointF(dx, dy)); }
  void setOffset2(qreal d) { setOffset2(QPointF(d, d)); }

  void setXOffset2(qreal dx) { setOffset2(QPointF(dx, yOffset())); }
  void setYOffset2(qreal dy) { setOffset2(QPointF(xOffset(), dy)); }

  void setBlurIntensity2(int intensity);
  void setBlurRadius2(qreal radius);
  void setColor2(const QColor &color);

signals:
  void enabled2Changed(bool enabled);
  void offset2Changed(const QPointF &offset);
  void blurIntensity2Changed(int intensity);
  void blurRadius2Changed(qreal radius);
  void color2Changed(const QColor &color);
};

QTEFFECTS_END_NAMESPACE

#endif // _QTEFFECTS_GRAPHICSGLOWEFFECT2_H

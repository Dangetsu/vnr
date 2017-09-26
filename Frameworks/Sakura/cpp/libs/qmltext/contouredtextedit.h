#ifndef _QMLTEXT_CONTOURED_TEXTEDIT_H
#define _QMLTEXT_CONTOURED_TEXTEDIT_H

// contouredtext.h
// 4/5/2014 jichi

#include "sakurakit/skglobal.h"
#include <qt/src/declarative/graphicsitems/qdeclarativetextedit_p.h>
#include <QtCore/QPoint>

class DeclarativeContouredTextEditPrivate;
class DeclarativeContouredTextEdit : public QDeclarativeTextEdit
{
  Q_OBJECT
  SK_EXTEND_CLASS(DeclarativeContouredTextEdit, QDeclarativeTextEdit)
  SK_DISABLE_COPY(DeclarativeContouredTextEdit)
  SK_DECLARE_PRIVATE(DeclarativeContouredTextEditPrivate)
  Q_PROPERTY(bool contourEnabled READ isContourEnabled WRITE setContourEnabled NOTIFY contourEnabledChanged)
  Q_PROPERTY(QColor contourColor READ contourColor WRITE setContourColor NOTIFY contourColorChanged)
  Q_PROPERTY(int contourRadius READ contourRadius WRITE setContourRadius NOTIFY contourRadiusChanged)
  Q_PROPERTY(QPoint contourOffset READ contourOffset WRITE setContourOffset NOTIFY contourOffsetChanged)
  Q_PROPERTY(int contourXOffset READ contourXOffset WRITE setContourXOffset NOTIFY contourOffsetChanged)
  Q_PROPERTY(int contourYOffset READ contourYOffset WRITE setContourYOffset NOTIFY contourOffsetChanged)
public:
  explicit DeclarativeContouredTextEdit(QDeclarativeItem *parent = nullptr);
  ~DeclarativeContouredTextEdit();

signals:
  void linkActivated(const QString &link); // FIXME: How to import parent qml signals?

protected:
  void drawContents(QPainter *painter, const QRect &bounds) override;

public:
  bool isContourEnabled() const;

  QColor contourColor() const;
  int contourRadius() const;

  QPoint contourOffset() const;
  int contourXOffset() const { return contourOffset().x(); }
  int contourYOffset() const { return contourOffset().y(); }

public slots:
  void setContourEnabled(bool t);

  void setContourOffset(const QPoint &ofs);
  void setContourOffset(int dx, int dy) { setContourOffset(QPoint(dx, dy)); }
  void setContourOffset(int d) { setContourOffset(QPoint(d, d)); }

  void setContourXOffset(int dx) { setContourOffset(QPoint(dx, contourYOffset())); }
  void setContourYOffset(int dy) { setContourOffset(QPoint(contourXOffset(), dy)); }

  void setContourColor(const QColor &color);
  void setContourRadius(int radius);

signals:
  void contourEnabledChanged();
  void contourOffsetChanged();
  void contourRadiusChanged();
  void contourColorChanged();
};

QML_DECLARE_TYPE(DeclarativeContouredTextEdit)

#endif // _QMLTEXT_CONTOURED_TEXTEDIT_H

#ifndef MOUSESELECTOR_H
#define MOUSESELECTOR_H

// mouseselector.h
// 8/21/2014 jichi

#include <QtCore/QObject>
//#include <QtGui/qwindowdefs.h> // for WId
#include "sakurakit/skglobal.h"

QT_FORWARD_DECLARE_CLASS(QRubberBand)

class MouseSelectorPrivate;
class MouseSelector : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(MouseSelector)
  SK_EXTEND_CLASS(MouseSelector, QObject)
  SK_DECLARE_PRIVATE(MouseSelectorPrivate)
public:
  explicit MouseSelector(QObject *parent = nullptr);
  ~MouseSelector();

  //QWidget *parentWidget() const;
  //void setParentWidget(QWidget *parentWidget);

  QRubberBand *rubberBand() const;
  //void setRubberBand(QRubberBand *value);

  bool isEnabled() const; // default false
  void setEnabled(bool t);

  int comboKey() const; // windows VK, default 0
  void setComboKey(int vk);

  int refreshInterval() const;
  void setRefreshInterval(int value);

  bool isRefreshEnabled() const;
  void setRefreshEnabled(bool value);

public slots:
  void refresh();

signals:
  void pressed(int x, int y);
  void released(int x, int y);
  void selected(int x, int y, int width, int height);
};

#endif // MOUSESELECTOR_H

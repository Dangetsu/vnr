#ifndef QTHELPER_P_H
#define QTHELPER_P_H

// qthelper_p.h
// 12/9/2012 jichi

#include <QtCore/QObject>

class QtHelper : public QObject
{
  Q_OBJECT
  typedef QObject Base;
public:
  explicit QtHelper(QObject *parent=nullptr);

  /**
   *  @param  q
   */
  Q_INVOKABLE static void deleteObject(QObject *q);
};

#ifdef _MSC_VER
# pragma warning (disable:4189)   // C4189: local variable is initialized bot not referenced
#endif // _MSC_VER

#endif // QTTHELPER_P_H

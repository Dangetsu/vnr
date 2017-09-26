// qmlhelper_p.cc
// 12/9/2012 jichi

#include "qmlhelperplugin/qmlhelper_p.h"
#include "qtmeta/qtmeta.h"
#include "qtprivate/d/d_qdeclarativetextedit.h"
#include <qt/src/gui/text/qtextcontrol_p.h>

QmlHelper::QmlHelper(QObject *parent): Base(parent) {}

QObject *QmlHelper::textEdit_document(QDeclarativeItem *q)
{
  if (QtMeta::checkClassName(q, "QDeclarativeTextEdit"))
    return nullptr;
  return QtPrivate::d_qdeclarativetextedit_document(static_cast<const QDeclarativeTextEdit *>(q));
}

QString QmlHelper::textEdit_linkAtCursor(QDeclarativeItem *q)
{
  if (QtMeta::checkClassName(q, "QDeclarativeTextEdit"))
    if (QTextControl *control = QtPrivate::d_qdeclarativetextedit_control(static_cast<const QDeclarativeTextEdit *>(q)))
      return control->anchorAtCursor();
  return QString();
}

QString QmlHelper::textEdit_linkAt(QDeclarativeItem *q, qreal x, qreal y)
{
  if (QtMeta::checkClassName(q, "QDeclarativeTextEdit"))
    if (QTextControl *control = QtPrivate::d_qdeclarativetextedit_control(static_cast<const QDeclarativeTextEdit *>(q)))
      return control->anchorAt(QPointF(x, y));
  return QString();
}

// EOF

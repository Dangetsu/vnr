#ifndef QTMETA_H
#define QTMETA_H

// qtmeta.h
// 1/8/2015 jichi

#include <QtCore/QObject>

namespace QtMeta {

inline const char *getClassName(const QObject *q)
{ return q && q->metaObject() ? q->metaObject()->className() : nullptr; }

inline bool checkClassName(const QObject *q, const char *cls)
{ return q && q->metaObject() && qstrcmp(cls, q->metaObject()->className()); }

};

#endif // QTMETA_H

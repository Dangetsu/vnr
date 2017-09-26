#ifndef _QTEFFECTS_IMAGEFILTERS_H
#define _QTEFFECTS_IMAGEFILTERS_H

// imagefilters.h
// 6/14/2012 jichi

#include "qteffects/qteffects.h"
#include <QtGlobal>

QT_FORWARD_DECLARE_CLASS(QPainter)
QT_FORWARD_DECLARE_CLASS(QImage)

QTEFFECTS_BEGIN_NAMESPACE

// See: qt/src/gui/image/qpixmapfilter.cpp

void blurImage(QPainter *painter, QImage &blurImage, qreal radius, bool quality, bool alphaOnly, int transposed = 0);
void blurImage(QImage &blurImage, qreal radius, bool quality, int transposed = 0);

QTEFFECTS_END_NAMESPACE

#endif // _QTEFFECTS_IMAGEFILTERS_H

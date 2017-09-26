#ifndef _QTEFFECTS_IMAGEFILTERS_P_H
#define _QTEFFECTS_IMAGEFILTERS_P_H

// imagefilters_p.h
// 5/16/2012 jichi
// See: qt/src/gui/image/qpixmapfilter.cpp

#include "qteffects/imagefilters_q.h"
#include <QtCore/qmath.h>
//#include <qt/src/gui/painting/qmemrotate_p.h>

//QT_BEGIN_NAMESPACE
QTEFFECTS_BEGIN_NAMESPACE

// expblur(QImage &img, int radius)
//
// Based on exponential blur algorithm by Jani Huhtanen
//
// In-place blur of image 'img' with kernel
// of approximate radius 'radius'.
//
// Blurs with two sided exponential impulse
// response.
//
// aprec = precision of alpha parameter
// in fixed-point format 0.aprec
//
// zprec = precision of state parameters
// zR,zG,zB and zA in fp format 8.zprec
template <int aprec, int zprec, bool alphaOnly>
inline void expblur(QImage &img, qreal radius, bool improvedQuality = false, int transposed = 0)
{
  // halve the radius if we're using two passes
  if (improvedQuality)
    radius *= 0.5;

  Q_ASSERT(img.format() == QImage::Format_ARGB32_Premultiplied
        || img.format() == QImage::Format_RGB32
        || img.format() == QImage::Format_Indexed8);

  // choose the alpha such that pixels at radius distance from a fully
  // saturated pixel will have an alpha component of no greater than
  // the cutOffIntensity
  const qreal cutOffIntensity = 2; // jichi: when increased, shadow will be vertically larger
  int alpha = radius <= qreal(1e-5) ?
        ((1 << aprec)-1) :
        qRound((1<<aprec)*(1 - qPow(cutOffIntensity * (1 / qreal(255)), 1 / radius)));

  int img_height = img.height();
  for (int row = 0; row < img_height; row++)
    for (int i = 0; i <= int(improvedQuality); i++)
      qt_blurrow<aprec, zprec, alphaOnly>(img, row, alpha);

  QImage temp(img.height(), img.width(), img.format());

  Q_UNUSED(transposed)
  /* jichi: memrotate is unimplemented
  if (transposed >= 0) {
    if (img.depth() == 8) {
      qt_memrotate270(reinterpret_cast<const quint8*>(img.bits()),
              img.width(), img.height(), img.bytesPerLine(),
              reinterpret_cast<quint8*>(temp.bits()),
              temp.bytesPerLine());
    } else {
      qt_memrotate270(reinterpret_cast<const quint32*>(img.bits()),
              img.width(), img.height(), img.bytesPerLine(),
              reinterpret_cast<quint32*>(temp.bits()),
              temp.bytesPerLine());
    }
  } else {
    if (img.depth() == 8) {
      qt_memrotate90(reinterpret_cast<const quint8*>(img.bits()),
               img.width(), img.height(), img.bytesPerLine(),
               reinterpret_cast<quint8*>(temp.bits()),
               temp.bytesPerLine());
    } else {
      qt_memrotate90(reinterpret_cast<const quint32*>(img.bits()),
               img.width(), img.height(), img.bytesPerLine(),
               reinterpret_cast<quint32*>(temp.bits()),
               temp.bytesPerLine());
    }
  }
  */

  img_height = temp.height();
  for (int row = 0; row < img_height; row++)
    for (int i = 0; i <= int(improvedQuality); i++)
      qt_blurrow<aprec, zprec, alphaOnly>(temp, row, alpha);

  /* jichi: memrotate is unimplemented
  if (transposed == 0) {
    if (img.depth() == 8) {
      qt_memrotate90(reinterpret_cast<const quint8*>(temp.bits()),
               temp.width(), temp.height(), temp.bytesPerLine(),
               reinterpret_cast<quint8*>(img.bits()),
               img.bytesPerLine());
    } else {
      qt_memrotate90(reinterpret_cast<const quint32*>(temp.bits()),
               temp.width(), temp.height(), temp.bytesPerLine(),
               reinterpret_cast<quint32*>(img.bits()),
               img.bytesPerLine());
    }
  } else {
    img = temp;
  }
  */
}

QTEFFECTS_END_NAMESPACE
//QT_END_NAMESPACE

#endif // _QTEFFECTS_IMAGEFILTERS_P_H

#ifndef _QTIMAGE_CONTOUR_H
#define _QTIMAGE_CONTOUR_H

// contour.h
// 4/5/2014 jichi

#include <QtGui/QImage>

namespace QtImage {

inline bool isPremultipliedImageFormat(QImage::Format fmt)
{
  switch (fmt) {
  case QImage::Format_ARGB32_Premultiplied:
  case QImage::Format_ARGB8565_Premultiplied:
  case QImage::Format_ARGB6666_Premultiplied:
  case QImage::Format_ARGB8555_Premultiplied:
  case QImage::Format_ARGB4444_Premultiplied:
    return true;
  default:
    return false;
  }
}

QImage contourImage(const QImage &src, const QColor &color, int radius, const QPoint &offset,
                    bool easingAlpha = true, int alphaThreshold = 255);

} // namespae QtImage

#endif // _QTIMAGE_CONTOUR_H

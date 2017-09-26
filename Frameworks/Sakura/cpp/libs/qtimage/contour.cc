// contour.cc
// 4/5/2014 jichi
#include "qtimage/contour.h"
#include <QtGui/QColor>

QImage QtImage::contourImage(const QImage &src, const QColor &color, int radius, const QPoint &offset,
                               bool easingAlpha, int alphaThreshold)
{
  bool premultiplied  = isPremultipliedImageFormat(src.format());
  int offsetX = offset.x(),
      offsetY = offset.x();
  QRgb fill = color.rgb();
  int width = src.width(),
      height = src.height();
  int radius2 = radius * radius;
  // Step 1: Found contour points
  // Step 2: Paint out side of contour according to distance
  QImage ret(width, height, src.format());
  for (int x = 0; x < src.width(); x++)
    for (int y = 0; y < src.height(); y++)
      if (qAlpha(src.pixel(x, y)) >= alphaThreshold) {
        //contourPixel();
        for (int i = -radius; i <= radius; i++)
          for (int j = -radius; j <= radius; j++) {
            int dx = i + offsetX,
                dy = j + offsetY;
            int dist2 = dx * dx+ dy * dy;
            if (dist2 <= radius2) {
              int xx = x + dx,
                  yy = y + dy;
              if (xx >= 0 && yy >= 0 && xx < width && yy < height &&
                  qAlpha(src.pixel(xx, yy)) < alphaThreshold) {
                if (!easingAlpha)
                  ret.setPixel(xx, yy, fill);
                else {
                  QRgb alpha = 255 * (radius2 - dist2) / radius2;
                  //if (qAlpha(fill) != 255)
                  //  alpha -= 255 - qAlpha(fill);
                  //alpha -= 255 - alphaThreshold;

                  //qreal dist = qSqrt(dist2);
                  //QRgb alpha = 255 * (radius - dist) / radius;
                  QRgb oldpixel = ret.pixel(xx, yy);
                  if (oldpixel)
                    alpha = qMax<uint>(alpha, qAlpha(oldpixel));
                  //double dist = qSqrt(dist2);
                  //QRgb alpha = 255 * (radius - dist) / radius;
                  QRgb pixel;
                  if (premultiplied)
                    pixel = qRgba(
                        qRed(fill) * alpha/255,
                        qGreen(fill) * alpha/255,
                        qBlue(fill) * alpha/255,
                        alpha);
                  else
                    pixel = (fill & 0xffffff) | (alpha << 24);
                    //QRgb pixel = qRgba(qRed(fill), qGreen(fill), qBlue(fill), alpha);
                  ret.setPixel(xx, yy, pixel);
                }
              }
            }
          }
      }
  return ret;
}

// EOF

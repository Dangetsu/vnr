// imagefilters.cc
// 6/14/2012 jichi
#include "qteffects/imagefilters.h"
#include "qteffects/imagefilters_p.h"
#include <QtGui/QPainter>

QTEFFECTS_BEGIN_NAMESPACE

// Alpha precsion & z precision, must be assigned at compile-time to specialize template
//enum { blurImage_aprec = 12, blurImage_zprec = 10 }; // defaults
enum { blurImage_aprec = 8, blurImage_zprec = 4 }; // essential, decide how text shadow effect is rendered

void blurImage(QImage &blurImage, qreal radius, bool quality, int transposed)
{
  qt_blurImage(blurImage, radius, quality, transposed);

  bool alphaOnly = blurImage.format() == QImage::Format_Indexed8;
  if (alphaOnly)
    expblur<blurImage_aprec, blurImage_zprec, true>(blurImage, radius, quality, transposed);
  else
    expblur<blurImage_aprec, blurImage_zprec, false>(blurImage, radius, quality, transposed);
}

void blurImage(QPainter *painter, QImage &blurImage, qreal radius, bool quality, bool alphaOnly, int transposed)
{
  //qt_blurImage(p, blurImage, radius, quality, alphaOnly, transposed);
  if (blurImage.format() != QImage::Format_ARGB32_Premultiplied &&
      blurImage.format() != QImage::Format_RGB32)
    blurImage = blurImage.convertToFormat(QImage::Format_ARGB32_Premultiplied);

  qreal scale = 1;
  if (radius >= 4 && blurImage.width() >= 2 && blurImage.height() >= 2) {
    blurImage = qt_halfScaled(blurImage);
    scale = 2;
    radius *= qreal(0.5);
  }

  if (alphaOnly)
    expblur<blurImage_aprec, blurImage_zprec, true>(blurImage, radius, quality, transposed);
  else
    expblur<blurImage_aprec, blurImage_zprec, false>(blurImage, radius, quality, transposed);

  if (painter) {
    painter->scale(scale, scale);
    painter->setRenderHint(QPainter::SmoothPixmapTransform);
    painter->drawImage(QRect(0, 0, blurImage.width(), blurImage.height()), blurImage);
  }
}

QTEFFECTS_END_NAMESPACE

// EOF

/*
template <int shift>
inline int qt_static_shift(int value)
{
  if (shift == 0)
    return value;
  else if (shift > 0)
    return value << (uint(shift) & 0x1f);
  else
    return value >> (uint(-shift) & 0x1f);
}

template<int aprec, int zprec>
inline void qt_blurinner(uchar *bptr, int &zR, int &zG, int &zB, int &zA, int alpha)
{
  QRgb *pixel = (QRgb *)bptr;

#define Z_MASK (0xff << zprec)
  const int A_zprec = qt_static_shift<zprec - 24>(*pixel) & Z_MASK;
  const int R_zprec = qt_static_shift<zprec - 16>(*pixel) & Z_MASK;
  const int G_zprec = qt_static_shift<zprec - 8>(*pixel)  & Z_MASK;
  const int B_zprec = qt_static_shift<zprec>(*pixel)    & Z_MASK;
#undef Z_MASK

  const int zR_zprec = zR >> aprec;
  const int zG_zprec = zG >> aprec;
  const int zB_zprec = zB >> aprec;
  const int zA_zprec = zA >> aprec;

  zR += alpha * (R_zprec - zR_zprec);
  zG += alpha * (G_zprec - zG_zprec);
  zB += alpha * (B_zprec - zB_zprec);
  zA += alpha * (A_zprec - zA_zprec);

#define ZA_MASK (0xff << (zprec + aprec))
  *pixel =
    qt_static_shift<24 - zprec - aprec>(zA & ZA_MASK)
    | qt_static_shift<16 - zprec - aprec>(zR & ZA_MASK)
    | qt_static_shift<8 - zprec - aprec>(zG & ZA_MASK)
    | qt_static_shift<-zprec - aprec>(zB & ZA_MASK);
#undef ZA_MASK
}

const int alphaIndex = (QSysInfo::ByteOrder == QSysInfo::BigEndian ? 0 : 3);

template<int aprec, int zprec>
inline void qt_blurinner_alphaOnly(uchar *bptr, int &z, int alpha)
{
  const int A_zprec = int(*(bptr)) << zprec;
  const int z_zprec = z >> aprec;
  z += alpha * (A_zprec - z_zprec);
  *(bptr) = z >> (zprec + aprec);
}

template<int aprec, int zprec, bool alphaOnly>
inline void qt_blurrow(QImage & im, int line, int alpha)
{
  uchar *bptr = im.scanLine(line);

  int zR = 0, zG = 0, zB = 0, zA = 0;

  if (alphaOnly && im.format() != QImage::Format_Indexed8)
    bptr += alphaIndex;

  const int stride = im.depth() >> 3;
  const int im_width = im.width();
  for (int index = 0; index < im_width; ++index) {
    if (alphaOnly)
      qt_blurinner_alphaOnly<aprec, zprec>(bptr, zA, alpha);
    else
      qt_blurinner<aprec, zprec>(bptr, zR, zG, zB, zA, alpha);
    bptr += stride;
  }

  bptr -= stride;

  for (int index = im_width - 2; index >= 0; --index) {
    bptr -= stride;
    if (alphaOnly)
      qt_blurinner_alphaOnly<aprec, zprec>(bptr, zA, alpha);
    else
      qt_blurinner<aprec, zprec>(bptr, zR, zG, zB, zA, alpha);
  }
}

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
void expblur(QImage &img, qreal radius, bool improvedQuality = false, int transposed = 0)
{
  // halve the radius if we're using two passes
  if (improvedQuality)
    radius *= qreal(0.5);

  Q_ASSERT(img.format() == QImage::Format_ARGB32_Premultiplied
       || img.format() == QImage::Format_RGB32
       || img.format() == QImage::Format_Indexed8);

  // choose the alpha such that pixels at radius distance from a fully
  // saturated pixel will have an alpha component of no greater than
  // the cutOffIntensity
  const qreal cutOffIntensity = 2;
  int alpha = radius <= qreal(1e-5)
    ? ((1 << aprec)-1)
    : qRound((1<<aprec)*(1 - qPow(cutOffIntensity * (1 / qreal(255)), 1 / radius)));

  int img_height = img.height();
  for (int row = 0; row < img_height; ++row) {
    for (int i = 0; i <= int(improvedQuality); ++i)
      qt_blurrow<aprec, zprec, alphaOnly>(img, row, alpha);
  }

  QImage temp(img.height(), img.width(), img.format());
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

  img_height = temp.height();
  for (int row = 0; row < img_height; ++row) {
    for (int i = 0; i <= int(improvedQuality); ++i)
      qt_blurrow<aprec, zprec, alphaOnly>(temp, row, alpha);
  }

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
}
#define AVG(a,b)  ( ((((a)^(b)) & 0xfefefefeUL) >> 1) + ((a)&(b)) )
#define AVG16(a,b)  ( ((((a)^(b)) & 0xf7deUL) >> 1) + ((a)&(b)) )

Q_GUI_EXPORT QImage qt_halfScaled(const QImage &source)
{
  if (source.width() < 2 || source.height() < 2)
    return QImage();

  QImage srcImage = source;

  if (source.format() == QImage::Format_Indexed8) {
    // assumes grayscale
    QImage dest(source.width() / 2, source.height() / 2, srcImage.format());

    const uchar *src = reinterpret_cast<const uchar*>(const_cast<const QImage &>(srcImage).bits());
    int sx = srcImage.bytesPerLine();
    int sx2 = sx << 1;

    uchar *dst = reinterpret_cast<uchar*>(dest.bits());
    int dx = dest.bytesPerLine();
    int ww = dest.width();
    int hh = dest.height();

    for (int y = hh; y; --y, dst += dx, src += sx2) {
      const uchar *p1 = src;
      const uchar *p2 = src + sx;
      uchar *q = dst;
      for (int x = ww; x; --x, ++q, p1 += 2, p2 += 2)
        *q = ((int(p1[0]) + int(p1[1]) + int(p2[0]) + int(p2[1])) + 2) >> 2;
    }

    return dest;
  } else if (source.format() == QImage::Format_ARGB8565_Premultiplied) {
    QImage dest(source.width() / 2, source.height() / 2, srcImage.format());

    const uchar *src = reinterpret_cast<const uchar*>(const_cast<const QImage &>(srcImage).bits());
    int sx = srcImage.bytesPerLine();
    int sx2 = sx << 1;

    uchar *dst = reinterpret_cast<uchar*>(dest.bits());
    int dx = dest.bytesPerLine();
    int ww = dest.width();
    int hh = dest.height();

    for (int y = hh; y; --y, dst += dx, src += sx2) {
      const uchar *p1 = src;
      const uchar *p2 = src + sx;
      uchar *q = dst;
      for (int x = ww; x; --x, q += 3, p1 += 6, p2 += 6) {
        // alpha
        q[0] = AVG(AVG(p1[0], p1[3]), AVG(p2[0], p2[3]));
        // rgb
        const quint16 p16_1 = (p1[2] << 8) | p1[1];
        const quint16 p16_2 = (p1[5] << 8) | p1[4];
        const quint16 p16_3 = (p2[2] << 8) | p2[1];
        const quint16 p16_4 = (p2[5] << 8) | p2[4];
        const quint16 result = AVG16(AVG16(p16_1, p16_2), AVG16(p16_3, p16_4));
        q[1] = result & 0xff;
        q[2] = result >> 8;
      }
    }

    return dest;
  } else if (source.format() != QImage::Format_ARGB32_Premultiplied
         && source.format() != QImage::Format_RGB32)
  {
    srcImage = source.convertToFormat(QImage::Format_ARGB32_Premultiplied);
  }

  QImage dest(source.width() / 2, source.height() / 2, srcImage.format());

  const quint32 *src = reinterpret_cast<const quint32*>(const_cast<const QImage &>(srcImage).bits());
  int sx = srcImage.bytesPerLine() >> 2;
  int sx2 = sx << 1;

  quint32 *dst = reinterpret_cast<quint32*>(dest.bits());
  int dx = dest.bytesPerLine() >> 2;
  int ww = dest.width();
  int hh = dest.height();

  for (int y = hh; y; --y, dst += dx, src += sx2) {
    const quint32 *p1 = src;
    const quint32 *p2 = src + sx;
    quint32 *q = dst;
    for (int x = ww; x; --x, q++, p1 += 2, p2 += 2)
      *q = AVG(AVG(p1[0], p1[1]), AVG(p2[0], p2[1]));
  }

  return dest;
}

Q_GUI_EXPORT void qt_blurImage(QPainter *p, QImage &blurImage, qreal radius, bool quality, bool alphaOnly, int transposed = 0)
{
  if (blurImage.format() != QImage::Format_ARGB32_Premultiplied
    && blurImage.format() != QImage::Format_RGB32)
  {
    blurImage = blurImage.convertToFormat(QImage::Format_ARGB32_Premultiplied);
  }

  qreal scale = 1;
  if (radius >= 4 && blurImage.width() >= 2 && blurImage.height() >= 2) {
    blurImage = qt_halfScaled(blurImage);
    scale = 2;
    radius *= qreal(0.5);
  }

  if (alphaOnly)
    expblur<12, 10, true>(blurImage, radius, quality, transposed);
  else
    expblur<12, 10, false>(blurImage, radius, quality, transposed);

  if (p) {
    p->scale(scale, scale);
    p->setRenderHint(QPainter::SmoothPixmapTransform);
    p->drawImage(QRect(0, 0, blurImage.width(), blurImage.height()), blurImage);
  }
}

Q_GUI_EXPORT void qt_blurImage(QImage &blurImage, qreal radius, bool quality, int transposed = 0)
{
  if (blurImage.format() == QImage::Format_Indexed8)
    expblur<12, 10, true>(blurImage, radius, quality, transposed);
  else
    expblur<12, 10, false>(blurImage, radius, quality, transposed);
}

Q_GUI_EXPORT bool qt_scaleForTransform(const QTransform &transform, qreal *scale);

// grayscales the image to dest (could be same). If rect isn't defined
// destination image size is used to determine the dimension of grayscaling
// process.
static void grayscale(const QImage &image, QImage &dest, const QRect& rect = QRect())
{
  QRect destRect = rect;
  QRect srcRect = rect;
  if (rect.isNull()) {
    srcRect = dest.rect();
    destRect = dest.rect();
  }
  if (&image != &dest) {
    destRect.moveTo(QPoint(0, 0));
  }

  unsigned int *data = (unsigned int *)image.bits();
  unsigned int *outData = (unsigned int *)dest.bits();

  if (dest.size() == image.size() && image.rect() == srcRect) {
    // a bit faster loop for grayscaling everything
    int pixels = dest.width() * dest.height();
    for (int i = 0; i < pixels; ++i) {
      int val = qGray(data[i]);
      outData[i] = qRgba(val, val, val, qAlpha(data[i]));
    }
  } else {
    int yd = destRect.top();
    for (int y = srcRect.top(); y <= srcRect.bottom() && y < image.height(); y++) {
      data = (unsigned int*)image.scanLine(y);
      outData = (unsigned int*)dest.scanLine(yd++);
      int xd = destRect.left();
      for (int x = srcRect.left(); x <= srcRect.right() && x < image.width(); x++) {
        int val = qGray(data[x]);
        outData[xd++] = qRgba(val, val, val, qAlpha(data[x]));
      }
    }
  }
}

*/

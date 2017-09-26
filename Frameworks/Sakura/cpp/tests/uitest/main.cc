// main.cc
// 4/5/2014 jichi
//
// See: Qt source code
// - src/gui/widgets/qtextedit.cpp
// - src/gui/widgets/qtextedit.h
// - src/gui/widgets/qtextedit_p.h
// - src/declarative/graphicsitems/qdeclarativetextedit.cpp
// - src/declarative/graphicsitems/qdeclarativetextedit_p.h
// - src/declarative/graphicsitems/qdeclarativetextedit_p_p.h

#include "main.h"
#include <qt/src/gui/text/qtextdocumentlayout_p.h>
#include <qt/src/gui/widgets/qtextedit_p.h>
#include <QDebug>

// Anti alias
// https://en.wikipedia.org/wiki/Spatial_anti-aliasing
// http://cs.brown.edu/courses/cs123/lectures/06_Image_Processing_II.pdf

// Outline text
// Other methods: http://www.codeproject.com/Articles/42529/Outline-Text

void maskImage(QImage &src, int alphaThreshold = 255)
{
  for (int x = 0; x < src.width(); x++)
    for (int y = 0; y < src.height(); y++)
      if (qAlpha(src.pixel(x, y)) < alphaThreshold)
        src.setPixel(x, y, 0);
}

QImage contourImage(const QImage &src, const QColor &color, int radius = 8, int offsetX = 2, int offsetY = 2, int alphaThreshold = 255)
{
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
                QRgb alpha = 255 * (radius2 - dist2) / radius2;
                //qreal dist = qSqrt(dist2);
                //QRgb alpha = 255 * (radius - dist) / radius;
                QRgb oldpixel = ret.pixel(xx, yy);
                if (oldpixel)
                  alpha = qMax<uint>(alpha, qAlpha(oldpixel));
                //double dist = qSqrt(dist2);
                //QRgb alpha = 255 * (radius - dist) / radius;
                //QRgb pixel = qRgba(qRed(fill), qGreen(fill), qBlue(fill), alpha);
                QRgb pixel = (fill & 0xffffff) | (alpha << 24);
                ret.setPixel(xx, yy, pixel);
              }
            }
          }
      }
  return ret;
}

QImage shadowImage(const QImage &src, const QColor &color, int radius = 8, int offsetX = 2, int offsetY = 2, int alphaThreshold = 255)
{
  QRgb fill = color.rgb();
  int width = src.width(),
      height = src.height();
  //int radius2 = radius * radius;
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
            int xx = x + dx,
                yy = y + dy;
            if (xx >= 0 && yy >= 0 && xx < width && yy < height &&
                qAlpha(src.pixel(xx, yy)) < alphaThreshold)
              ret.setPixel(xx, yy, fill);
          }
      }
  return ret;
}

void mergeImage(QImage &target, const QImage &src)
{
  for (int x = 0; x < qMin(target.width(), src.width()); x++)
    for (int y = 0; y < qMin(target.height(), src.height()); y++)
      if (QRgb pixel = src.pixel(x, y))
        target.setPixel(x, y, pixel);
}

void TextEdit::paintEvent(QPaintEvent *e)
{
  //Base::paintEvent(e);
  QTextEditPrivate *d = static_cast<QTextEditPrivate *>(d_ptr.data());
  //qDebug() << "paintEvent: pass";

  QPainter painter(d->viewport);
  QPainter *p = &painter;
  //d->paint(&p, e);
  const int xOffset = d->horizontalOffset();
  const int yOffset = d->verticalOffset();

  QRect r = e->rect();
  p->translate(-xOffset, -yOffset);
  r.translate(xOffset, yOffset);

  //QImage img(p->device()->width(), p->device()->height(), QImage::Format_ARGB32_Premultiplied);
  QImage img(p->device()->width(), p->device()->height(), QImage::Format_ARGB32);
  img.fill(0);
  QPainter imgPainter(&img);
  d->control->document()->drawContents(&imgPainter, r);
  imgPainter.end();

  //maskImage(img, 255);

  // QImage contourImage(const QImage &src, const QColor &color, int radius = 8, int offsetX = 2, int offsetY = 2, int alphaThreshold = 255)
  QImage img2 = contourImage(img, Qt::green, 8, 2, 2, 255);

  //mergeImage(img, img2);
  //QImage img3 = shadowImage(img, Qt::black, 1, 1, 1, 128);
  //mergeImage(img2, img3);

  p->drawImage(0, 0, img2);

  d->control->drawContents(p, r, this);
}

int main(int argc, char *argv[])
{
  QApplication a(argc, argv);

  auto w = new TextEdit;

  enum { transp = 1 };

  if (transp) {
    w->setAttribute(Qt::WA_TranslucentBackground);
    w->setStyleSheet("background-color:transparent");
    w->setWindowFlags(Qt::FramelessWindowHint);
  }

  auto font = w->font();
  font.setPointSize(24);
  font.setBold(true);
  w->setFont(font);

  //auto h = "<span style='color:white'>a very long text</span>";
  //auto h = "a very long text";
  //auto h = "aaaa"
  //    "<table>"
  //      "<tr><td>hello</td><td>what</td></tr>"
  //      "<tr>"
  //          "<td>outer1</td>"
  //          "<td><table><tr><td>inner1</td></tr><tr><td>inner2</td></tr></table></td>"
  //          "<td>outer2afwaefae</td>"
  //      "</tr>"
  //    "</table>"
  //    "bbbb";
  //auto h = "<table width=100% border=1>"
  //  "<tr><td width=33%>2</td><td width=34%>2</td><td width=33% ><div style='float:left;display:inline-block;width:50%;text-align:right;'>3</div><div style='float:left;display:inline-block;width:50%;text-align: left;'>.6</div></td></tr>"
  //  "</table>";
  //auto h = "Yomi<sup>reading</sup>";
  auto h = "<sub>Name</sub><sup>ruby</sup>";
  w->setHtml(h);
  //w->setTextBackgroundColor(Qt::black);

  w->resize(400, 300);
  w->show();
  return a.exec();
}

// EOF
//static QGraphicsEffect *createEffect()
//{
//  auto e = new GraphicsGlowEffect;
//  e->setColor(Qt::blue);
//  e->setOffset(1, 1);
//  e->setBlurRadius(8);;
//  e->setBlurIntensity(1);
//  e->setEnabled(true);
//  return e;
//}

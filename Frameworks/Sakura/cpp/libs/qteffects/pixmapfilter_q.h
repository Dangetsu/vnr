#ifndef _QTEFFECTS_PIXMAPFILTER_Q_H
#define _QTEFFECTS_PIXMAPFILTER_Q_H

// pixmapfilter_q.h
// 5/3/2012 jichi
// See: gui/image/pixmapfilter_p.cpp

#include <qt/src/gui/painting/qpaintengineex_p.h>

QT_BEGIN_NAMESPACE

// Must be consistent with qpixmapfilter.cpp
class QPixmapFilterPrivate : public QObjectPrivate
{
  Q_DECLARE_PUBLIC(QPixmapFilter)
public:
  QPixmapFilter::FilterType type;
};

QT_END_NAMESPACE

#endif // _QTEFFECTS_PIXMAPFILTER_Q_H

#ifndef PYMSIME_P_H
#define PYMSIME_P_H

// pymsime_p.h
// 1/4/2015 jichi

#include <QtCore/QString>

class ime_applier
{
  QString *d_;
public:
  explicit ime_applier(QString *d) : d_(d) { Q_ASSERT(d_); }
  void operator()(const wchar_t *ws, size_t len)
  { d_->append(QString::fromWCharArray(ws, len)); }
};

class ime_collector
{
  typedef QList<QPair<QString, QString> > D;
  D *d_;
public:
  explicit ime_collector(D *d) : d_(d) { Q_ASSERT(d_); }
  void operator()(const wchar_t *sx, size_t nx, const wchar_t *sy, size_t ny)
  {
    d_->append(qMakePair(QString::fromWCharArray(sx, nx),
                         QString::fromWCharArray(sy, ny)));
  }
};

#endif // PYMSIME_P_H

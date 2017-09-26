#ifndef MAIN_H
#define MAIN_H

// main.h
// 10/12/2014 jichi
#include <QtCore>


class TestThread : public QThread
{
  Q_OBJECT
protected:
  void run() override;
};

#endif // MAIN_H

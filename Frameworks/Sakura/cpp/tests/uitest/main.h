#ifndef MAIN_H
#define MAIN_H

// main.h
// 4/5/2014 jichi

#include <QtGui>

//class TextEdit : public QTextBrowser
class TextEdit : public QTextEdit
{
  Q_OBJECT
  typedef QTextEdit Base;
public:
  TextEdit() {}
protected:
  void paintEvent(QPaintEvent *e) override;
};

#endif // MAIN_H

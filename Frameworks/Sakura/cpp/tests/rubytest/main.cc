// main.cc
// 6/25/2015 jichi
//
// Measure text width in Qt
// http://doc.qt.io/qt-4.8/qfontmetrics.html
// http://stackoverflow.com/questions/1337523/measuring-text-width-in-qt
#include "qtrichruby/richrubyparser.h"
#include <QtGui>

int main(int argc, char *argv[])
{
  QApplication a(argc, argv);

  RichRubyParser p;

  auto w = new QTextEdit;
  w->setWordWrapMode(QTextOption::WordWrap);

  //QString h = "awf    abhe<u>[ruby=hello]world[/ruby]</u> <u>hellafawewafe</u> awef";
  QString h = "yes <u>[ruby=hello]world[/ruby]</u> and";
  w->resize(200, 300);
  int contentWidth = w->contentsRect().width();
  QFont rbFont = w->font(),
        rtFont = w->font();
  rbFont.setBold(true);
  rtFont.setUnderline(true);
  qDebug() << p.createRuby("rb", "rt");
  qDebug() << "no ruby:" << p.removeRuby(h);
  qDebug() << "plain text:" << p.renderToPlainText(h);
  h = p.renderToHtmlTable(h, contentWidth, rbFont, rtFont);
  //h.prepend(
  //  "<style type='text/css'>"
  //  ".rt { text-decoration: underline; }"
  //  "</style>"
  //);
  qDebug() << h;
  w->setHtml(h);
  w->show();
  return a.exec();
}

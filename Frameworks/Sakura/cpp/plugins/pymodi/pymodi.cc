// pymodi.cc
// 8/13/2014

#include "pymodi/pymodi.h"
#include "modiocr/modiocr.h"
//#include <QtCore/QMutex>
//#include <QtCore/QMutexLocker>

//static QMutex _mutex; // MODI OCR would crash if invoked simutaneously

bool ModiReader::isValid()
{ return ::modiocr_available(); }

QString ModiReader::readText(const QString &path, int language)
{
  //QMutexLocker sync(&::_mutex);
  QString ret;
  ::modiocr_readfile((const wchar_t *)path.utf16(), language,
    [&ret](const wchar_t *text) {
      ret.append(QString::fromWCharArray(text));
    }
  );
  return ret;
}

QStringList ModiReader::readTextList(const QString &path, int language)
{
  //QMutexLocker sync(&::_mutex);
  QStringList ret;
  ::modiocr_readfile((const wchar_t *)path.utf16(), language,
    [&ret](const wchar_t *text) {
      ret.append(QString::fromWCharArray(text));
    }
  );
  return ret;
}

// EOF

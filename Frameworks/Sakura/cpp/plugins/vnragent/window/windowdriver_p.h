#pragma once

// windowdriver_p.h
// 2/1/2013 jichi

#include "sakurakit/skglobal.h"
#include <QtCore/QObject>
#include <qt_windows.h>

QT_FORWARD_DECLARE_CLASS(QTimer)

class WindowManager;
class WindowDriverPrivate : public QObject
{
  Q_OBJECT
  Q_DISABLE_COPY(WindowDriverPrivate)
  SK_EXTEND_CLASS(WindowDriverPrivate, QObject)
  //SK_DECLARE_PUBLIC(WindowDriver)

  enum { RefreshInterval = 500 }; // interval checking if new window is created
  QTimer *refreshTimer;

public:
  WindowManager *manager;

  bool enabled,
       textVisible,
       translationEnabled;

public:
  static Self *instance();
  explicit WindowDriverPrivate(QObject *parent=nullptr);
  ~WindowDriverPrivate();

  void requestUpdateContextMenu(HMENU hMenu, HWND hWnd) // queued
  { emit updateContextMenuRequested(hMenu, hWnd); }

signals:
  void updateContextMenuRequested(void *hMenu, void *hWnd);
private slots:
  // Needed as HWMD and HMENU are not registered by Qt
  void onUpdateContextMenuRequested(void *hMenu, void *hWnd)
  { updateContextMenu((HMENU)hMenu, (HWND)hWnd); }

  void refresh() { updateProcessWindows(); }

private:
  void updateAbstractWindow(HWND hWnd); // The type of the window is unknown

  bool updateStandardWindow(HWND hWnd, LPWSTR buffer, int bufferSize); // window, return whether the window is changed
  void updateContextMenu(HMENU hMenu, HWND hWnd);
  bool updateListView(HWND hWnd, LPWSTR buffer, int bufferSize); // SysListView
  bool updateTabControl(HWND hWnd, LPWSTR buffer, int bufferSize); // SysTabControl
  bool updateMenu(HMENU hMenu, HWND hWnd, LPWSTR buffer, int bufferSize); // MenuItem
  bool updateTabView();

  QString transformText(const QString &text, qint64 hash) const;

  static void repaintWindow(HWND hWnd);
  static void repaintMenuBar(HWND hWnd);

  static void updateProcessWindows(DWORD processId = 0);
  static void updateThreadWindows(DWORD threadId = 0);

  //static QString joinTextTranslation(const QString &text, const QString &tr)
  //{ return text + "<" + tr; }
};

// EOF

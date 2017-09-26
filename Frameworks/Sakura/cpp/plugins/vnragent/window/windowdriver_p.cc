// windowdriver_p.cc
// 2/1/2013 jichi

#include "config.h"
#include "window/windowdriver_p.h"
#include "window/windowhash.h"
#include "window/windowmanager.h"
#include "winiter/winiter.h"
#include "winiter/winitertl.h"
#include <commctrl.h>
#include <QtCore/QHash>
#include <QtCore/QTextCodec>
#include <QtCore/QTimer>
#include <unordered_map>
//#include <boost/bind.hpp>

//#define DEBUG "windowdriver_p"
//#include "sakurakit/skdebug.h"

enum { TEXT_BUFFER_SIZE = 256 };

// - Construction -

static WindowDriverPrivate *instance_;
WindowDriverPrivate *WindowDriverPrivate::instance() { return instance_; }

WindowDriverPrivate::WindowDriverPrivate(QObject *parent)
  : Base(parent)
  , enabled(false)
  , textVisible(false)
  , translationEnabled(false)
{
  manager = new WindowManager(this);

  refreshTimer = new QTimer(this);
  refreshTimer->setSingleShot(false); // keep refreshing
  refreshTimer->setInterval(RefreshInterval);
  connect(refreshTimer, SIGNAL(timeout()), SLOT(refresh()));

  connect(this, SIGNAL(updateContextMenuRequested(void*,void*)), SLOT(onUpdateContextMenuRequested(void*,void*)),
          Qt::QueuedConnection);

  ::instance_ = this;

  refreshTimer->start();
}

WindowDriverPrivate::~WindowDriverPrivate() { ::instance_ = nullptr; }

// - Text -

QString WindowDriverPrivate::transformText(const QString &text, qint64 hash) const
{
  QString ret;
  if (translationEnabled) {
    ret = manager->findTranslationWithHash(hash);
    //if (repl.isEmpty()) {
    //  if (enabled)
    //    manager->requestTranslation(text, hash);
    if (textVisible && !ret.isEmpty() && ret != text)
      ret.append(" / ")
         .append(text);
      //ret = QString("%1 / %2").arg(ret, text);
  }
  if (ret.isEmpty())
    ret = text;
  return ret;
}

// - Processes and threads -

void WindowDriverPrivate::updateThreadWindows(DWORD threadId)
{
  WinIter::iterThreadChildWindows(threadId, [](HWND hWnd) {
    ::instance_->updateAbstractWindow(hWnd);
  });
  //WinIter::iterThreadChildWindows(threadId,
  //  boost::bind(&Self::updateAbstractWindow, ::instance_, _1));
}

void WindowDriverPrivate::updateProcessWindows(DWORD processId)
{ WinIter::iterProcessThreadIds(processId, updateThreadWindows); }

// - Windows -

void WindowDriverPrivate::updateAbstractWindow(HWND hWnd)
{
  wchar_t buf[TEXT_BUFFER_SIZE];

  // https://msdn.microsoft.com/en-us/library/windows/desktop/ee671196%28v=vs.85%29.aspx
  if (::RealGetWindowClassW(hWnd, buf, TEXT_BUFFER_SIZE)) {
    if (!::wcscmp(buf, L"SysTabControl32")) { // Tab, TabItem
      updateTabControl(hWnd, buf, TEXT_BUFFER_SIZE);
      return;
    }
    if (!::wcscmp(buf, L"SysListView32")) { // DataGrid, List
      updateListView(hWnd, buf, TEXT_BUFFER_SIZE);
      return;
    }
    //DOUT(QString::fromWCharArray(buf));

    // Only translate selected controls
    //if (::wcscmp(buf, L"ComboBox") &&
    //    ::wcscmp(buf, L"ComboBoxEx32") &&
    //    ::wcscmp(buf, L"Edit") &&
    //    ::wcscmp(buf, L"ListBox") &&
    //    ::wcscmp(buf, L"SysLink") &&
    //    ::wcscmp(buf, L"SysTreeView32"))
    //  return;
  }

  if (updateStandardWindow(hWnd, buf, TEXT_BUFFER_SIZE))
    repaintWindow(hWnd);

  if (HMENU hMenu = ::GetMenu(hWnd))
    if (updateMenu(hMenu, hWnd, buf, TEXT_BUFFER_SIZE))
      repaintMenuBar(hWnd);
}

void WindowDriverPrivate::updateContextMenu(HMENU hMenu, HWND hWnd)
{
  wchar_t buf[TEXT_BUFFER_SIZE];
  updateMenu(hMenu, hWnd, buf, TEXT_BUFFER_SIZE);
}

void WindowDriverPrivate::repaintMenuBar(HWND hWnd) { ::DrawMenuBar(hWnd); }

void WindowDriverPrivate::repaintWindow(HWND hWnd)
{
  enum { MaximumRepaintCount = 5 };
  static std::unordered_map<HWND, int> windows_;

  // 7/26/2015: Avoid repainting outer-most window
  // http://sakuradite.com/topic/981
  // http://sakuradite.com/topic/994
  auto p = windows_.find(hWnd);
  if (p == windows_.end())
    windows_[hWnd] = 1;
  else {
    if (!::GetParent(hWnd)) // paint only once for root window
      return;
    if (p->second > MaximumRepaintCount)
      return;
    p->second++;
  }

  ::InvalidateRect(hWnd, nullptr, TRUE);
}

bool WindowDriverPrivate::updateStandardWindow(HWND hWnd, LPWSTR buffer, int bufferSize)
{
  enum { TextRole = Window::WindowTextRole };
  qint64 h = 0;
  int sz = ::GetWindowTextW(hWnd, buffer, bufferSize);
  if (sz) {
#ifdef VNRAGENT_ENABLE_NTLEA // NTLEA could mess up the length of the string orz
    sz = ::wcslen(buffer);
#endif // VNRAGENT_ENABLE_NTLEA
    h = Window::hashWCharArray(buffer, sz);
  }

  QString repl;
  long anchor = Window::hashWindow(hWnd);
  const auto &e = manager->findEntryWithAnchor(anchor);
  if (!e.isEmpty())
    repl = transformText(e.text, e.hash);
  else if (enabled && h && sz) {
    QByteArray data((const char *)buffer, sz * 2);
    repl = manager->decodeText(data);
    manager->addEntry(data, repl, h, anchor, TextRole);
  }

  // DefWindowProcW is used instead of SetWindowTextW
  // https://groups.google.com/forum/?fromgroups#!topic/microsoft.public.platformsdk.mslayerforunicode/nWi3dlZeS60
  if (!repl.isEmpty() && h != Window::hashString(repl)) {
    if (repl.size() >= bufferSize)
      //::SetWindowTextW(hWnd, repl.utf16());
      ::DefWindowProcW(hWnd, WM_SETTEXT, 0, (LPARAM)repl.utf16());
    else { // faster
      buffer[repl.size()] = 0;
      repl.toWCharArray(buffer);
      //::SetWindowTextW(hWnd, buffer);
      ::DefWindowProcW(hWnd, WM_SETTEXT, 0, (LPARAM)buffer);
    }

    return true;
  }
  return false;
}

bool WindowDriverPrivate::updateMenu(HMENU hMenu, HWND hWnd, LPWSTR buffer, int bufferSize)
{
  enum { TextRole = Window::MenuTextRole };
  if (!hMenu)
    return false;
  int count = ::GetMenuItemCount(hMenu);
  if (count <= 0)
    return false;

  bool ret = false;

  MENUITEMINFOW info = {};
  info.cbSize = sizeof(info);
  for (int i = 0; i < count; i++) {
    info.fMask = MIIM_SUBMENU | MIIM_TYPE | MIIM_ID;
    info.cch = bufferSize;
    info.dwTypeData = buffer;
    if (::GetMenuItemInfoW(hMenu, i, TRUE, &info)) { // fByPosition: TRUE
      if (int sz = info.cch) {
#ifdef VNRAGENT_ENABLE_NTLEA // NTLEA could mess up the length of the string orz
        sz = ::wcslen(buffer);
#endif // VNRAGENT_ENABLE_NTLEA
        qint64 h = Window::hashWCharArray(buffer, sz);

        QString repl;
        long anchor = Window::hashWindowItem(hWnd, Window::MenuTextRole, (info.wID<<2) + (i<<4));
        const auto &e = manager->findEntryWithAnchor(anchor);
        if (!e.isEmpty())
          repl = transformText(e.text, e.hash);
        else if (enabled && h && sz) {
          QByteArray data((const char *)buffer, sz * 2);
          QString t = QString::fromWCharArray(buffer, sz);
          //repl = manager->decodeText(data); // disable transcoding menu text
          repl = QString::fromWCharArray(buffer, sz);
          manager->addEntry(data, repl, h, anchor, TextRole);
        }

        if (!repl.isEmpty() && h != Window::hashString(repl)) {
          int sz = qMin(repl.size(), bufferSize);
          info.fMask = MIIM_STRING;
          info.dwTypeData = buffer;
          info.cch = sz;
          info.dwTypeData[sz] = 0;
          repl.toWCharArray(info.dwTypeData);
          ::SetMenuItemInfoW(hMenu, i, TRUE, &info);
          ret = true;
        }
      }

      if (info.hSubMenu)
        ret = updateMenu(info.hSubMenu, hWnd, buffer, bufferSize) || ret;
    }
  }
  return ret;
}

bool WindowDriverPrivate::updateTabControl(HWND hWnd, LPWSTR buffer, int bufferSize)
{
  enum { TextRole = Window::TabTextRole };
  bool ret = false;
  LRESULT count = ::SendMessageW(hWnd, TCM_GETITEMCOUNT, 0, 0);
  TCITEMW item = {};
  for (int i = 0; i < count; i++) {
    item.mask = TCIF_TEXT;
    item.pszText = buffer;
    item.cchTextMax = bufferSize;
    if (!::SendMessageW(hWnd, TCM_GETITEM, i, (LPARAM)&item))
      break;
    int sz = ::wcslen(item.pszText);
    if (!sz)
      continue;
    qint64 h = Window::hashWCharArray(buffer, sz);

    QString repl;
    long anchor = Window::hashWindowItem(hWnd, TextRole, i);
    const auto &e = manager->findEntryWithAnchor(anchor);
    if (!e.isEmpty())
      repl = transformText(e.text, e.hash);
    else if (enabled && h && sz) {
      QByteArray data((const char *)buffer, sz * 2);
      repl = manager->decodeText(data);
      manager->addEntry(data, repl, h, anchor, TextRole);
    }

    if (!repl.isEmpty() && h != Window::hashString(repl)) {
      ret = true;
      if (repl.size() < bufferSize) {
        buffer[repl.size()] = 0;
        repl.toWCharArray(buffer);
        item.pszText = buffer;
        item.mask = TCIF_TEXT;
        ::SendMessageW(hWnd, TCM_SETITEM, i, (LPARAM)&item);
      } else {
        wchar_t *w = new wchar_t[repl.size() +1];
        w[repl.size()] = 0;
        repl.toWCharArray(w);
        item.pszText = w;
        item.mask = TCIF_TEXT;
        ::SendMessageW(hWnd, TCM_SETITEM, i, (LPARAM)&item);
        delete[] w;
      }
    }
  }
  return ret;
}

bool WindowDriverPrivate::updateListView(HWND hWnd, LPWSTR buffer, int bufferSize)
{
  enum { TextRole = Window::ListTextRole };
  enum { MAX_COLUMN = 100 };
  bool ret = false;
  for (int i = 0; i < MAX_COLUMN; i++) {
    LVCOLUMNW column = {};
    column.mask = LVCF_TEXT;
    column.pszText = buffer;
    column.cchTextMax = bufferSize;
    if (!ListView_GetColumn(hWnd, i, &column))
      break;
    int sz = ::wcslen(buffer);
    if (!sz)
      continue;

    qint64 h = Window::hashWCharArray(buffer, sz);
    QString repl;
    long anchor = Window::hashWindowItem(hWnd, TextRole, i);
    const auto &e = manager->findEntryWithAnchor(anchor);
    if (!e.isEmpty())
      repl = transformText(e.text, e.hash);
    else if (enabled && h && sz) {
      QByteArray data((const char *)buffer, sz * 2);
      repl = manager->decodeText(data);
      manager->addEntry(data, repl, h, anchor, TextRole);
    }

    if (!repl.isEmpty() && h != Window::hashString(repl)) {
      ret = true;
      if (repl.size() < bufferSize) {
        buffer[repl.size()] = 0;
        repl.toWCharArray(buffer);
        column.mask = TCIF_TEXT;
        column.pszText = buffer;
        ListView_SetColumn(hWnd, i, &column);
      } else {
        wchar_t *w = new wchar_t[repl.size() +1];
        w[repl.size()] = 0;
        repl.toWCharArray(w);
        column.mask = TCIF_TEXT;
        column.pszText = w;
        ListView_SetColumn(hWnd, i, &column);
        delete[] w;
      }
    }
  }
  return ret;
}

// EOF

/*

// - Helpers -

void WindowDriverPrivate::updateWindows()
{
  QHash<HWND, uint> w;
  foreach (const auto &e, manager->entries())
    w[e.window] |= e.role;

  enum { BUFFER_SIZE = 256 };
  wchar_t buf[BUFFER_SIZE];

  for (auto it = w.begin(); it != w.end(); ++it) {
    HWND h = it.key();
    if (::IsWindow(h)) {
      uint roles = it.value();
      if (roles & Window::WindowTextRole)
        updateWindow(h, buf, BUFFER_SIZE);
      if (roles & Window::MenuTextRole)
        if (HMENU hMenu = ::GetMenu(h)) {
          updateMenu(hMenu, h, buf, BUFFER_SIZE);
          ::DrawMenuBar(h);
        }
}

  inline bool NotSupportedWindow(HWND hWnd)
  {
    enum { bufsz = 64 };
    char buf[bufsz];
    return !::RealGetWindowClassA(hWnd, buf, bufsz) ||
        ::strcmp(buf, "ComboBox") &&
        ::strcmp(buf, "ComboBoxEx32") &&
        ::strcmp(buf, "Edit") &&
        ::strcmp(buf, "ListBox") &&
        ::strcmp(buf, "SysLink") &&
        ::strcmp(buf, "SysTreeView32");
  }

*/

# coding: utf8
# skdwm.py
# 12/11/2012 jichi
# Windows only
#
# See: http://labs.qt.nokia.com/2009/09/15/using-blur-behind-on-windows/
# http://sic.no-ammo.org/git/index.cgi/Client.git/blob_plain/HEAD:/modules/qtwin/qtwin.h
# http://sic.no-ammo.org/git/index.cgi/Client.git/blob_plain/HEAD:/modules/qtwin/qtwin.cpp

## DWM API
import skos
if skos.WIN:
  import ctypes
  import win32api, win32con, win32security
  import skwinapi
  from skdebug import dprint, dwarn

  def isCompositionEnabled():
    """
    @return bool
    """
    if skwinapi.dwmapi:
      yes = skwinapi.BOOL()
      hr = skwinapi.DwmIsCompositionEnabled(ctypes.byref(yes))
      if not hr and yes:
        return True
    return False

  #  Window notifier is not used.
  def enableBlurBehindWindow(hwnd, enable=True):
    """
    @param  hwnd  HWND
    @param  enabled  bool
    @return  bool
    """
    bb = skwinapi.DWM_BLURBEHIND(
      fEnable = 1 if enable else 0,
      dwFlags = skwinapi.DWM_BB_ENABLE,
    )
    return not skwinapi.DwmEnableBlurBehindWindow(hwnd, ctypes.byref(bb))

  #  Window notifier is used.
  #bool enableBlurBehindWindow(QWidget *widget, bool enable = true);

  #  Window notifier is not used.
  def extendFrameIntoClientArea(hwnd, left=-1, top=-1, right=-1, bottom=-1):
    """
      @param  hwnd  HWND
      @param  left  int
      @param  top  int
      @param  right  int
      @param  bottom  int
      @return  bool
    """
    m = skwinapi.MARGINS(left, right, top, bottom)
    return not skwinapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(m))

  #  Window notifier is used.
  #bool extendFrameIntoClientArea(QWidget *widget, int left = -1, int top = -1, int right = -1, int bottom = -1);

  #QColor colorizationColor()
  #{
  #  DWORD color = 0;
  #  BOOL opaque = FALSE; // unused
  #
  #  HRESULT hr = DWMAPI::DwmGetColorizationColor(&color, &opaque);
  #  return SUCCEEDED(hr) ? QColor(color) :
  #         QApplication::palette().window().color();
  #}

## WindowNotifier
# Note: This will delay all winEvent!

# EOF

#from Qt5.QtWidgets import QWidget
#
#WM_DWMCOMPOSITIONCHANGED = 0x031e
#
## Invisible background window.
## Inherit QWidget to access protected winEvent.
#class DwmEventListener(QWidget):
#
#  compositionEnabledChanged = Signal()
#
#  def __init__(self, parent=None):
#    super(DwmEventListener, self).__init__(parent)
#    self.winId() # enforce a valid hwnd
#
#  def winEvent(self, message, result):
#    """@reimp @protected
#    @param  message LPMSG
#    @param  result LPLONG
#    @return  bool
#    """
#    if  message.message == WM_DWMCOMPOSITIONCHANGED:
#      self.compositionEnabledChanged.emit()
#    return super(DwmEventListener, self).winEvent(message, result)
#
#    # Not implemented
#    #Q_ASSERT(message);
#    #if (!widgets_.empty() &&
#    #    message && message->message == WM_DWMCOMPOSITIONCHANGED) {
#    #  bool enabled = Dwm::isCompositionEnabled();
#    #  foreach (QWidget *w, widgets_) {
#    #    Q_ASSERT(w);
#    #    w->setAttribute(Qt::WA_NoSystemBackground, enabled);
#    #    if (enabled) {
#    #      Dwm::enableBlurBehindWindow(w->winId(), true);
#    #      Dwm::extendFrameIntoClientArea(w->winId(), -1, -1, -1, -1);
#    #    } else {
#    #      Dwm::enableBlurBehindWindow(w->winId(), false);
#    #      Dwm::extendFrameIntoClientArea(w->winId(), 0, 0, 0, 0);
#    #    }
#    #    w->update();
#    #  }
#    #}


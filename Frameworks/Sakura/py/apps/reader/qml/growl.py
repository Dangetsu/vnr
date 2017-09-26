# coding: utf8
# growl.py
# 10/28/2012 jichi

from PySide.QtCore import Signal, Slot, Qt, QObject
from sakurakit.skdebug import dprint
#from sakurakit.skqml import QmlObject

#@Q_Q
#class _GrowlBean(object):
#  def __init__(self, q):
#    q.destroyed.connect(self._onDestroyed)
#
#  def _onDestroyed(self):
#    if self.q is GrowlBean.instance:
#      GrowlBean.instance = None

class GrowlBean(QObject):

  instance = None

  def __init__(self, parent=None):
    super(GrowlBean, self).__init__(parent)
    GrowlBean.instance = self
    #self.__d = _GrowlBean(self)
    for k in 'pageBreak', 'show', 'message', 'warning', 'error', 'notification':
      q = getattr(self, 'q_' + k)
      s = getattr(self, k)
      q.connect(s, Qt.QueuedConnection)
    dprint("pass")

  ## Sequential signals ##
  pageBreak = Signal()
  show = Signal()
  message = Signal(unicode)
  warning = Signal(unicode)
  error = Signal(unicode)
  notification = Signal(unicode)

  ## Queued Signals ##
  q_pageBreak = Signal()
  q_show = Signal()
  q_message = Signal(unicode)
  q_warning = Signal(unicode)
  q_error = Signal(unicode)
  q_notification = Signal(unicode)

def show(async=False):
  try:
    if async: GrowlBean.instance.q_show.emit()
    else: GrowlBean.instance.show.emit()
  except AttributeError: pass

def pageBreak(async=False):
  try:
    if async: GrowlBean.instance.q_pageBreak.emit()
    else: GrowlBean.instance.pageBreak.emit()
  except AttributeError: pass

def msg(text, async=False):
  try:
    if async: GrowlBean.instance.q_message.emit(text)
    else: GrowlBean.instance.message.emit(text)
  except AttributeError: pass

def warn(text, async=False):
  try:
    if async: GrowlBean.instance.q_warning.emit(text)
    else: GrowlBean.instance.warning.emit(text)
  except AttributeError: pass

def error(text, async=False):
  try:
    if async: GrowlBean.instance.q_error.emit(text)
    else: GrowlBean.instance.error.emit(text)
  except AttributeError: pass

def notify(text, async=False):
  try:
    if async: GrowlBean.instance.q_notification.emit(text)
    else: GrowlBean.instance.notification.emit(text)
  except AttributeError: pass

#@QmlObject
class GrowlQmlProxy(QObject):
  def __init__(self, parent=None):
    super(GrowlQmlProxy, self).__init__(parent)

  @Slot()
  def show(self): show()

  @Slot()
  def pageBreak(self): pageBreak(text)

  @Slot(unicode)
  def msg(self, text): msg(text)

  @Slot(unicode)
  def warn(self, text): warn(text)

  @Slot(unicode)
  def error(self, text): error(text)

  @Slot(unicode)
  def notify(self, text): notify(text)

class GrowlCoffeeProxy(QObject):
  def __init__(self, parent=None):
    super(GrowlCoffeeProxy).__init__(parent)

  @Slot()
  def show(self): show()

  @Slot()
  def pageBreak(self): pageBreak(text)

  @Slot(unicode)
  def msg(self, text): msg(text)

  @Slot(unicode)
  def warn(self, text): warn(text)

  @Slot(unicode)
  def error(self, text): error(text)

  @Slot(unicode)
  def notify(self, text): notify(text)

# EOF

# coding: utf8
# growl.py
# 10/28/2012 jichi

from PySide.QtCore import Signal, Qt, QObject

class GrowlBean(QObject):

  instance = None

  def __init__(self, parent=None):
    super(GrowlBean, self).__init__(parent)
    GrowlBean.instance = self
    #self.__d = _GrowlBean(self)

    for k in 'message', 'warning', 'error', 'notification', 'pageBreak':
      q = getattr(self, 'q_' + k)
      s = getattr(self, k)
      q.connect(s, Qt.QueuedConnection)

    self.q_pageBreak.connect(self.pageBreak, Qt.QueuedConnection)
    self.q_message.connect(self.message, Qt.QueuedConnection)
    self.q_warning.connect(self.warning, Qt.QueuedConnection)
    self.q_error.connect(self.error, Qt.QueuedConnection)
    self.q_notification.connect(self.notification, Qt.QueuedConnection)
    #dprint("pass")

  ## Sequential signals ##
  message = Signal(unicode)
  warning = Signal(unicode)
  error = Signal(unicode)
  notification = Signal(unicode)
  pageBreak = Signal()

  ## Queued Signals ##
  q_message = Signal(unicode)
  q_warning = Signal(unicode)
  q_error = Signal(unicode)
  q_notification = Signal(unicode)
  q_pageBreak = Signal()

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

def pageBreak(async=False):
  try:
    if async: GrowlBean.instance.q_pageBreak.emit()
    else: GrowlBean.instance.pageBreak.emit()
  except AttributeError: pass

# EOF

#def show(async=False):
#  try:
#    if async: GrowlBean.instance.q_show.emit()
#    else: GrowlBean.instance.show.emit()
#  except AttributeError: pass

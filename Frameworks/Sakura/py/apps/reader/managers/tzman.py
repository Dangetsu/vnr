# coding: utf8
# tzman.py
# 12/11/2012 jichi

from PySide.QtCore import QObject, QTimer, QCoreApplication
from sakurakit import skos, skwin, skwinsec
from sakurakit.skclass import Q_Q, memoized, memoizedproperty, hasmemoizedproperty
from sakurakit.skdebug import dprint

# see: GetTimeInformation and TIME_ZONE_INFORMATION
TZI_JST = (
  -540, # Bias, actually, this is not required for most games
  u'\u6771\u4eac (\u6a19\u6e96\u6642)', # u"東京 (標準時)"
  (0,) * 8, # SYSTEMTIME
  0,
  u'\u6771\u4eac (\u590f\u6642\u9593)', # u"東京 (夏時間)"
  (0,) * 8, # SYSTEMTIME
  0,
)

def set_time_zone_info(tzi):
  with skwinsec.SkProcessElevator(skwinsec.SE_TIMEZONE_PRIVILEGE):
    skwin.set_time_zone_info(tzi)

@Q_Q
class _TimeZoneManager(object):

  @memoizedproperty
  def tzi(self): return skwin.get_time_zone_info()

  def hasTzi(self): return hasmemoizedproperty(self, 'tzi')

  @memoizedproperty
  def restoreTimer(self):
    ret = QTimer(self.q)
    ret.setSingleShot(True)
    ret.timeout.connect(self.restore)
    return ret

  def setToJst(self):
    tzi = self.tzi
    if tzi[1] != TZI_JST[1]:
      tzi = TZI_JST[0], TZI_JST[1], tzi[2], tzi[3], tzi[4], tzi[5], tzi[6]

      dprint("change time zone to JST")
      set_time_zone_info(tzi)

  def restore(self):
    if self.hasTzi() and self.tzi[1] != TZI_JST[1]:
      dprint("restore time zone")
      set_time_zone_info(self.tzi)

class TimeZoneManager(QObject):

  def __init__(self, parent=None):
    super(TimeZoneManager, self).__init__(parent)
    self.__d = _TimeZoneManager(self)
    QCoreApplication.instance().aboutToQuit.connect(self.__d.restore)

  def changeTimeZone(self, interval=5000): # The same as the timeout in gameman
    d = self.__d
    if not d.restoreTimer.isActive():
      d.setToJst()
    d.restoreTimer.start(interval)
    dprint("pass")

@memoized
def manager(): return TimeZoneManager()

# EOF

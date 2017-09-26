# coding: utf8
# gamerec.py
# 8/17/2014 jichi

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

from PySide.QtCore import QObject #, QTimer
from sakurakit.skclass import memoized

@memoized
def manager(): return GameRecorder()

class _GameRecorder:
  def __init__(self, q):
    #self.timer = QTimer(q)
    self.savePath = "" # unicode

    # Game information
    self.gameId = 0 # long
    self.gameItemId = 0 # long
    self.gameTitle = "" # unicode

    # Process information
    self.wid = 0 # long

class GameRecorder(QObject):
  def __init__(self, parent=None):
    super(GameRecorder, self).__init__(parent)
    self.__d = _GameRecorder(self)

  def saveImage(self):
    pass

  def saveText(self, text):
    """
    @param  text
    """
    pass

if __name__ == '__main__':
  m = manager()
  print m

# EOF

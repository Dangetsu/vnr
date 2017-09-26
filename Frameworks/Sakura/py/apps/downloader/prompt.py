# coding: utf8
# prompt.py
# 6/4/2013 jichi

from Qt5.QtWidgets import QMessageBox
from tr import my
import config

Yes = QMessageBox.Yes
No = QMessageBox.No

def _parent():
  """
  @return  QWidget  parent window
  """
  import window
  return window.MainWindow.instance

def confirmQuit():
  """
  @return  bool
  """
  from PySide.QtCore import QCoreApplication
  appName = QCoreApplication.instance().applicationName()
  return Yes == QMessageBox.question(_parent(),
      appName,
      my.tr("Quit {0}?").format(appName),
      Yes|No, No)

# EOF

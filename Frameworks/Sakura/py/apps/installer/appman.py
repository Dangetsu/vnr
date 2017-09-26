# coding: utf8
# appman.py
# 12/15/2012 jichi

import os
from PySide.QtCore import QObject
from sakurakit.skdebug import dprint
from sakurakit.skunicode import u
import config, osutil, settings

def is_player_activated():
  return os.path.exists(config.TRACE_PLAYER)

def is_reader_activated():
  return os.path.exists(config.TRACE_READER)

def activate_player():
  osutil.run_batch(config.SCRIPT_PLAYER_UPDATE)
  dprint("pass")

def deactivate_player():
  osutil.run_batch(config.SCRIPT_PLAYER_REMOVE)
  dprint("pass")

def activate_reader():
  osutil.run_batch(config.SCRIPT_READER_UPDATE)
  dprint("pass")

def deactivate_reader():
  osutil.run_batch(config.SCRIPT_READER_REMOVE)
  dprint("pass")

class AppManager(QObject):

  def isReaderActivated(self):
    return is_reader_activated()

  def isPlayerActivated(self):
    return is_player_activated()

  def setPlayerActivated(self, value):
    if value:
      activate_player()
    else:
      deactivate_player()
    settings.global_().setPlayerActivated(is_player_activated())

  def setReaderActivated(self, value):
    if value:
      activate_reader()
    else:
      deactivate_reader()
    settings.global_().setPlayerActivated(is_reader_activated())

# EOF

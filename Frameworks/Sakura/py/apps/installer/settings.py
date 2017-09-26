# coding: utf8
# settings.py
# 12/13/2012 jichi

from PySide.QtCore import QSettings
from sakurakit.skclass import memoized
from sakurakit.sktypes import to_int, to_unicode
import config

def to_bool(value): return value == True or value  == 'true'

class Settings(QSettings):

  def __init__(self):
    super(Settings, self).__init__(
      QSettings.NativeFormat, QSettings.UserScope,
      config.VERSION_DOMAIN, config.VERSION_NAME)

  def setVersion(self, value): self.setValue('Version', value)
  def version(self): return to_int(self.value('Version'))

  def setLanguage(self, value): self.setValue('UserLanguage', value)
  def language(self): return to_unicode(self.value('UserLanguage'))

  def setPlayerActivated(self, value): self.setValue("PlayerActivated", value)
  def isPlayerActivated(self): return to_bool(self.value("PlayerActivated", True))

  def setReaderActivated(self, value): self.setValue("ReaderActivated", value)
  def isReaderActivated(self): return to_bool(self.value("ReaderActivated", True))

@memoized
def global_(): return Settings()

# EOF

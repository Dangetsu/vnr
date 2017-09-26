# coding: utf8
# app.py
# 12/13/2012 jichi

__all__ = 'Application',

from Qt5.QtWidgets import QApplication
from sakurakit.skdebug import dprint
from tr import my
#import config

class Application(QApplication):
  def __init__(self, argv):
    super(Application, self).__init__(argv)
    self.setApplicationName(my.tr("YouTube Downloader"))

    #self.setApplicationVersion(str(config.VERSION_TIMESTAMP))
    #self.setOrganizationName(config.VERSION_ORGANIZATION)
    #self.setOrganizationDomain(config.VERSION_DOMAIN)

    dprint("pass")

# EOF

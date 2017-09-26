# coding: utf8
# app.py
# 12/13/2012 jichi

__all__ = 'Application',

from PySide.QtCore import QTranslator
from Qt5.QtWidgets import QApplication
from sakurakit.skdebug import dprint, dwarn
import config

class Application(QApplication):
  def __init__(self, argv):
    super(Application, self).__init__(argv)

    self.setApplicationName(self.tr("Add or Remove Features"))
    self.setApplicationVersion(str(config.VERSION_TIMESTAMP))
    self.setOrganizationName(config.VERSION_ORGANIZATION)
    self.setOrganizationDomain(config.VERSION_DOMAIN)

    #if skos.WIN:
    #  ignoreWindowsExceptions()

    dprint("pass")

  @staticmethod
  def systemLocale():
    from PySide.QtCore import QLocale
    system = QLocale.system()
    lang, script = system.language(), system.script()
    if lang == QLocale.English: return 'en_US'
    if lang == QLocale.Japanese: return 'ja_JP'
    if lang == QLocale.Korean: return 'ko_KR'
    if lang == QLocale.French: return 'fr_FR'
    if lang == QLocale.German: return 'de_DE'
    if lang == QLocale.Italian: return 'it_IT'
    if lang == QLocale.Spanish: return 'es_ES'
    if lang == QLocale.Portuguese: return 'pt_PT'
    if lang == QLocale.Russian: return 'ru_RU'
    if lang == QLocale.Polish: return 'pl_PL'
    if lang == QLocale.Chinese: return 'zh_CN' if script == QLocale.SimplifiedChineseScript else 'zh_TW'

  def loadTranslations(self):
    locale = self.systemLocale()

    if locale and locale != 'en_US':
      dprint("loading translation for %s" % locale)

      t = QTranslator(self)
      ok = t.load('qt_%s' % locale, config.QT_TRANSLATIONS_LOCATION)
      assert ok, "failed to load qt translation"
      if ok:
        self.installTranslator(t)
      else:
        dwarn("warning: failed to load translation from location %s" % location)

# EOF

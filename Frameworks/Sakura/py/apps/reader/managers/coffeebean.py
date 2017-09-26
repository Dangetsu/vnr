# coding: utf8
# coffeebean.py
# 10/11/2013 jichi

__all__ = 'YoutubeBean', 'CoffeeBeanManager'

from PySide.QtCore import Slot, QObject
from sakurakit.skclass import memoized, memoizedproperty
from sakurakit.skdebug import dprint
from sakurakit.sktr import utr_
from mytr import my
import growl

class MainBean(QObject):
  def __init__(self, parent=None):
    super(MainBean, self).__init__(parent)

  @Slot(unicode)
  def showUser(self, name): # unicode ->
    import main
    main.manager().showUserView(name=name)

  @Slot(long)
  def showGame(self, itemId): # long ->
    import main
    main.manager().showGameView(itemId=itemId)

  @Slot(long)
  def showTopic(self, topicId): # long ->
    import main
    main.manager().showTopic(topicId)

  @Slot(long)
  def showGameTopics(self, itemId): # long ->
    import main
    main.manager().showGameTopics(itemId)

class YoutubeBean(QObject):
  def __init__(self, parent=None):
    super(YoutubeBean, self).__init__(parent)

  @Slot(str)
  def get(self, vid):
    """
    @param  vid  str  youtube id
    """
    dprint(vid)
    import prompt
    if prompt.confirmDownloadGameVideo():
      #growl.msg("%s YouTube(%s) ..." % (my.tr("Downloading to Desktop"), vid))
      growl.msg(my.tr("Downloading YouTube video to Desktop") + " ...")
      import procutil
      procutil.getyoutube([vid])
      #return dl.get(vid)

class I18nBean(QObject):
  def __init__(self, parent=None):
    super(I18nBean, self).__init__(parent)

  @Slot(result=unicode)
  def lang(self):
    """
    @return  user language in html format
    """
    import config, dataman
    lang = dataman.manager().user().language
    return config.language2htmllocale(lang) or 'ja'

  @Slot(unicode, result=unicode)
  def tr(self, text):
    """
    @param  text  unicode  english
    @return  unicode
    """
    return utr_(text)

  @Slot(unicode, result=unicode)
  def getLangShortName(self, lang):
    """
    @param  lang  unicode
    @return  unicode
    """
    if not lang:
      return ''
    import config, i18n
    ret = config.htmllocale2language(lang)
    return i18n.language_name2(ret) or ret or lang

  @Slot(unicode, result=unicode)
  def getTopicTypeName(self, type):
    """
    @param  type  unicode
    @return  unicode
    """
    import i18n
    return i18n.topic_type_name(type)

# Temporarily disabled
#class JlpBean(QObject):
#  def __init__(self, parent):
#    super(JlpBean, self).__init__(parent)
#
#  @Slot(result=bool)
#  def isEnabled(self):
#    import jlpman
#    return jlpman.manager().isEnabled()
#
#  @Slot(unicode, result=unicode)
#  def parse(self, text):
#    import json
#    import jlpman
#    ret = jlpman.manager().parseToRuby(text)
#    return json.dumps(ret) if ret else ''

@memoized
def manager(): return CoffeeBeanManager()

class CoffeeBeanManager(object):
  def __init__(self, parent=None):
    """
    @param  parent  QObject
    """
    self._parent = parent

  def parent(self): return self._parent
  def setParent(self, v): self._parent = v

  @memoizedproperty
  def mainBean(self): return MainBean(self.parent())

  @memoizedproperty
  def i18nBean(self): return I18nBean(self.parent())

  @memoizedproperty
  def youtubeBean(self): return YoutubeBean(self.parent())

  @memoizedproperty
  def cacheBean(self):
    import cacheman
    return cacheman.CacheCoffeeBean(self.parent())

  @memoizedproperty
  def clipBean(self):
    from sakurakit import skwebkit
    return skwebkit.SkClipboardProxy(self.parent())

  @memoizedproperty
  def growlBean(self):
    import growl
    return growl.GrowlCoffeeProxy(self.parent())

  @memoizedproperty
  def jlpBean(self):
    return JlpBean(self.parent())

  @memoizedproperty
  def shioriBean(self):
    import shiori
    return shiori.ShioriCoffeeProxy(self.parent())

  @memoizedproperty
  def ttsBean(self):
    import ttsman
    return ttsman.TtsCoffeeBean(self.parent())

  @memoizedproperty
  def trBean(self):
    import trman
    return trman.TranslatorCoffeeBean(self.parent())

# EOF

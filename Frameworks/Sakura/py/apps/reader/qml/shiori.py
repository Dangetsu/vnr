# coding: utf8
# shiori.py
# 10/10/2012 jichi

import json
from functools import partial
from PySide.QtCore import Signal, Slot, Property, QObject, QMutex
from sakurakit import skthreads
from sakurakit.skdebug import dprint, dwarn
#from sakurakit.skqml import QmlObject
from sakurakit.sktr import tr_
from mytr import my
from kagami import GrimoireBean
import dataman, dictman, i18n, qmldialog, rc, settings

class _ShioriBean:
  def __init__(self):
    self.enabled = True
    self._renderMutex = QMutex()

  def renderKorean(self, text):
    """
    @param  text  unicode
    @return  unicode
    """
    ret = ""
    if self._renderMutex.tryLock():
      ret = dictman.manager().renderKorean(text)
      self._renderMutex.unlock()
    else:
      dwarn("ignore thread contention")
    return ret

  def renderJapanese(self, text):
    """
    @param  text  unicode
    @return  unicode
    """
    ret = ""
    feature = GrimoireBean.instance.lookupFeature(text)
    if self._renderMutex.tryLock():
      ret = skthreads.runsync(partial(
          dictman.manager().renderJapanese, text, exact=True,feature=feature)) # do exact match for speed
      self._renderMutex.unlock()
    else:
      dwarn("ignore thread contention")
    return ret

  def renderJson(self, data):
    """
    @param  data  unicode  json
    @return  unicode
    """
    ret = ""
    if self._renderMutex.tryLock():
      try:
        data = json.loads(data)
        ret = self._renderJson(**data) or ''
      except Exception, e:
        dwarn(e)
      self._renderMutex.unlock()
    else:
      dwarn("ignore thread contention")
    return ret

  @staticmethod
  def _renderJson(type, id=0, source='', target='', **kwargs):
    """
    @param  type  str
    @param* id  long
    @param* source  unicode
    @param* target  unicode
    @return  unicode or None
    """
    if type == 'term' and id:
      td = dataman.manager().queryTermData(id)
      if td:
        return rc.jinja_template('html/term').render({
          'td': td,
          'userName': td.userName,
          'updateUserName': td.updateUserName,
          'source': source,
          'target': target,
          'i18n': i18n,
          'tr': i18n.autotr_,
        })
    elif type == 'tip':
      l = filter(bool, (source, target))
      return ': '.join(l)

#@QmlObject
class ShioriBean(QObject):

  instance = None

  def __init__(self, parent=None):
    super(ShioriBean, self).__init__(parent)
    self.__d = _ShioriBean()
    ShioriBean.instance = self

    ss = settings.global_()
    self.__d.enabled = ss.isJapaneseDictionaryEnabled()
    ss.japaneseDictionaryEnabledChanged.connect(self.setEnabled)
    dprint("pass")

  def isEnabled(self): return self.__d.enabled
  def setEnabled(self, v):
    if self.__d.enabled != v:
      self.__d.enabled = v
      self.enabledChanged.emit(v)
  enabledChanged = Signal(bool)
  enabled = Property(bool, isEnabled, setEnabled, notify=enabledChanged)

  @Slot(unicode, unicode, result=unicode)
  def renderLookup(self, text, language):
    """
    @param  text  Japanese phrase
    @param  language
    @return  unicode not None  html
    """
    if language == 'ja':
      return self.__d.renderJapanese(text)
    if language == 'ko':
      return self.__d.renderKorean(text)
    return ''

  @Slot(unicode, result=unicode)
  def renderJson(self, json):
    """
    @param  json  term
    @return  unicode not None  html
    """
    return self.__d.renderJson(json)

  popupLookup = Signal(unicode, unicode, int, int)  # text, language, x, y
  popupJson = Signal(unicode, int, int)  # json, x, y

def lookupat(text, language, x, y):
  """
  @param  text  unicode
  @param  x  int
  @param  y  int
  """
  #dprint("x = %s, y = %s" % (x,y))
  if ShioriBean.instance.isEnabled():
    qmldialog.Kagami.instance.raise_()
    ShioriBean.instance.popupLookup.emit(text, language, x, y)

def showjsonat(data, x, y):
  """
  @param  data  str
  @param  x  int
  @param  y  int
  """
  #if ShioriBean.instance.isEnabled():
  qmldialog.Kagami.instance.raise_()
  ShioriBean.instance.popupJson.emit(data, x, y)

def showjson(data):
  """
  @param  data  str
  """
  from sakurakit import skos, skwin
  #if ShioriBean.instance.isEnabled():
  if skos.WIN:
    try: x, y = skwin.get_mouse_pos()
    except Exception, e:
      dwarn(e)
      return
    showjsonat(data, x, y)

def showterm(id):
  """
  @param  id  long
  """
  showjson(json.dumps({
    'type': 'term',
    'id': id,
  }))

#@QmlObject
class ShioriQmlProxy(QObject):
  def __init__(self, parent=None):
    super(ShioriQmlProxy, self).__init__(parent)

  @Slot(unicode, unicode, int, int)
  def popup(self, language, text, x, y):
    lookupat(text, x, y)

class ShioriCoffeeProxy(QObject):
  def __init__(self, parent=None):
    super(ShioriCoffeeProxy, self).__init__(parent)

  @Slot(unicode, unicode, int, int)
  def popup(self, text, language, x, y):
    lookupat(text, language, x, y)

# EOF

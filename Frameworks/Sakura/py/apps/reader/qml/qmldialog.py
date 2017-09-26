# coding: utf8
# qmldialog.py
# 10/5/2012 jichi

from PySide.QtCore import QObject
from PySide.QtGui import QIcon
from sakurakit.skdebug import dprint
from sakurakit.skqml import SkDeclarativeView
from sakurakit.skwidgets import shortcut
import rc, qmlrc

#class Omajinai(SkDeclarativeView):
#  def __init__(self, parent=None):
#    super(Omajinai, self).__init__(rc.qml_url('omajinai'), parent)
#    dprint("pass")

class Kagami(SkDeclarativeView):
  instance = None

  def __init__(self, parent=None):
    super(Kagami, self).__init__(rc.qml_url('kagami'), parent)
      #imageProviders=(
      #  (qmlrc.ResourceImageProvider.PROVIDER_ID, qmlrc.ResourceImageProvider()),
      #))

    root = self.rootObject()

    ctx = 'globalComet', 'gameComet'
    for k in ctx:
      obj = root.findChild(QObject, k)
      assert obj
      setattr(self, k, obj)

    Kagami.instance = self

    # Not used ...
    #self._createShortcuts()
    dprint("pass")

  def _createShortcuts(self):
    from functools import partial
    import main
    root = self.rootObject()
    sig = root.ignoresFocusChanged
    # Must be consistent with kagami/appmenu.qml

    b = root.property('ignoresFocus')
    m = main.manager()
    s = shortcut('alt+q', m.confirmQuit, parent=self)
    s.setEnabled(not b)
    sig.connect(partial((lambda s, v: s.setEnabled(not v)), s))

    #shortcut('alt+r', m.confirmRestart, parent=self)
    #shortcut('alt+o', m.showPreferences, parent=self) # Does not work on windows?!
    #shortcut('alt+f', m.showGameBoard, parent=self)

  def comets(self):
    return self.globalComet, self.gameComet

  def stopComets(self):
    for it in self.comets():
      if it.property('active'):
        it.setProperty('active', False)
      #it.stop()

  def createPostComet(self):
    """
    @return  QObject
    """
    root = self.rootObject()
    return root.createPostComet()

  def setMirageVisible(self, value):
    """
    @param  value  bool
    """
    root = self.rootObject()
    root.setProperty('mirageVisible', value)

class VoiceView(SkDeclarativeView):

  def __init__(self, parent=None):
    super(VoiceView, self).__init__(rc.qml_url('voiceview'), parent,
      imageProviders=(
        (qmlrc.ResourceImageProvider.PROVIDER_ID, qmlrc.ResourceImageProvider()),
      ))
    self.setWindowIcon(rc.icon('window-voice'))
    dprint("pass")

class TermView(SkDeclarativeView):

  instance = None

  def __init__(self, parent=None):
    super(TermView, self).__init__(rc.qml_url('termview'), parent,
      imageProviders=(
        (qmlrc.ResourceImageProvider.PROVIDER_ID, qmlrc.ResourceImageProvider()),
      ))
    self.setWindowIcon(rc.icon('window-dict'))

    root = self.rootObject()

    ctx = 'termComet',
    for k in ctx:
      obj = root.findChild(QObject, k)
      assert obj
      setattr(self, k, obj)

    TermView.instance = self

    dprint("pass")

class SubtitleMaker(SkDeclarativeView):
  instance = None

  def __init__(self, parent=None):
    super(SubtitleMaker, self).__init__(rc.qml_url('submaker'), parent,
      imageProviders=(
        (qmlrc.ResourceImageProvider.PROVIDER_ID, qmlrc.ResourceImageProvider()),
      ))
    self.setWindowIcon(rc.icon('window-submaker'))
    SubtitleMaker.instance = self
    dprint("pass")

class SubtitleView(SkDeclarativeView):

  def __init__(self, parent=None):
    super(SubtitleView, self).__init__(rc.qml_url('subview'), parent,
      imageProviders=(
        (qmlrc.ResourceImageProvider.PROVIDER_ID, qmlrc.ResourceImageProvider()),
      ))
    self.setWindowIcon(rc.icon('window-subview'))
    dprint("pass")

  def setGame(self, game):
    """
    @param  game  dataman.GameObject
    """
    icon = game.icon() if game else None
    self.setWindowIcon(icon or rc.icon('window-subview'))
    root = self.rootObject()
    root.setProperty('game', game)
    #self.rootObject().gameChanged.emit()

class ReferenceView(SkDeclarativeView):

  def __init__(self, parent=None):
    super(ReferenceView, self).__init__(rc.qml_url('refview'), parent,
      imageProviders=(
        (qmlrc.ResourceImageProvider.PROVIDER_ID, qmlrc.ResourceImageProvider()),
      ))
    self.setWindowIcon(rc.icon('window-refview'))
    dprint("pass")

  def setGameId(self, gameId):
    """
    @param  game  dataman.GameObject
    """
    import dataman
    icon = dataman.manager().queryGameIcon(id=gameId)
    self.setWindowIcon(icon or rc.icon('window-refview'))
    root = self.rootObject()
    root.setProperty('gameId', gameId)
    #self.rootObject().gameIdChanged.emit()

# EOF

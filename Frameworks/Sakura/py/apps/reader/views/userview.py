# coding: utf8
# userview.py
# 6/29/2013 jichi

__all__ = 'UserViewManager' #, 'UserViewManagerProxy'

from PySide.QtCore import Qt, Slot
from PySide import QtCore
from sakurakit.skclass import memoized
from sakurakit.sktr import tr_
#from sakurakit.skqml import QmlObject
from sakurakit.skwebkit import SkWebView
from mytr import my, mytr_
import dataman, growl, i18n, osutil, rc

class WebDialog(SkWebView):

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(WebDialog, self).__init__(parent, WINDOW_FLAGS)
    self.titleChanged.connect(self.setWindowTitle)

    from PySide.QtWebKit import QWebPage

    self.pageAction(QWebPage.Reload).triggered.connect(self.onReload)

    self.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks) # Since there are local images
    #self.page().setLinkDelegationPolicy(QWebPage.DelegateExternalLinks)
    self.linkClicked.connect(osutil.open_url)

  def onReload(self): pass # pure virtual

  def setVisible(self, value):
    super(WebDialog, self).setVisible(value)
    if not value: # save memory
      self.clear()

class UserView(WebDialog):
  def __init__(self, parent=None):
    super(UserView, self).__init__(parent)
    self.setWindowIcon(rc.icon('window-user'))
    self.userId = 0
    self.userHash = 0
    self.userName = ''

  def onReload(self):
    """@reimp"""
    dm = dataman.manager()
    user =  dm.queryUser(id=self.userId, name=self.userName)
    if not user:
      growl.notify(my.tr("Unknown user. Please try updating the database."))
      return
    self.userId = user.id
    self.userName = user.name
    av = dm.queryUserAvatarUrl(self.userId, hash=self.userHash, cache=True)
    self.setHtml(rc.haml_template('haml/reader/userview').render({
      'user': user,
      'avatar': av,
      'i18n': i18n,
      'rc': rc,
      'tr': tr_,
      'mytr': mytr_,
    }))

  def refresh(self): self.onReload()

  def setUserId(self, v): self.userId = v
  def setUserName(self, v): self.userName = v
  def setUserHash(self, v): self.userHash = v

  def setVisible(self, value):
    """@reimp @public"""
    if value and not self.isVisible():
      self.refresh()
    super(UserView, self).setVisible(value)

class _UserViewManager:
  def __init__(self):
    self.dialogs = []

  @staticmethod
  def _createDialog():
    import windows
    parent = windows.top()
    ret = UserView(parent)
    ret.resize(400, 270)
    return ret

  def getDialog(self):
    for w in self.dialogs:
      if not w.isVisible():
        return w
    ret = self._createDialog()
    self.dialogs.append(ret)
    return ret

class UserViewManager:
  def __init__(self):
    self.__d = _UserViewManager()

  #def clear(self): self.hide()

  def hide(self):
    if self.__d.dialogs:
      for w in self.__d.dialogs:
        if w.isVisible():
          w.hide()

  def showUser(self, id=0, hash=0, name=''):
    """
    @param* id  long  user id
    @param* hash  long  ip hash
    @param* name  unicode  name  str
    """
    if not dataman.manager().queryUser(id=id, name=name):
      growl.notify(my.tr("Unknown user. Please try updating the database."))
    else:
      w = self.__d.getDialog()
      w.setUserId(id)
      w.setUserName(name)
      w.setUserHash(hash)
      w.show()

@memoized
def manager():
  import webrc
  webrc.init()
  return UserViewManager()

#@QmlObject
#class UserViewManagerProxy(QtCore.QObject):
#  def __init__(self, parent=None):
#    super(UserViewManagerProxy, self).__init__(parent)
#
#  @Slot(int)
#  def showUser(self, id):
#    manager().showUser(id)
#
#  @Slot(int, int)
#  def showUserWithHash(self, id, hash):
#    manager().showUser(id, hash)

# EOF

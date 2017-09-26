# coding: utf8
# commentinput.py
# 5/28/2014 jichi

__all__ = 'CommentInputDialog',

if __name__ == '__main__':
  import sys
  sys.path.append('..')
  import debug
  debug.initenv()

from Qt5 import QtWidgets
from PySide.QtCore import Qt
from sakurakit import skqss
#from sakurakit.skclass import memoizedproperty
#from sakurakit.skdebug import dprint
from sakurakit.sktr import tr_
from mytr import mytr_

def create_label(text=""): # unicode -> QLabel
  ret = QtWidgets.QLabel()
  if text:
    ret.setText(text + ":")
  ret.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
  return ret

class CommentInputDialog(QtWidgets.QDialog):

  def __init__(self, parent=None):
    super(CommentInputDialog, self).__init__(parent)
    skqss.class_(self, 'texture')
    self.setWindowTitle(mytr_("Update reason"))
    #self.setWindowIcon(rc.icon('window-shortcuts'))
    self.__d = _CommentInputDialog(self)
    #self.resize(300, 250)
    #self.statusBar() # show status bar

  #def __del__(self):
  #  """@reimp"""
  #  dprint("pass")

  def text(self): return self.__d.edit.text()
  def setText(self, v): self.__d.edit.setText(v)

  def type(self): # -> str
    return (
        'updateComment' if self.__d.updateCommentButton.isChecked() else
        'comment' if self.__d.commentButton.isChecked() else
        '')

  def method(self): # -> str
    return (
        'append' if self.__d.appendButton.isChecked() else
        'overwrite' if self.__d.overwriteButton.isChecked() else
        '')

  def get(self, default=""):
    """
    @param  parent  QWidget
    @param  default  str
    @return  bool ok, unicode comment, {type:str, append:bool}
    """
    if default:
      self.setText(default)
    r = self.exec_()
    return bool(r), self.text(), {
      'type': self.type(),
      'method': self.method(),
    }

  @classmethod
  def getComment(cls, parent=None, default=""):
    """
    @param  parent  QWidget
    @param  default  str
    @return  bool ok, unicode comment, {type:str, append:bool}
    """
    w = cls(parent)
    r = w.get(default)
    if parent:
      w.setParent(None)
    return r

#@Q_Q
class _CommentInputDialog(object):
  def __init__(self, q):
    self._createUi(q)

  def _createUi(self, q):
    self.edit = QtWidgets.QLineEdit()
    skqss.class_(self.edit, 'normal')

    grid = QtWidgets.QGridLayout()
    r = 0
    self.updateCommentButton = QtWidgets.QRadioButton(mytr_("Update reason"))
    self.updateCommentButton.setChecked(True)
    self.commentButton = QtWidgets.QRadioButton(tr_("Comment"))
    g = QtWidgets.QButtonGroup(q)
    g.addButton(self.updateCommentButton)
    g.addButton(self.commentButton)
    grid.addWidget(create_label(tr_("Property")), r, 0)
    for i,b in enumerate(g.buttons()):
      grid.addWidget(b, r, i+1)

    r += 1
    self.appendButton = QtWidgets.QRadioButton(tr_("Append"))
    self.appendButton.setChecked(True)
    self.overwriteButton = QtWidgets.QRadioButton(tr_("Overwrite"))
    g = QtWidgets.QButtonGroup(q)
    g.addButton(self.appendButton)
    g.addButton(self.overwriteButton)
    grid.addWidget(create_label(tr_("Method")), r, 0)
    for i,b in enumerate(g.buttons()):
      grid.addWidget(b, r, i+1)

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(self.edit)

    optionGroup = QtWidgets.QGroupBox(tr_("Option"))
    optionGroup.setLayout(grid)
    layout.addWidget(optionGroup)

    buttonBox = QtWidgets.QDialogButtonBox(
        QtWidgets.QDialogButtonBox.Ok|
        QtWidgets.QDialogButtonBox.Cancel)
    layout.addWidget(buttonBox)
    buttonBox.accepted.connect(q.accept)
    buttonBox.rejected.connect(q.reject)

    okButton = buttonBox.button(buttonBox.Ok)
    okButton.setDefault(True)
    skqss.class_(okButton, 'btn btn-primary')
    #cancelButton = buttonBox.button(buttonBox.Cancel)

    q.setLayout(layout)

if __name__ == '__main__':
  a = debug.app()
  r = CommentInputDialog.getComment()
  #a.exec_()

# EOF

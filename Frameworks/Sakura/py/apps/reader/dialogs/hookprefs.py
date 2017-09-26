# coding: utf8
# hookprefs.py
# 11/6/2012 jichi

from PySide.QtCore import Qt, Signal
from Qt5 import QtWidgets
from texthook import texthook
from sakurakit import skqss
from sakurakit.skclass import Q_Q
from sakurakit.skdebug import dprint
from sakurakit.sktr import tr_
from mytr import my
import growl, rc

class HookPrefsDialog(QtWidgets.QDialog):
  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(HookPrefsDialog, self).__init__(parent, WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    self.setWindowTitle(my.tr("Edit Hook Code"))
    self.setWindowIcon(rc.icon('window-hookprefs'))
    #self.setModel(True)
    self.__d = _HookPrefsDialog(self)
    self.resize(450, 400)

  hookCodeEntered = Signal(unicode)
  hookCodeDeleted = Signal()

  def setVisible(self, visible):
    """@reimp @public"""
    if visible != self.isVisible():
      self.__d.load()
    super(HookPrefsDialog, self).setVisible(visible)

  def setDeletedHook(self, text):
    """
    @param  text  unicode
    """
    self.__d.setDeletedHook(text)

  #def setHookCode(self, text):

  #def hookCode(self):
  #  return self.__d.currentHookCode() if self.__d.isComplete() else ""

@Q_Q
class _HookPrefsDialog(object):
  def __init__(self, q):
    self._hookHistory = set() # [str hcode] history
    self._createUi(q)

  def _createUi(self, q):
    introEdit = QtWidgets.QTextBrowser()
    skqss.class_(introEdit, 'texture')
    introEdit.setReadOnly(True)
    introEdit.setOpenExternalLinks(True)

    import info
    introEdit.setHtml(info.renderHookCodeHelp())

    self._hookEdit = QtWidgets.QComboBox()
    self._hookEdit.setEditable(True)
    self._hookEdit.setToolTip(my.tr("Your hook code"))
    #self._hookEdit.lineEdit().setPlaceholderText(my.tr("Type /H code here"))
    self._hookEdit.editTextChanged.connect(self._refresh)
    #self._hookEdit = QtWidgets.QLineEdit()
    #self._hookEdit.setToolTip(my.tr("Your hook code"))
    #self._hookEdit.setPlaceholderText(my.tr("Type /H code here"))
    #self._hookEdit.textChanged.connect(self._refresh)

    self._deletedHookLabel = QtWidgets.QLabel()
    skqss.class_(self._deletedHookLabel, 'text-info')
    self._deletedHookLabel.setText(tr_("Empty"))
    self._deletedHookLabel.linkActivated.connect(self._hookEdit.setEditText)

    #self._deletedHookEdit.setText("%s (%s)" %
    #    (my.tr("Deleted hook code"), tr_("Empty")))

    cancelButton = QtWidgets.QPushButton(tr_("Cancel"))
    skqss.class_(cancelButton, 'btn btn-default')
    cancelButton.setToolTip(my.tr("Discard changes"))
    cancelButton.clicked.connect(q.hide)

    self._saveButton = QtWidgets.QPushButton(tr_("Save"))
    skqss.class_(self._saveButton, 'btn btn-primary')
    self._saveButton.setToolTip(my.tr("Apply the hook code to the current game"))
    self._saveButton.setEnabled(False)
    self._saveButton.clicked.connect(self._save)

    self._deleteButton = QtWidgets.QPushButton(tr_("Delete"))
    skqss.class_(self._deleteButton, 'btn btn-danger')
    self._deleteButton.setToolTip(my.tr("Remove the hook code from the current game"))
    self._deleteButton.setEnabled(False)
    self._deleteButton.clicked.connect(self._confirmDelete)

    layout = QtWidgets.QVBoxLayout()
    layout.addWidget(introEdit)

    row = QtWidgets.QHBoxLayout()
    label = QtWidgets.QLabel(my.tr("Deleted /H code") + ": ")
    skqss.class_(label, 'text-info')
    tip = my.tr("Recent /H code for this game that is deleted by other users")
    label.setToolTip(tip)
    row.addWidget(label)
    self._deletedHookLabel.setToolTip(tip)
    row.addWidget(self._deletedHookLabel)
    row.addStretch()
    layout.addLayout(row)

    layout.addWidget(self._hookEdit)
    buttons = QtWidgets.QHBoxLayout()
    buttons.addWidget(self._deleteButton)
    buttons.addStretch()
    buttons.addWidget(cancelButton)
    buttons.addWidget(self._saveButton)
    layout.addLayout(buttons)

    layout.setContentsMargins(18, 18, 18, 9) # left, top, right, bottom
    q.setLayout(layout)

    cancelButton.setFocus()

    # Do this after setLayout, otherwise QLineEdit is None
    self._hookEdit.lineEdit().setPlaceholderText(my.tr("Type /H code here"))

  def isComplete(self):
    t = self.currentHookCode()
    return (
        len(t) > 4 and
        len(t) < 255 and
        (t.startswith("/H") or t.startswith("/h")) and
        texthook.TextHook.verifyHookCode(t))

  def _addHookToHistory(self, hcode): # str
    if hcode and hcode not in self._hookHistory:
      self._hookHistory.add(hcode)
      self._hookEdit.addItem(hcode)

  def setDeletedHook(self, hcode): # str ->
    self._addHookToHistory(hcode)
    self._deletedHookLabel.setText(tr_("Empty") if not hcode else
        '<a style="color:#428bca" href="%s">%s</a>' % (hcode, hcode)) # Same color as bootstrap 3 btn-link

  def _refresh(self):
    ok = self.isComplete()
    self._saveButton.setEnabled(ok)
    skqss.class_(self._hookEdit, 'normal' if ok else 'error')

    hooked = bool(texthook.global_().currentHookCode())
    self._deleteButton.setEnabled(hooked)

  def _confirmDelete(self):
    import prompt
    if prompt.confirmDeleteHookCode():
      self._delete()

  def _delete(self):
    #self._hookEdit.clear()
    self._hookEdit.clearEditText()
    self._refresh()
    texthook.global_().clearHookCode()
    self.q.hookCodeDeleted.emit()
    growl.msg(my.tr("User-defined hook removed!"))

  def _save(self):
    if self.isComplete():
      hcode = self.currentHookCode()
      th = texthook.global_()
      old_hcode = th.currentHookCode()
      if hcode == old_hcode:
        growl.msg(my.tr("Hook code is not changed"))
        self._saveButton.setEnabled(False)
        skqss.class_(self._hookEdit, 'normal')
      else:
        self._addHookToHistory(hcode)
        if old_hcode:
          growl.notify(my.tr("Override previous hook code") + "<br/>" + old_hcode)
        if th.setHookCode(hcode):
          #self.q.hide()
          growl.msg(my.tr("Hook code saved"))
          self._saveButton.setEnabled(False)
          skqss.class_(self._hookEdit, 'normal')
          self.q.hookCodeEntered.emit(hcode)
        else:
          growl.error(my.tr("Hook code does not work with the current game"))
          self._saveButton.setEnabled(False)
          skqss.class_(self._hookEdit, 'error')

    hooked = bool(texthook.global_().currentHookCode())
    self._deleteButton.setEnabled(hooked)
    dprint("pass")

  def currentHookCode(self): return self._hookEdit.currentText().strip()

  def load(self):
    th = texthook.global_()
    hcode = th.currentHookCode()
    self._addHookToHistory(hcode)
    #if hcode:
    self._hookEdit.setEditText(hcode)
    self._refresh()

# EOF

# coding: utf8
# help.py
# 12/25/2012 jichi

from PySide.QtCore import Qt
from Qt5.QtWidgets import QTextBrowser
from sakurakit import skqss
from sakurakit.skdebug import dprint
from sakurakit.sktr import tr_
from mytr import my, mytr_
import config, info

class HelpDialog(QTextBrowser):

  def __init__(self, parent=None):
    WINDOW_FLAGS = Qt.Dialog|Qt.WindowMinMaxButtonsHint
    super(HelpDialog, self).__init__(parent)
    self.setWindowFlags(WINDOW_FLAGS)
    skqss.class_(self, 'texture')
    #self.setWindowTitle(tr_("Help"))
    self.setReadOnly(True)
    self.setOpenExternalLinks(True)
    #dprint("pass")

class CreditsDialog(HelpDialog):

  def __init__(self, parent=None):
    super(CreditsDialog, self).__init__(parent)
    self.setWindowTitle("%s - %s" %
        (tr_("Credits"), mytr_("Visual Novel Reader")))
    self.setHtml(info.renderCredits())
    self.resize(450, 400)
    dprint("pass")

class AppHelpDialog(HelpDialog):

  def __init__(self, parent=None):
    super(AppHelpDialog, self).__init__(parent)
    self.setWindowTitle("%s - %s" %
        (tr_("Help"), mytr_("Visual Novel Reader")))
    self.setHtml(info.renderAppHelp())
    self.resize(450, 400)
    dprint("pass")

class CommentHelpDialog(HelpDialog):

  def __init__(self, parent=None):
    super(CommentHelpDialog, self).__init__(parent)
    self.setWindowTitle("%s - %s" %
        (tr_("Help"), tr_("Subtitles")))
    self.setHtml(info.renderCommentHelp())
    self.resize(500, 300)
    dprint("pass")

class ReferenceHelpDialog(HelpDialog):

  def __init__(self, parent=None):
    super(ReferenceHelpDialog, self).__init__(parent)
    self.setWindowTitle("%s - %s" %
        (tr_("Help"), mytr_("Game References")))
    self.setHtml(info.renderReferenceHelp())
    self.resize(500, 375)
    dprint("pass")

class VoiceHelpDialog(HelpDialog):

  def __init__(self, parent=None):
    super(VoiceHelpDialog, self).__init__(parent)
    self.setWindowTitle("%s - %s" %
        (tr_("Help"), mytr_("Voice Settings")))
    self.setHtml(info.renderVoiceHelp())
    self.resize(500, 400)
    dprint("pass")

class TermHelpDialog(HelpDialog):

  def __init__(self, parent=None):
    super(TermHelpDialog, self).__init__(parent)
    self.setWindowTitle("%s - %s" %
        (tr_("Help"), mytr_("Shared Dictionary")))
    self.setHtml(info.renderTermHelp())
    self.resize(500, 300)
    dprint("pass")

class TextReaderHelpDialog(HelpDialog):

  def __init__(self, parent=None):
    super(TextReaderHelpDialog, self).__init__(parent)
    self.setWindowTitle("%s - %s" %
        (tr_("Help"), mytr_("Text Reader")))
    self.setHtml(info.renderTextReaderHelp())
    self.resize(400, 260)
    dprint("pass")

class TextSettingsHelpDialog(HelpDialog):

  def __init__(self, parent=None):
    super(TextSettingsHelpDialog, self).__init__(parent)
    self.setWindowTitle("%s - %s" %
        (tr_("Help"), mytr_("Text Settings")))
    self.setHtml(info.renderTextSettingsHelp())
    self.resize(500, 400)
    dprint("pass")

class EmbeddedTextSettingsHelpDialog(HelpDialog):

  def __init__(self, parent=None):
    super(EmbeddedTextSettingsHelpDialog, self).__init__(parent)
    self.setWindowTitle("%s - %s" %
        (tr_("Help"), mytr_("Text Settings")))
    self.setHtml(info.renderEmbeddedTextSettingsHelp())
    self.resize(500, 400)
    dprint("pass")

# EOF

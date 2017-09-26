# coding: utf8
# prompt.py
# 6/4/2013 jichi

from functools import partial
from PySide.QtCore import QObject, Slot
from Qt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox
from sakurakit import skevents
from sakurakit.sktr import tr_, notr_
#from sakurakit.skqml import QmlObject
from mytr import my, mytr_
import config, growl, i18n, netman, settings #ttsman

Yes = QMessageBox.Yes
No = QMessageBox.No
Reset = QMessageBox.Reset

def _parent():
  """
  @return  QWidget  parent window
  """
  import windows
  return windows.top()

def _speak(t):
  """
  @param  t  unicode
  """
  # Disabled
  pass
  #skevents.runlater(partial(
  #    ttsman.speak, t, verbose=False))

def _defaultUpdateComment(): # -> unicode
  ret = notr_("typo")
  import dataman
  user = dataman.manager().user()
  if user.id:
    ret = "@%s: %s" % (user.name, ret)
  return ret

_LAST_UPDATE_COMMENT = ''
def getUpdateComment(default=""):
  """
  @param  default  unicode
  @return  unicode
  """
  global _LAST_UPDATE_COMMENT
  ret, ok = QInputDialog.getText(_parent(),
      my.tr("Update reason"),
      my.tr(
"""You are not the author of this entry.
Please specify the REASON for modifying other's work.
For example, you can put in "typo", "inaccurate", or "scam".
"""),
      QLineEdit.Normal,
      default or _LAST_UPDATE_COMMENT or _defaultUpdateComment())
  t = ret.strip()
  if t:
    _LAST_UPDATE_COMMENT = t
  return t if ok else ""

#def showAbout():
#  t = config.VERSION_TIMESTAMP
#  line1 = tr_("Version") + " " + i18n.timestamp2datetime(t)
#  t = settings.global_().updateTime() or config.VERSION_TIMESTAMP
#  line2 = tr_("Update") + " " + i18n.timestamp2datetime(t)
#  msg = '\n'.join((line1, line2))
#  QMessageBox.about(_parent(),
#      tr_("About {0}").format(mytr_("Visual Novel Reader")),
#      msg)

#def confirmDeleteSelection(count):
#  """
#  @param  count  int
#  @return  bool
#  """
#  return Yes == QMessageBox.question(_parent(),
#      my.tr("Confirm deletion"),
#      my.tr("Do you want to permanently delete the selected {0} items?").format(count),
#      Yes|No, No)

_LAST_DELETE_SELECTION_COMMENT = ''
def getDeleteSelectionComment(count, default=''):
  """
  @param  count  int
  @return  bool
  """
  global _LAST_DELETE_SELECTION_COMMENT
  ret, ok = QInputDialog.getText(_parent(),
      my.tr("Confirm deletion"),
      "\n".join((
        my.tr("Do you want to permanently delete the selected {0} items?").format(count),
        my.tr('Please specify the REASON for the modification, such as "typo".'),
      )),
      QLineEdit.Normal,
      default or _LAST_DELETE_SELECTION_COMMENT or _defaultUpdateComment())
  t = ret.strip()
  if t:
    _LAST_DELETE_SELECTION_COMMENT = t
  return t if ok else ""

_LAST_UPDATE_SELECTION_COMMENT = ''
def getDisableSelectionComment(count, default=''):
  """
  @param  count  int
  @return  bool
  """
  global _LAST_UPDATE_SELECTION_COMMENT
  ret, ok = QInputDialog.getText(_parent(),
      my.tr("Update reason"),
      "\n".join((
        my.tr("Do you want to disable the selected {0} items?").format(count),
        my.tr('Please specify the REASON for the modification, such as "typo".'),
      )),
      QLineEdit.Normal,
      default or _LAST_UPDATE_SELECTION_COMMENT or _defaultUpdateComment())
  t = ret.strip()
  if t:
    _LAST_UPDATE_SELECTION_COMMENT = t
  return t if ok else ""
def getEnableSelectionComment(count, default=''):
  """
  @param  count  int
  @return  bool
  """
  global _LAST_UPDATE_SELECTION_COMMENT
  ret, ok = QInputDialog.getText(_parent(),
      my.tr("Update reason"),
      "\n".join((
        my.tr("Do you want to enable the selected {0} items?").format(count),
        my.tr('Please specify the REASON for the modification, such as "typo".'),
      )),
      QLineEdit.Normal,
      default or _LAST_UPDATE_SELECTION_COMMENT or _defaultUpdateComment())
  t = ret.strip()
  if t:
    _LAST_UPDATE_SELECTION_COMMENT = t
  return t if ok else ""

def confirmQuit():
  """
  @return  bool
  """
  #_speak(u"終了しますか？")
  return Yes == QMessageBox.question(_parent(),
      mytr_("Visual Novel Reader"),
      my.tr("Quit {0}?").format(mytr_("Visual Novel Reader")),
      Yes|No, No)

def confirmRestart():
  """
  @return  bool
  """
  #_speak(u"再起動しますか？")
  return Yes == QMessageBox.question(_parent(),
      mytr_("Visual Novel Reader"),
      '\n'.join((
        my.tr("Restart {0}?").format(mytr_("Visual Novel Reader")),
        "",
        my.tr("If VNR is taking too much memory, restarting it might help reduce its memory usage."),
      )),
      Yes|No, No)

def confirmResetSettings():
  """
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      tr_("Restore default settings"),
      my.tr("Do you want to restore default settings?"),
      Yes|No, No)

def confirmDeleteGame(game):
  """
  @param  game  dataman.GameObject
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      mytr_("Visual Novel Reader"),
      "\n".join((
        my.tr("Remove this game from the dashboard?"),
        "",
        tr_("Name") + ": " + game.name,
        tr_("Location") + ": " + game.path,
      )),
      Yes|No, No)

def confirmDeleteHookCode():
  """
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      my.tr("Remove Game-specific Hook Code"),
      my.tr(
"""Do you want to delete the hook code for this game?
It is recommended that you have the Internet access now, so that VNR will delete the hook code from the online database as well.

But other users might revert your deletion later.
If the hook code appear here again, please delete it here again."""),
      Yes|No, No)

def confirmDeleteComment(comment):
  """
  @param  dataman.Comment
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      my.tr("Confirm deletion"),
      "\n".join((
        my.tr("Do you want to permanently delete this entry?"),
        "",
        tr_("Text") + ": " + comment.text,
        tr_("Context") + ": " + comment.context,
      )),
      Yes|No, No)

#def confirmDeleteSubtitle():
#  return Yes == QMessageBox.question(_parent(),
#      my.tr("Confirm deletion"),
#      my.tr("Do you want to permanently delete this subtitle?"),
#      Yes|No, No)

def confirmDuplicateEntry():
  """
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      my.tr("Clone entry"),
my.tr("""Do you want to clone other people's entry?
The entry has already been enabled even without you cloning it.
Instead, cloning will result in duplicate entries that makes it more difficult to manage."""),
      Yes|No, No)

def confirmClearEntries():
  """
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      my.tr("Confirm deletion"),
      my.tr("Do you want to permanently delete all entries?"),
      Yes|No, No)

def confirmDeleteTerm(term):
  """
  @param  dataman.Term
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      my.tr("Confirm deletion"),
      "\n".join((
        my.tr("Do you want to permanently delete this entry?"),
        "",
        tr_("Pattern") + ": " + term.pattern,
        tr_("Text") + ": " + term.text,
      )),
      Yes|No, No)

def confirmDeleteCharacter(c):
  """
  @param  dataman.Character
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      my.tr("Confirm deletion"),
      "\n".join((
        my.tr("Do you want to permanently delete this entry?"),
        "",
        tr_("Name") + ": " + (c.name or tr_("Aside")),
        tr_("Gender") + ": " + i18n.gender_name(c.gender),
      )),
      Yes|No, No)

def confirmDeleteRef(ref):
  """
  @param  dataman.Reference
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      my.tr("Confirm deletion"),
      "\n".join((
        my.tr("Do you want to permanently delete this entry?"),
        "",
        tr_("Title") + ": " + ref.title,
        tr_("Release date") + ": " + i18n.timestamp2date(ref.date),
      )),
      Yes|No, No)

def confirmUpdateRefs(game=None):
  """
  @param  game  dataman.Game or None
  @return  bool
  """
  #if not game:
  #  growl.notify(my.tr("Unknown game. Please try updating the database."))
  #  return
  if not netman.manager().isOnline():
    growl.warn(my.tr("Cannot perform update when offline"))
    return
  #_speak(u"今すぐゲーム情報を更新しますか？")

  msg = ""
  if game:
    t = game.refsUpdateTime or game.visitTime or config.VERSION_TIMESTAMP
    msg += my.tr("Game references are updated on: {0}.").format(
        i18n.timestamp2datetime(t)) + "\n"

  msg += "\n\n".join((
my.tr("VNR will automatically check for updates."),
my.tr("""Do you want to update now?
It might take a couple of seconds to complete."""),
))

  return Yes == QMessageBox.question(_parent(),
      my.tr("Update game references"),
      msg,
      Yes|No, No)

def confirmUpdateComments(game=None):
  """
  @param  game  dataman.Game or None
  @return  bool
  """
  #if not game:
  #  growl.notify(my.tr("Unknown game. Please try updating the database."))
  #  return
  if not netman.manager().isOnline():
    growl.warn(my.tr("Cannot perform update when offline"))
    return
  _speak(u"今すぐ字幕を更新しますか？")

  msg = "\n\n".join((
my.tr("VNR will automatically check for updates."),
my.tr("""Do you want to update now?
It might take a couple of seconds to complete."""),
))

  t = game.commentsUpdateTime or game.visitTime if game else 0
  if t > 0:
    msg = "\n".join((
        my.tr("Comments are updated on: {0}.").format(i18n.timestamp2datetime(t)),
        msg))
  return Yes == QMessageBox.question(_parent(),
      my.tr("Update user-contributed comments"),
      msg, Yes|No, No)

def confirmUpdateTerms():
  """
  @return  {reset=bool} or None
  """
  if not netman.manager().isOnline():
    growl.warn(my.tr("Cannot perform update when offline"))
    return
  #_speak(u"今すぐ辞書を更新しますか？")
  t = settings.global_().termsTime() or config.VERSION_TIMESTAMP
  sel = QMessageBox.question(_parent(),
      my.tr("Update user-contributed dictionary"),
      "\n\n".join((
"\n".join((my.tr("Dictionary terms for machine translation are updated on: {0}."),
           my.tr("VNR will check for automatically updates. Do you want to update now?"))),
my.tr("""
VNR will do incremental update by default.
But if you press Reset, VNR will redownload the entire data, which is slow."""),
)).format(i18n.timestamp2datetime(t)),
      Yes|No|Reset, No)
  if sel == Yes:
    return {'reset':False}
  elif sel == Reset:
    return {'reset':True}

def confirmUpdateSubs(timestamp=0):
  """
  @param* timestamp  long
  @return  {reset=bool} or None
  """
  if not netman.manager().isOnline():
    growl.warn(my.tr("Cannot perform update when offline"))
    return
  ts = i18n.timestamp2datetime(timestamp) if timestamp else tr_('empty')
  sel = QMessageBox.question(_parent(),
      my.tr("Update user-contributed subtitles"),
      "\n\n".join((
"\n".join((my.tr("Shared subtitles are updated on: {0}."),
           my.tr("VNR will check for automatically updates. Do you want to update now?"))),
my.tr("""
VNR will do incremental update by default.
But if you press Reset, VNR will redownload the entire data, which is slow."""),
)).format(ts),
      Yes|No|Reset, No)
  if sel == Yes:
    return {'reset':False}
  elif sel == Reset:
    return {'reset':True}

#def confirmUpdateTranslationScripts():
#  """
#  @return  bool
#  """
#  if not netman.manager().isOnline():
#    growl.warn(my.tr("Cannot perform update when offline"))
#    return
#  #_speak(u"今すぐ辞書を更新しますか？")
#  t = settings.global_().translationScriptTime() or config.VERSION_TIMESTAMP
#  return Yes == QMessageBox.question(_parent(),
#      my.tr("Update translation scripts on Wiki"),
#      "\n\n".join((
#my.tr("""Translation scripts are updated on: {0}.
#The scripts might enhance machine translation quality.
#VNR will check for automatically updates."""),
#my.tr("""Do you want to update now?
#It might take a couple of seconds to complete."""),
#)).format(i18n.timestamp2datetime(t)),
#      Yes|No, No)
#
#def confirmReloadTranslationScripts():
#  """
#  @return  bool
#  """
#  url = "http://sakuradite.com/wiki/en/VNR/Translation_Scripts"
#  return Yes == QMessageBox.question(_parent(),
#      my.tr("Reload offline translation scripts"),
#my.tr("""Do you want to reload the offline translation scripts?
#Most most most users don't need to do this.
#
#But if you have manually modified the local TAH script, you can reload it here.
#However, the local script will be overwritten by the online version on next update.
#You want have to merge your changes online in the following URL."""
#) + "\n\n" + url,
#      Yes|No, No)

def confirmUpdateGameFiles():
  """
  @return  bool
  """
  if not netman.manager().isOnline():
    growl.warn(my.tr("Cannot perform update when offline"))
    return
  _speak(u"今すぐゲーム情報を更新しますか？")

  t = settings.global_().gameFilesTime() or config.VERSION_TIMESTAMP
  return Yes == QMessageBox.question(_parent(),
      my.tr("Update online game database"),
      "\n\n".join((
my.tr("""Game database is updated on: {0}.
The database is used to detect new games.
VNR will automatically check for updates."""),
my.tr("""Do you want to update now?
It might take a couple of seconds to complete."""),
)).format(i18n.timestamp2datetime(t)),
      Yes|No, No)

def confirmBlockLanguage(lang):
  """
  @param  lang  str
  @return  bool
  """
  lang = i18n.language_name(lang)
  return Yes == QMessageBox.question(_parent(),
      my.tr("Block user language"),
      my.tr(
"""Are you sure to block {0}?
It is the same as your current user language.
If yes, VNR will block all settings for this language."""
).format(lang),
      Yes|No, No)

def confirmStretchGameWindow():
  """
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      my.tr("Switch to full screen"),
      my.tr(
"""Do you want to stretch the game window to full screen?
You can click the same button again to switch back.

Note: This function does not work well for all games ><"""),
      Yes|No, No)

def confirmRemoveRepeat():
  """
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      "%s: %s" % (tr_("Warning"), my.tr("Enable repetition filter")),
      my.tr(
"""Are you sure to turn on repetition filter?
You might NOT want to turn this on unless the game text is FULL OF repeats.
Few games really need this option.

This option only serves to eliminate repetition.
It has NOTHING to do with finding NEW game text.

WARNING: If the game do NOT have repetition but you turn it on,
it might significantly downgrade the translation quality.

If only some of the game text repeat while some not,
it is better to add some regular expressions to Shared Dictionary
than turning on global repetition filters here."""),
      Yes|No, No)

def confirmKeepThreads():
  """
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      "%s: %s" % (tr_("Warning"), my.tr("Keep all text threads")),
      my.tr(
"""Are you sure to keep all scenario text threads?
You might NOT want to enable this unless the ADDRESS OF TEXT
(the gray the number) varies each time you launch the game!

WARNING:
For example, if there are several threads marked as KiriKiri,
when you turn this option on, VNR will translate ALL KIRIKIRI TEXTS.
This will result in LARGE AMOUNT OF GARBAGE, which is NOT what you want!"""),
      Yes|No, No)

def confirmKeepSpace():
  """
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      "%s: %s" % (tr_("Warning"), my.tr("Insert spaces")),
      my.tr(
"""Are you sure to preserve spaces in the game text?
This might be useful for English games.

WARNING:
This might result in redundant spaces for Japanese games."""),
      Yes|No, No)

def confirmDownloadGameVideo():
  """
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      my.tr("Download YouTube video"),
      my.tr("Do you want to download the selected video to your Desktop?"),
      Yes|No, No)

def confirmDownloadGameVideos():
  """
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      my.tr("Download YouTube videos"),
      my.tr("Do you want to download all YouTube videos to your Desktop?"),
      Yes|No, No)

def confirmDownloadGameImages():
  """
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      my.tr("Save game images"),
      my.tr("Do you want to save all images to your Desktop?"),
      Yes|No, No)

def confirmExportCsv():
  """
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      my.tr("Export Excel CSV"),
      my.tr("Do you want to export the data into an Excel CSV file?"),
      Yes|No, No)

def confirmRemoveDictionary(name): # unicode
  """
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      my.tr("Remove dictionary"),
      my.tr("""Do you want to remove the {0} dictionary?
You can reinstall it later if you want.""").format(name),
      Yes|No, No)

def confirmDownloadFont(name): # unicode
  """
  @return  bool
  """
  location = "Caches/Fonts"
  return Yes == QMessageBox.question(_parent(),
      my.tr("Download font"),
      my.tr("""Do you want to download the {0}?
It requires Internet access and might take a couple of minutes.
The font will be installed to {1}.""").format(name, location),
      Yes|No, No)

def confirmDownloadDictionary(name): # unicode
  """
  @return  bool
  """
  location = "Caches/Dictionaries"
  return Yes == QMessageBox.question(_parent(),
      my.tr("Download dictionary"),
      my.tr("""Do you want to download the {0} dictionary?
It requires Internet access and might take a couple of minutes.
The dictionary will be installed to {1}.""").format(name, location),
      Yes|No, No)

def confirmCompileDictionary(name): # unicode
  """
  @return  bool
  """
  location = "Caches/Dictionaries"
  return Yes == QMessageBox.question(_parent(),
      my.tr("Compile dictionary"),
      my.tr("""Do you want to compile the {0} dictionary?
It does not require Internet access and might take a couple of seconds.
The dictionary will be installed to {1}.""").format(name, location),
      Yes|No, No)

def confirmRemoveApploc():
  """
  @return  bool
  """
  return Yes == QMessageBox.question(_parent(),
      my.tr("Remove AppLocale"),
      my.tr("""Do you want to remove AppLocale?
It requires Internet access and might take a couple of minutes.
You can reinstall it later if you have Internet access."""),
      Yes|No, No)

def confirmDownloadApploc():
  """
  @return  bool
  """
  from sakurakit import skpaths
  location = skpaths.WINDIR + r"\AppPatch"
  return Yes == QMessageBox.question(_parent(),
      my.tr("Install Microsoft AppLocale"),
      my.tr("""Do you want to install the @piaip version of Microsoft AppLocale?
It requires Internet access and might take a couple of minutes.
The program will be installed to {0}.
There is no way to change the installation location.
VNR can also uninstall it later if you want.""").format(location),
      Yes|No, No)

#def confirmTranslationSyntaxDisabled():
#  """
#  @return  bool
#  """
#  return Yes == QMessageBox.question(_parent(),
#      my.tr("Disable syntax-based translation system"),
#      my.tr("""VNR has to disable the syntax-based Japanese translation if CaboCha or UniDic is not enabled.
#Do you want to continue?"""),
#      Yes|No, No)

# QML

#@QmlObject
class PromptProxy(QObject):
  def __init__(self, parent=None):
    super(PromptProxy, self).__init__(parent)

  @Slot(result=bool)
  def confirmStretchGameWindow(self):
    return confirmStretchGameWindow()

# EOF

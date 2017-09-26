# coding: utf8
# mytr.py
# 10/8/2012 jichi

__all__ = 'my', 'mytr_'

from PySide.QtCore import QObject
from sakurakit.skclass import memoized

#import os
#LOCATION = os.path.dirname(__file__) + '/tr'
#TRANSLATIONS = frozenset(('ja_JP', 'zh_TW', 'zh_CN'))

# The class name must be same as reader.js
class reader(QObject):

  # Dummy translations to fool pyside-lupdate
  def translations(self):
    return (
      # Windows
      self.tr("Visual Novel Reader"),
      self.tr("Web Browser"),
      self.tr("Spring Board"),
      self.tr("Game Board"),
      self.tr("Subtitle Maker"), self.tr("Subtitle maker"),
      self.tr("Subtitle Editor"), self.tr("Subtitle editor"),
      self.tr("Post Editor"),
      self.tr("Topic Editor"),
      self.tr("New Post"),
      self.tr("New Topic"),
      self.tr("Game Settings"),
      self.tr("Game Finder"),
      self.tr("Game References"),
      self.tr("Game Properties"),
      self.tr("Text Settings"),
      self.tr("Voice Settings"),
      self.tr("Game Wizard"),
      self.tr("Shared Dictionary"),
      self.tr("Japanese Dictionary"),
      self.tr("Text Reader"),

      self.tr("Translator"),

      self.tr("Embeddable"),
      self.tr("embeddable"),

      self.tr("YouTube Downloader"),
      self.tr("Download YouTube Videos"), self.tr("Download YouTube videos"),

      self.tr("Test Regular Expression"), self.tr("Test regular expression"),
      self.tr("Test BBCode"), #self.tr("Test BBCode"),
      self.tr("Test Machine Translation"), self.tr("Test machine translation"),
      self.tr("Test Speech Recognition"), self.tr("Test speech recognition"),
      self.tr("Test Japanese Syntax Tree"), self.tr("Test Japanese syntax tree"),
      self.tr("Test Japanese Syntax"),
      self.tr("Japanese Syntax Tree"),

      self.tr("Note"),
      self.tr("Replay"),

      self.tr("Reset Settings"),

      # Messages

      self.tr("Unknown game"),

      # Articles
      self.tr("ctx"),

      self.tr("H-code"),

      self.tr("FS"),

      self.tr("Game engine"),

      self.tr("with tone"),
      self.tr("without tone"),

      self.tr("Recordings"),

      self.tr("Matched text"),
      self.tr("Replaced text"),

      self.tr("Game text"), self.tr("game text"),
      self.tr("Machine translation"), self.tr("machine translation"),
      self.tr("Character name"), self.tr("character name"),
      self.tr("Community subtitle"),
      self.tr("User comment"),
      self.tr("User danmaku"),

      self.tr("New"),

      self.tr("C/K Ruby"),

      self.tr("Taiwan Standard Chinese"),
      self.tr("Hong Kong Traditional Chinese"),
      self.tr("Japanese Kanji"),
      self.tr("Korean Hanja"),

      #self.tr("Original text"), self.tr("original text"),
      self.tr("Voice"),
      self.tr("Speech"),
      self.tr("Speak"),
      self.tr("Text-to-speech"), self.tr("Text-To-Speech"),

      self.tr("Embedded"),
      self.tr("Embed translation"),

      self.tr("User-defined"),

      self.tr("Context count"),
      self.tr("Previous context"),

      self.tr("Scenario"), self.tr("scenario"),
      self.tr("Character"), self.tr("character"),

      self.tr("Dialog"), self.tr("dialog"),
      #self.tr("Chara"), self.tr("chara"),

      self.tr('Moderate anonymous subs'),
      self.tr('Moderate anonymous terms'),

      self.tr('Message'),
      self.tr('Messages'),
      self.tr('Discuss'),
      self.tr('Discussion'),
      self.tr('Game Discussion'),

      self.tr('Hanazono font'),

      self.tr('Overall'),
      self.tr('Ecchi'),
      self.tr('Easy'),

      self.tr('Ruby'),

      #self.tr("ATLAS"),
      self.tr("Baidu"),
      self.tr("Youdao"),
      self.tr("Infoseek"),
      self.tr("Excite"),
      #self.tr("nifty"),
      #self.tr("SYSTRAN"),
      #self.tr("Babylon"),
      self.tr("Yahoo!"),
      self.tr("Bing"),
      self.tr("Google"),
      #self.tr("LEC"),
      self.tr("LEC Online"),
      #self.tr("Translate.Ru"),
      #self.tr("ezTrans XP"),
      self.tr("Kojien"),
      self.tr("Daijirin"),
      self.tr("Daijisen"),
      self.tr("Wadoku"),
      self.tr("Zhongri"),
      self.tr("JBeijing"),
      self.tr("JBeijing7"),
      #self.tr("Dr.eye"),
      #self.tr("Han Viet"),
      self.tr("FastAIT"),
      self.tr("Kingsoft"),
      self.tr("Kingsoft FastAIT"),

      self.tr("Built-in"),
      self.tr("built-in"),

      self.tr("Romanize"),

      self.tr("Shortcuts"),

      self.tr("Multilingual"), self.tr("multilingual"),

      self.tr("Need to install"),
      self.tr("need to install"),

      self.tr("Installing"),
      self.tr("Installed"),
      self.tr("Not installed"), self.tr("not installed"),

      self.tr("Launcher"),

      self.tr("Game language"),
      self.tr("Text thread"),
      self.tr("Text threads"),
      self.tr("Hook code"),

      self.tr("Update reason"),
      self.tr("Update comment"),

      self.tr("Fill color"),
      self.tr("Background shadow"),

      self.tr("Text color"),

      self.tr("Sub"),
      self.tr("Info"),

      self.tr("Transp"),

      # Terms
      self.tr("Name"), self.tr("name"), # used in Text Settings
      self.tr("Names"), self.tr("names"),
      self.tr("Yomigana"),
      self.tr("Yomi"),
      self.tr("Suffix"),
      self.tr("Prefix"),
      self.tr("Boundary"),

      self.tr("TTS"),
      self.tr("OCR"),
      self.tr("ASR"),

      self.tr("Input"),
      self.tr("Output"),

      #self.tr("Background shadow color"),
      #self.tr("Game text color"),
      #self.tr("Machine translation color"),
      #self.tr("Community subtitle color"),
      #self.tr("User comment color"),
      #self.tr("User danmaku color"),

      self.tr("Game-specific"),
      self.tr("Series-specific"),
      self.tr("Current game"),

      self.tr("{0} games"),

      self.tr("{0} people are viewing this page"),

      # Actions

      #self.tr("Stretch"),

      #self.tr("Show {0}"),
      #self.tr("Hide {0}"),
      self.tr("Speak {0}"),

      self.tr("Capture"),

      #self.tr("Recognition"),
      self.tr("Optical character recognition"),

      self.tr("Automatic speech recognition"),
      self.tr("Speech recognition"),
      self.tr("Speech Recognition"),

      self.tr("Open in external browser"),
      self.tr("Open in external window"),

      self.tr("Monitor mouse"),
      self.tr("Monitor clipboard"),

      self.tr("Auto Hide"),
      self.tr("Edit Subtitle"),
      self.tr("New comment"),
      self.tr("New subtitle"),
      self.tr("Add comment"), self.tr("add comment"),
      self.tr("Add subtitle"), self.tr("add subtitle"),

      self.tr("Read Sentence"),

      self.tr("Sync with Running Game"),
      self.tr("Update Shared Dictionary"),
      self.tr("Update Subtitles"),
      self.tr("Update Danmaku"),
      self.tr("Update Game Database"),
      self.tr("Update Translation Scripts"),
      self.tr("Reload Translation Scripts"),
    )

@memoized
def manager(): return reader()

def mytr_(text): return manager().tr(text)

class my(QObject): pass
my = my()

# EOF

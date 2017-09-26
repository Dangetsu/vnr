# coding: utf8
# qmlplugin.py
# 10/7/2012 jichi
#
# Categorization of QML plugins
# - Standalone: should be avoid!
# - Associative
#   - Proxy: QML => (invoke) => Python
#   - Delegate: QML <= (invoke) <= Python
#
# Note: This file has reached 50 limits of qml plugins.
# I have to disable existing plugins before adding new one.
# This can be done by merging plugin manager with main plugin
#
# No more plugins can be added.

from Qt5.QtQml import qmlRegisterType
import features

QML_EFFECT = 'QtEffects'
QML_PLUGIN = 'org.sakuradite.reader'

def reg(cls, name, ns=QML_PLUGIN):
  """
  @param  cls  class
  @param  name  str
  @param* ns  str
  """
  qmlRegisterType(cls, ns, 1, 0, name)

# See: http://stackoverflow.com/questions/8894244/qml-and-blurring-image
from Qt5 import QtWidgets
#reg(QtWidgets.QGraphicsBlurEffect, 'Blur', QML_EFFECT)
#reg(QtWidgets.QGraphicsColorizeEffect, 'Colorize', QML_EFFECT)
#reg(QtWidgets.QGraphicsOpacityEffect, 'Opacity', QML_EFFECT)
reg(QtWidgets.QGraphicsDropShadowEffect, 'DropShadow', QML_EFFECT)

from sakurakit import skqml
reg(skqml.SkDesktopProxy, 'DesktopProxy')
reg(skqml.SkClipboardProxy, 'ClipboardProxy')

from qmlwidgets import qmlspinner
#reg(qmlgradient.QmlLinearGradient, 'LinearGradient')
reg(qmlspinner.QmlGradientSpinner,'GradientSpinner')

#from sakuradite import skqmlnet
#reg(skqmlnet.QmlAjax, 'Ajax')

import main
reg(main.MainObjectProxy, 'MainObjectProxy')

import trman
reg(trman.TranslatorQmlBean, 'TranslatorBean')

import ttsman
reg(ttsman.TtsQmlBean, 'Tts')

import srman
reg(srman.SpeechRecognitionBean, 'SpeechRecognition')

import settings
reg(settings.SettingsProxy, 'Settings')

import qmlutil
reg(qmlutil.QmlUtil, 'Util')
reg(qmlutil.JlpUtil, 'JlpUtil')
reg(qmlutil.TextUtil, 'TextUtil')
reg(qmlutil.BBCodeParser, 'BBCodeParser')

#import qmlbeans
#reg(qmlbeans.SliderBean, 'SliderBean')

import spell
reg(spell.SpellChecker, 'SpellChecker')

# Temporarily disabled
#import mecabman
#reg(mecabman.QmlMeCabHighlighter, 'MeCabHighlighter')

import status
reg(status.SystemStatus, 'SystemStatus')
reg(status.ThreadPoolStatus, 'ThreadPoolStatus')

import kagami
reg(kagami.KagamiBean, 'KagamiBean')
reg(kagami.GospelBean, 'GospelBean')
reg(kagami.GossipBean, 'GossipBean')
reg(kagami.GrimoireBean, 'GrimoireBean')
reg(kagami.OmajinaiBean, 'OmajinaiBean')
reg(kagami.OcrPopupBean, 'OcrPopupBean')
reg(kagami.OcrRegionBean, 'OcrRegionBean')
reg(kagami.MirageBean, 'MirageBean')

import growl
reg(growl.GrowlBean, 'GrowlBean')
reg(growl.GrowlQmlProxy, 'Growl')

import shiori
reg(shiori.ShioriBean, 'ShioriBean')
reg(shiori.ShioriQmlProxy, 'ShioriProxy')

import termview
reg(termview.TermViewBean, 'TermViewBean')

#import ocrman
#reg(ocrman.OcrQmlBean, 'OcrBean')

import submaker
reg(submaker.GraffitiBean, 'GraffitiBean')
reg(submaker.SubtitleContextBean, 'SubtitleContextBean')

import textman
reg(textman.TextManagerProxy, 'TextManagerProxy')

#import cometman
#reg(cometman.CometManagerProxy, 'CometManagerProxy')

import hkman
reg(hkman.HotkeyManagerProxy, 'HotkeyManagerProxy')

import dataman
reg(dataman.DataManagerProxy, 'DataManagerProxy')
reg(dataman.CommentModel, 'CommentModel')
reg(dataman.GameModel, 'GameModel')
reg(dataman.ReferenceModel, 'ReferenceModel')
reg(dataman.TermModel, 'TermModel')
reg(dataman.VoiceModel,'VoiceModel')

import gameman
reg(gameman.TaskBarProxy, 'TaskBarProxy')
reg(gameman.GameProxy, 'GameProxy')
reg(gameman.GameWindowProxy, 'GameWindowProxy')
reg(gameman.GameManagerProxy, 'GameManagerProxy')

#import subedit
#reg(subedit.SubtitleEditorManagerProxy, 'SubtitleEditorManagerProxy')

import postinput
reg(postinput.PostInputManagerBean, 'PostInputManager')
import postedit
reg(postedit.PostEditorManagerBean, 'PostEditorManager')

import gameedit
reg(gameedit.GameEditorManagerProxy, 'GameEditorManagerProxy')

#import prompt
#reg(prompt.PromptProxy, 'PromptProxy')

#import gameview
#reg(gameview.GameViewManagerProxy, 'GameViewManagerProxy')

#import userview
#reg(userview.UserViewManagerProxy, 'UserViewManagerProxy')

import refinput
reg(refinput.QmlReferenceInput, 'ReferenceInput')

if not features.WINE:
  import textspy
  reg(textspy.TextSpyProxy, 'TextSpyProxy')
  import textreader
  reg(textreader.TextReaderProxy, 'TextReaderProxy')

# EOF

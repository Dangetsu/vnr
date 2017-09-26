/** kagami.qml
 *  9/29/2012 jichi
 *  Fullscreen invisible screen.
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../imports/qmlhelper' as Helper
import '../../js/sakurakit.min.js' as Sk
import '../../js/eval.min.js' as Eval
//import '../../js/reader.min.js' as My
import 'comet' as Comet
import 'kagami' as Kagami
//import 'share' as Share

Item { id: root_
  implicitWidth: 800; implicitHeight: 600 // dummy

  // Window properties
  property string windowTitle: qsTr("Kagami")
  property bool translucent: true
  property bool fullScreen: true
  property int windowFlags: Qt.SplashScreen | Qt.FramelessWindowHint
  property bool ignoresCloseEvent: true

  // This might be flashing on Windows XP?
  //property bool windowVisible: !wine && (gameWindow_.visible || ajaxIndicator_.visible || !growl_.hidden)

  //property bool ignoresFocus: dock_.ignoresFocusChecked && gameWindow_.fullScreen
  property bool ignoresFocus:
      gameWindowTracker_.fullScreen
      && !gameWindowTracker_.stretched
      && !currentGameIsEmulator
      && !currentGameFocusEnabled
      && !settings_.kagamiFocusEnabled

  // 8/3/2014 TODO: Remove focus restriction for CIRCUS game as well
  property int currentGameId: datamanPlugin_.gameItemId // cached
  property bool currentGameIsEmulator: currentGameId > 50 && currentGameId < 60
  property bool currentGameFocusEnabled: datamanPlugin_.currentGameFocusEnabled // cached

  property bool mirageVisible: false

  property bool wine: statusPlugin_.wine // cached
  property int admin: statusPlugin_.admin // cached  xp: -1; otherwise 1 or 0
  property string userLanguage: statusPlugin_.userLanguage // cached

  function createPostComet() {
    return postCometComp_.createObject(root_)
  }

  // - Private -

  clip: true // maybe, this could save some CPU cycles when grimoire goes out of screen

  Helper.QmlHelper { id: qmlhelper_ }

  Component { id: postCometComp_
    Comet.PostDataComet {}
  }

  // cached

  property real globalZoomFactor: 1.0
  function updateGlobalZoomFactor() {
    var factor = Math.max(0.6, Math.sqrt( // Reduce zoom factor
        gameWindow_.getZoomFactor())) // At most zoom 0.5
    var per = Math.round(factor * 100) + "%"
    growl_.showMessage(Sk.tr("Zoom") + ' ' + per)
    globalZoomFactor = factor
  }

  Behavior on globalZoomFactor { NumberAnimation {} }

  Timer { id: zoomFactorTimer_
    interval: 1600 // different from full screen notification timeout 1500
    repeat: false
    onTriggered: updateGlobalZoomFactor()
  }

  function updateZoomFactorLater() { zoomFactorTimer_.restart() }

  Plugin.TaskBarProxy { id: taskBar_
    Component.onCompleted: root_.taskBarNeedsAutoHide = !autoHide
  }
  //property int taskBarHeight: taskBar_.visible ? taskBar_.height : 0 // cached
  property bool taskBarNeedsAutoHide: false
  property int taskBarHeight: !taskBarNeedsAutoHide ? 0 // cached
      : root_.wine ? 65 : taskBar_.height

  // Update grimoire when screen resolution changed
  //onIgnoresFocusChanged: grimoire_.updatePadding()

  Component.onCompleted: {
    //console.log("kagami.qml: taskbar height =", taskBar_.height)
    initEvalContext()
    loadSettings()
    qApp.aboutToQuit.connect(saveSettings)

    console.log("kagami.qml: pass")
  }

  Component.onDestruction: {
    console.log("kagami.qml:destroy: pass")
  }

  function initEvalContext() {
    var ctx = Eval.scriptContext
    ctx.main = mainPlugin_
    ctx.growl = growl_
    //ctx.clipboard = clipboardPlugin_
  }

  function loadSettings() {
    grimoire_.zoomFactor = settings_.grimoireZoomFactor
    ocrPopup_.zoomFactor = settings_.ocrZoomFactor
    shiori_.zoomFactor = settings_.shioriZoomFactor
    shiori_.defaultWidth = settings_.shioriWidth

    grimoire_.widthFactor = settings_.grimoireWidthFactor

    dock_.growlChecked = settings_.growlEnabled

    //dock_.windowHookChecked = settings_.windowHookEnabled
    //dock_.windowTextChecked = settings_.windowTextVisible

    dock_.autoHide = settings_.grimoireAutoHideDock
    dock_.speaksTextChecked = settings_.speaksGameText && !settings_.subtitleVoiceEnabled
    dock_.speaksTranslationChecked = settings_.speaksGameText && settings_.subtitleVoiceEnabled

    dock_.copiesTextChecked = settings_.copiesGameText
    dock_.copiesSubtitleChecked = settings_.copiesGameSubtitle
    //dock_.voiceChecked = settings_.voiceCharacterEnabled
    //dock_.subtitleVoiceChecked = settings_.subtitleVoiceEnabled

    clock_.x = Math.min(settings_.kagamiClockX, root_.width - clock_.width)
    clock_.y = Math.min(settings_.kagamiClockY, root_.height - clock_.height)

    dock_.clockChecked = settings_.kagamiClockEnabled

    dock_.hotkeyChecked = settings_.hotkeyEnabled

    dock_.hentaiChecked = settings_.hentai

    dock_.slimChecked = settings_.grimoireSlimDock
    dock_.gameTextCapacity = settings_.gameTextCapacity

    dock_.shadowOpacity = settings_.grimoireShadowOpacity
    dock_.glowIntensity = settings_.glowIntensity
    dock_.glowRadius = settings_.glowRadius

    dock_.splitsTextChecked = settings_.splitsGameText
    dock_.splitsTranslationChecked = settings_.splitsTranslation

    //dock_.shioriZoomFactor = settings_.shioriZoomFactor
    //dock_.grimoireZoomFactor = settings_.grimoireZoomFactor
    dock_.alignCenterChecked = settings_.grimoireAlignCenter
    dock_.textChecked = settings_.grimoireTextVisible
    dock_.nameChecked = settings_.grimoireNameVisible
    dock_.translationChecked = settings_.grimoireTranslationVisible
    dock_.subtitleChecked = settings_.grimoireSubtitleVisible
    dock_.commentChecked = settings_.grimoireCommentVisible
    dock_.danmakuChecked = settings_.grimoireDanmakuVisible
    //dock_.popupChecked = settings_.grimoirePopupEnabled
    dock_.hoverChecked = settings_.grimoireHoverEnabled
    //dock_.copyChecked = settings_.grimoireCopyEnabled
    //dock_.furiganaChecked = settings_.grimoireFuriganaEnabled
    dock_.shadowChecked = settings_.grimoireShadowEnabled
    //dock_.revertsColorChecked = settings_.grimoireRevertsColor
    //dock_.gameBorderChecked = settings_.gameBorderVisible
    //graffitiDock_.textChecked = settings_.graffitiTextVisible
    //graffitiDock_.translationChecked = settings_.graffitiTranslationVisible
    //graffitiDock_.subtitleChecked = settings_.graffitiSubtitleVisible
    //graffitiDock_.commentChecked = settings_.graffitiCommentVisible
    //graffitiDock_.checkedAlignment = settings_.graffitiPosition

    //dock_.ignoresFocusChecked = settings_.kagamiIgnoresFocus
    console.log("kagami.qml:loadSettings: pass")
  }

  function saveSettings() {
    settings_.grimoireZoomFactor = grimoire_.zoomFactor
    settings_.ocrZoomFactor = ocrPopup_.zoomFactor
    settings_.shioriZoomFactor = shiori_.zoomFactor
    settings_.shioriWidth = shiori_.defaultWidth

    settings_.grimoireWidthFactor = grimoire_.widthFactor

    settings_.glowIntensity = dock_.glowIntensity
    settings_.glowRadius = dock_.glowRadius

    settings_.grimoireAutoHideDock = dock_.autoHide
    //settings_.gameTextCapacity = dock_.gameTextCapacity

    settings_.hotkeyEnabled = dock_.hotkeyChecked

    settings_.kagamiClockEnabled = dock_.clockChecked
    settings_.kagamiClockX = clock_.x
    settings_.kagamiClockY = clock_.y

    settings_.splitsGameText = dock_.splitsTextChecked
    settings_.splitsTranslation = dock_.splitsTranslationChecked

    //settings_.copiesGameText = dock_.copiesTextChecked
    //settings_.shioriZoomFactor = dock_.shioriZoomFactor
    //settings_.grimoireZoomFactor = dock_.grimoireZoomFactor
    settings_.grimoireSlimDock = dock_.slimChecked
    settings_.grimoireShadowOpacity = dock_.shadowOpacity
    settings_.grimoireAlignCenter = dock_.alignCenterChecked

    //settings_.grimoireTextVisible = dock_.textChecked
    //settings_.grimoireNameVisible = dock_.nameChecked
    //settings_.grimoireTranslationVisible = dock_.translationChecked
    //settings_.grimoireSubtitleVisible = dock_.subtitleChecked
    //settings_.grimoireCommentVisible = dock_.commentChecked
    //settings_.grimoireDanmakuVisible = dock_.danmakuChecked

    //settings_.grimoirePopupEnabled = dock_.popupChecked
    settings_.grimoireHoverEnabled = dock_.hoverChecked
    //settings_.grimoireCopyEnabled = dock_.copyChecked
    //settings_.grimoireFuriganaEnabled = dock_.furiganaChecked
    settings_.grimoireShadowEnabled = dock_.shadowChecked
    //settings_.grimoireRevertsColor = dock_.revertsColorChecked
    //settings_.gameBorderVisible = dock_.gameBorderChecked
    //settings_.graffitiTextVisible = graffitiDock_.textChecked
    //settings_.graffitiTranslationVisible = graffitiDock_.translationChecked
    //settings_.graffitiSubtitleVisible = graffitiDock_.subtitleChecked
    //settings_.graffitiCommentVisible = graffitiDock_.commentChecked
    //settings_.graffitiPosition = graffitiDock_.checkedAlignment

    //settings_.kagamiIgnoresFocus = dock_.ignoresFocusChecked
    //settings_.sync()
    console.log("kagami.qml:saveSettings: pass")
  }

  Plugin.Settings { id: settings_
    // double-bound
    //onVoiceCharacterEnabledChanged:
    //  if (dock_.voiceChecked !== voiceCharacterEnabled)
    //    dock_.voiceChecked = voiceCharacterEnabled
    onHentaiChanged: if (dock_.hentaiChecked !== hentai) dock_.hentaiChecked = hentai
    onGrowlEnabledChanged: if (dock_.growlChecked !== growlEnabled) dock_.growlChecked = growlEnabled

    onSpeaksGameTextChanged: {
      var t = speaksGameText && !subtitleVoiceEnabled
      if (t != dock_.speaksTextChecked)
        dock_.speaksTextChecked = t
      t = settings_.speaksGameText && settings_.subtitleVoiceEnabled
      if (t != dock_.speaksTranslationChecked)
        dock_.speaksTranslationChecked = t
    }
  }

  //Plugin.SystemStatus { id: statusPlugin_
  //  //onOnlineChanged: gossip_.avatarVisible = online
  //}

  Plugin.KagamiBean { //id: kagami_
    onOcrToggled: dock_.toggleOcrRegionEnabled()
  }

  Plugin.MainObjectProxy { id: mainPlugin_
    windowRefreshInterval: ignoresFocus ? 1000 : 10000 // 1 sec, 10 sec
  }

  Plugin.DataManagerProxy { id: datamanPlugin_ }

  //Plugin.GameManagerProxy { id: gamemanPlugin_ }

  Plugin.TranslatorBean { id: trPlugin_ }

  Plugin.SystemStatus { id: statusPlugin_ }

  //Plugin.TextUtil { id: textPlugin_ }

  Comet.GlobalComet { id: globalComet_ }

  Comet.GameComet { id: gameComet_
    gameId: datamanPlugin_.gameItemId
    active: gameId > 0 && gameWindow_.active && statusPlugin_.online
  }

  Plugin.TextManagerProxy { id: textmanPlugin_
    //enabled: dock_.visibleChecked
    onEnabledChanged:
      if (dock_.visibleChecked !== enabled)
        dock_.visibleChecked = enabled
  }

  Plugin.HotkeyManagerProxy { id: hotkeyPlugin_
    enabled: dock_.hotkeyChecked && gamePanel_.visible
  }

  Plugin.BBCodeParser { id: bbcodePlugin_ }

  //Plugin.SubtitleEditorManagerProxy { id: subeditPlugin_ }
  //Plugin.UserViewManagerProxy { id: userViewPlugin_ }

  Plugin.ClipboardProxy { id: clipboardPlugin_ }
  Plugin.Tts { id: ttsPlugin_ }
  Plugin.SpeechRecognition { id: srPlugin_ }

  Plugin.GameProxy { id: gamePlugin_ }

  Plugin.GameWindowProxy { id: gameWindow_

    //onWindowStateChanged:
    //  dock_.show()

    onMinimizedChanged:
      //console.log("kagami.qml:gamewindowproxy: minimized =", minimized)
      if (!minimized)
        grimoire_.scrollEnd()
        //dock_.show() // already implemented when visible changed

    //onWindowClosed:
    //  shiori_.hideNow()

    onStretchedChanged:
      if (stretched !== dock_.windowStretchedChecked)
        dock_.windowStretchedChecked = stretched
      //root_.updateZoomFactorLater()

    onDisplayStretchedChanged: {
      if (displayStretched !== dock_.displayStretchedChecked)
        dock_.displayStretchedChecked = displayStretched
      root_.updateZoomFactorLater()
    }

    onKeepsDisplayRatioChanged:
      if (dock_.displayRatioChecked !== keepsDisplayRatio)
        dock_.displayRatioChecked = keepsDisplayRatio

    onFullScreenChanged: {
      if (fullScreen)
        grimoire_.ensureVisible()
      root_.updateZoomFactorLater()
      grimoire_.scrollEnd()
      //dock_.show() // This is too dangerous to enable, which might crash VNR
    }
  }

  Plugin.DesktopProxy { id: desktop_ }
  Item { id: container_
    anchors {
      left: parent.left
      top: parent.top
    }
    width: Math.min(parent.width, desktop_.width || parent.width)
    height: Math.min(parent.height, desktop_.height || parent.height)

    clip: true // maybe, this could save some CPU cycles when grimoire goes out of screen

    Item { id: gamePanel_
      anchors.fill: parent

      visible: gameWindow_.visible && !gameWindow_.minimized

      onVisibleChanged: {
        if (visible)
          dock_.show()
        console.log("kagami.qml: visible = " + visible)
      }

      // 4 paddings surrounding the center
      property int paddingMargin: -gameWindowTracker_.borderWidth - 5 //(dock_.displayStretchedChecked ? 2 : 0)
      property int paddingTopMargin: -gameWindowTracker_.titleBarHeight - (dock_.displayStretchedChecked ? 2 : 0)
      //property int paddingBottomMargin: -gameWindowTracker_.borderWidth - (dock_.displayStretchedChecked ? 4 : 0)

      //property bool paddingVisible: gameWindowTracker_.stretched
      property bool paddingVisible: false
      onPaddingVisibleChanged:
        if (paddingVisible !== dock_.paddingChecked)
          dock_.paddingChecked = paddingVisible

      Rectangle { // Top
        anchors {
          left: parent.left; right: parent.right
          top: parent.top
          bottom: gameWindowTracker_.top
          bottomMargin: parent.paddingTopMargin
        }
        color: 'black'
        //visible: gameWindowTracker_.stretched
        visible: gamePanel_.paddingVisible
        Desktop.TooltipArea {
          anchors.fill: parent
          text: qsTr("VNR's top padding")
        }
      }

      Rectangle { // Bottom
        anchors {
          left: parent.left; right: parent.right
          bottom: parent.bottom
          top: gameWindowTracker_.bottom
          topMargin: parent.paddingMargin
        }
        color: 'black'
        //visible: gameWindowTracker_.stretched
        visible: gamePanel_.paddingVisible
        Desktop.TooltipArea {
          anchors.fill: parent
          text: qsTr("VNR's bottom padding")
        }
      }

      Rectangle { // Left
        anchors {
          left: parent.left
          right: gameWindowTracker_.left
          top: gameWindowTracker_.top; bottom: gameWindowTracker_.bottom
          rightMargin: parent.paddingMargin
        }
        color: 'black'
        //visible: gameWindowTracker_.stretched
        visible: gamePanel_.paddingVisible
        Desktop.TooltipArea {
          anchors.fill: parent
          text: qsTr("VNR's left padding")
        }
      }

      Rectangle { // Right
        anchors {
          right: parent.right
          left: gameWindowTracker_.right
          top: gameWindowTracker_.top; bottom: gameWindowTracker_.bottom
          leftMargin: parent.paddingMargin
        }
        color: 'black'
        //visible: gameWindowTracker_.stretched
        visible: gamePanel_.paddingVisible
        Desktop.TooltipArea {
          anchors.fill: parent
          text: qsTr("VNR's right padding")
        }
      }

      // Cached gameproxy geometry
      //Kagami.CentralArea { id: gameWindowTracker_
      Item { id: gameWindowTracker_ // invisible game window tracker to cache game window properties that are expensive
        visible: false

        // Fix the slow changes when minimized
        //x: gameWindow_.x; y: gameWindow_.y

        property bool tracking: gameWindow_.visible && !gameWindow_.minimized
        x: tracking ? gameWindow_.x : 0
        y: tracking ? gameWindow_.y : 0

        height: gameWindow_.height; width: gameWindow_.width

        // velocity: unit per second, default 200
        Behavior on x { SmoothedAnimation { velocity: 640 } }
        Behavior on y { SmoothedAnimation { velocity: 480 } }

        property int contentWidth: gameWindow_.contentWidth // cached
        property int contentHeight: gameWindow_.contentHeight // cached

        property int borderWidth: Math.max(0, Math.min(3, (width - contentWidth)/2))
        property int titleBarHeight: Math.max(0, height - contentHeight - borderWidth)

        //borderVisible: dock_.gameBorderChecked && Qt.application.active && !root_.ignoresFocus
        //borderVisible: false
        property bool fullScreen: gameWindow_.fullScreen
        property bool stretched: dock_.stretchedChecked
        property bool fullScreenOrStretched: fullScreen || stretched

        //onStretchedChanged:
        //  gamePanel_.paddingVisible = stretched
      }

      Kagami.CommentView { //id: gossip_
        anchors {
          top: gameWindowTracker_.top; bottom: gameWindowTracker_.bottom
          left: gameWindowTracker_.left
          right: gameWindowTracker_.horizontalCenter
          margins: 20
        }

        zoomFactor: root_.globalZoomFactor

        userId: statusPlugin_.userId
        readOnly: !statusPlugin_.online

        convertsChinese: settings_.convertsChinese

        // FIXME: Why binding loop here?!
        //avatarVisible: statusPlugin_.online

        ignoresFocus: root_.ignoresFocus
        effectColor: settings_.grimoireCommentColor

        //subtitleVisible: dock_.subtitleChecked
        commentVisible: dock_.commentChecked
      }

      Kagami.Grimoire { id: grimoire_
        //anchors {
        //  fill: locked ? gameWindowTracker_ : undefined
        //  leftMargin: gameWindowTracker_.width * (1 - widthFactor) / 2
        //  rightMargin: gameWindowTracker_.width * (1 - widthFactor) / 2
        //  bottomMargin: gameWindowTracker_.height / 4
        //  topMargin: gameWindowTracker_.fullScreen ? 0 : 25
        //}
        x: (locked && !dragging) ? relativeX + gameWindowTracker_.x : x
        y: (locked && !dragging) ? relativeY + gameWindowTracker_.y : y

        //property real widthFactor
        property alias widthFactor: dock_.widthFactor

        width: gameWindowTracker_.width * widthFactor //* root_.globalZoomFactor
        height: gameWindowTracker_.height * 0.7

        //property int maxHeight: gameWindowTracker_.height * 3 / 4
        //height: maxHeight < root_.height - y ? maxHeight : root_.height - y

        toolTipEnabled: !gameWindowTracker_.fullScreenOrStretched

        //userLanguage: root_.userLanguage

        japaneseFont: settings_.japaneseFont
        englishFont: settings_.englishFont
        chineseFont: settings_.chineseFont
        //simplifiedChineseFont: settings_.simplifiedChineseFont
        koreanFont: settings_.koreanFont
        thaiFont: settings_.thaiFont
        vietnameseFont: settings_.vietnameseFont
        malaysianFont: settings_.malaysianFont
        indonesianFont: settings_.indonesianFont
        hebrewFont: settings_.hebrewFont
        bulgarianFont: settings_.bulgarianFont
        slovenianFont: settings_.slovenianFont
        tagalogFont: settings_.tagalogFont
        belarusianFont: settings_.belarusianFont
        estonianFont: settings_.estonianFont
        latvianFont: settings_.latvianFont
        lithuanianFont: settings_.lithuanianFont
        arabicFont: settings_.arabicFont
        germanFont: settings_.germanFont
        frenchFont: settings_.frenchFont
        italianFont: settings_.italianFont
        spanishFont: settings_.spanishFont
        portugueseFont: settings_.portugueseFont
        russianFont: settings_.russianFont
        polishFont: settings_.polishFont
        dutchFont: settings_.dutchFont
        czechFont: settings_.czechFont
        danishFont: settings_.danishFont
        finnishFont: settings_.finnishFont
        hungarianFont: settings_.hungarianFont
        norwegianFont: settings_.norwegianFont
        slovakFont: settings_.slovakFont
        swedishFont: settings_.swedishFont
        greekFont: settings_.greekFont
        turkishFont: settings_.turkishFont
        ukrainianFont: settings_.ukrainianFont
        romanianFont: settings_.romanianFont

        termRubyEnabled: settings_.termRubyEnabled

        rubyTextEnabled: settings_.rubyTextEnabled
        rubyTranslationEnabled: settings_.rubyTranslationEnabled

        function ensureVisible() {
          if (x < gameWindowTracker_.x || x+width/2 > gameWindowTracker_.x+gameWindowTracker_.width) {
            if (locked) relativeX = (gameWindowTracker_.width - width) / 2
            else x = gameWindowTracker_.x + (gameWindowTracker_.width - width) / 2
          }
          if (y < gameWindowTracker_.y || y+height/2 > gameWindowTracker_.y+gameWindowTracker_.height) {
            var h = gameWindowTracker_.height * 0.75
            if (locked) relativeY = h
            else y = gameWindowTracker_.y + h
          }
        }

        // Bound bottom of grimoire in fullscreen mode
        onContentHeightChanged:
          if (gameWindowTracker_.fullScreen && y+contentHeight > gameWindowTracker_.y+gameWindowTracker_.height) {
            var d = gameWindowTracker_.height - contentHeight
            if (d > gameWindowTracker_.height*0.5) { // no more than half of the screen
              if (locked) relativeY = d
              else y = gameWindowTracker_.y + d
            }
          }

        onSpeakTextRequested: textmanPlugin_.speakCurrentText()

        onSavePosRequested: grimoire_.savePosition()
        onLoadPosRequested: grimoire_.loadPosition()
        //onResetPosRequested: grimoire_.resetPosition()

        function savePosition() {
          if (gamePanel_.visible && gameWindowTracker_.width && gameWindowTracker_.height) {
            settings_.grimoireNormalizedX = (x - gameWindowTracker_.x - (gameWindowTracker_.width - width) / 2) / gameWindowTracker_.width
            settings_.grimoireNormalizedY = (y - gameWindowTracker_.y - (gameWindowTracker_.fullScreen ? 0 : 25)) / gameWindowTracker_.height

            growl_.showMessage(qsTr("Save the text box position"))
          } else
            growl_.showError(qsTr("Cannot find the game window. Is it closed?"))
        }

        function loadPosition() {
          if (gamePanel_.visible && gameWindowTracker_.width && gameWindowTracker_.height) {
            var locked_bak = locked
            locked = true
            relativeX = settings_.grimoireNormalizedX * gameWindowTracker_.width + (gameWindowTracker_.width - width) / 2
            relativeY = settings_.grimoireNormalizedY * gameWindowTracker_.height + (gameWindowTracker_.fullScreen ? 0 : 25)
            locked = locked_bak
            growl_.showMessage(qsTr("Load the text box position"))
          } else
            growl_.showError(qsTr("Cannot find the game window. Is it closed?"))
        }

        function resetPosition() {
          if (gamePanel_.visible && gameWindowTracker_.width > 0 && gameWindowTracker_.height > 0) {
            var locked_bak = locked
            locked = true
            // Top center
            relativeX = (gameWindowTracker_.width - width) / 2
            relativeY = gameWindowTracker_.titleBarHeight
            //relativeY = gameWindowTracker_.height * 0.75
            locked = locked_bak
            growl_.showMessage(qsTr("Reset the text box position"))
          } else
            growl_.showError(qsTr("Cannot find the game window. Is it closed?"))
        }

        //Timer { id: unlockTimer_ // singleShot timer
        //  interval: 10 // https://projects.kde.org/projects/kde/kdegames/kbreakout/repository/revisions/master/changes/src/qml/Singleshot.qml
        //  onTriggered: parent.locked = false
        //}

        //copiesText: dock_.copiesTextChecked
        convertsChinese: settings_.convertsChinese
        //msimeParserEnabled: settings_.msimeParserEnabled

        //outlineEnabled: dock_.outlineChecked && !shadowEnabled
        //outlineEnabled: !shadowEnabled
        //outlineEnabled: false

        //rubyJaInverted: settings_.rubyJaInverted
        rubyInverted: settings_.rubyInverted

        chineseRubyEnabled: settings_.chineseRubyEnabled
        koreanRubyEnabled: settings_.koreanRubyEnabled

        hanjaRubyEnabled: settings_.hanjaRubyEnabled
        romajaRubyEnabled: settings_.romajaRubyEnabled

        chineseRubyType: settings_.chineseRubyType

        japaneseRubyEnabled: settings_.japaneseRubyEnabled
        japaneseRubyKanaEnabled: settings_.japaneseRubyKanaEnabled
        japaneseRubyHighlight: settings_.japaneseRubyHighlight
        japaneseRubyAnnotated: settings_.japaneseRubyAnnotated
        japaneseRubyType: settings_.japaneseRubyType
        japaneseRubyInverted: settings_.japaneseRubyInverted

        //rubyType: settings_.rubyType
        //rubyDic: settings_.meCabDictionary
        //caboChaEnabled: settings_.caboChaEnabled

        removesTextNewLine: !dock_.splitsTextChecked
        splitsTranslation: dock_.splitsTranslationChecked

        alignCenter: dock_.alignCenterChecked

        glowIntensity: Math.round(dock_.glowIntensity)
        glowRadius: dock_.glowRadius

        shadowOpacity: dock_.shadowOpacity
        shadowColor: settings_.grimoireShadowColor
        fontColor: settings_.grimoireFontColor
        textColor: settings_.grimoireTextColor
        //translationColor: settings_.grimoireTranslationColor
        commentColor: settings_.grimoireSubtitleColor

        infoseekColor: settings_.infoseekColor
        exciteColor: settings_.exciteColor
        babylonColor: settings_.babylonColor
        systranColor: settings_.systranColor
        niftyColor: settings_.niftyColor
        bingColor: settings_.bingColor
        googleColor: settings_.googleColor
        naverColor: settings_.naverColor
        baiduColor: settings_.baiduColor
        youdaoColor: settings_.youdaoColor
        hanVietColor: settings_.hanVietColor
        romajiColor: settings_.romajiColor
        jbeijingColor: settings_.jbeijingColor
        vtransColor: settings_.vtransColor
        fastaitColor: settings_.fastaitColor
        dreyeColor: settings_.dreyeColor
        ezTransColor: settings_.ezTransColor
        transcatColor: settings_.transcatColor
        atlasColor: settings_.atlasColor
        lecColor: settings_.lecColor
        lecOnlineColor: settings_.lecOnlineColor
        transruColor: settings_.transruColor

        property int relativeX: settings_.grimoireNormalizedX * gameWindowTracker_.width + (gameWindowTracker_.width - width) / 2
        property int relativeY: settings_.grimoireNormalizedY * gameWindowTracker_.height + (gameWindowTracker_.fullScreen ? 0 : 25)

        onLockedChanged: keepPosotion()
        onDraggingChanged: keepPosotion()

        function keepPosotion() {
          relativeX = x - gameWindowTracker_.x
          relativeY = y - gameWindowTracker_.y
        }

        ignoresFocus: root_.ignoresFocus

        //borderVisible: dock_.borderChecked
        //locked: dock_.lockChecked

        globalZoomFactor: root_.globalZoomFactor

        minimumZoomFactor: dock_.minimumZoomFactor
        maximumZoomFactor: dock_.maximumZoomFactor
        onZoomFactorChanged:
          if (dock_.grimoireZoomFactor != zoomFactor)
            dock_.grimoireZoomFactor = zoomFactor

        //zoomFactor: dock_.grimoireZoomFactor * root_.globalZoomFactor
        //property alias widthFactor: dock_.widthFactor

        textVisible: dock_.textChecked
        nameVisible: dock_.nameChecked
        translationVisible: dock_.translationChecked
        commentVisible: dock_.subtitleChecked
        //popupEnabled: dock_.popupChecked
        hoverEnabled: dock_.hoverChecked
        //copyEnabled: dock_.copyChecked
        //hoverEnabled: dock_.hoverChecked
        shadowEnabled: dock_.shadowChecked
        //revertsColor: dock_.revertsColorChecked

        onVisibleChanged:
          if (visible !== dock_.visibleChecked)
            dock_.visibleChecked = visible

        //visible: dock_.visibleChecked
        //onVisibleChanged: {
        //  console.log("kagami.qml:grimoire: visible =", visible)
        //  if (visible)
        //    scrollEnd()
        //  //else
        //  //  repaint()
        //}

        property int minWidth: dock_.minimumWidthFactor * gameWindowTracker_.width
        property int maxWidth: dock_.maximumWidthFactor * gameWindowTracker_.width

        property int _RESIZABLE_AREA_WIDTH: 20

        MouseArea { // left draggable area
          anchors {
            top: parent.top; bottom: parent.bottom
            left: parent.left
            margins: grimoire_.shadowMargin
          }
          width: parent._RESIZABLE_AREA_WIDTH - grimoire_.shadowMargin
          acceptedButtons: Qt.LeftButton

          property int pressedX
          onPressed: pressedX = mouseX
          onPositionChanged:
            if (pressed && gameWindowTracker_.width) {
              var dx = mouseX - pressedX
              var w = grimoire_.width - dx
              if (w > grimoire_.minWidth && w < grimoire_.maxWidth) {
                grimoire_.widthFactor = w / gameWindowTracker_.width

                if (grimoire_.locked) grimoire_.relativeX += dx
                else grimoire_.x += dx
              }
            }

          Desktop.TooltipArea { //id: leftResizeTip_
            anchors.fill: parent
            text: Sk.tr("Resize")
          }
        }

        MouseArea { // right draggable area
          anchors {
            top: parent.top; bottom: parent.bottom
            right: parent.right
            margins: grimoire_.shadowMargin
          }
          width: parent._RESIZABLE_AREA_WIDTH - grimoire_.shadowMargin
          acceptedButtons: Qt.LeftButton

          property int pressedX
          onPressed: pressedX = mouseX
          onPositionChanged:
            if (pressed && gameWindowTracker_.width) {
              var dx = mouseX - pressedX
              var w = grimoire_.width + dx
              if (w > grimoire_.minWidth && w < grimoire_.maxWidth)
                grimoire_.widthFactor = w / gameWindowTracker_.width
            }

          Desktop.TooltipArea { //id: rightResizeTip_
            anchors.fill: parent
            text: Sk.tr("Resize")
          }
        }
      }

      Kagami.NoteView { //id: gospel_
        minimumX: 0; minimumY: 0
        maximumX: parent.width - width
        maximumY: parent.height - height

        globalZoomFactor: root_.globalZoomFactor

        ignoresFocus: root_.ignoresFocus
        effectColor: settings_.grimoireCommentColor

        convertsChinese: settings_.convertsChinese

        commentVisible: dock_.subtitleChecked

        property bool invisible: !visible || !opacity
        onInvisibleChanged:
          if (!invisible)
            updatePosition()

        function updatePosition() {
          x = gameWindowTracker_.x + gameWindowTracker_.width - width - 20 // margin right
          y = gameWindowTracker_.y + (gameWindowTracker_.height - height) / 2
          ensureVisible()
        }
      }

      Kagami.DanmakuView { //id: omajinai_
        anchors {
          fill: gameWindowTracker_
          //topMargin: gameWindowTracker_.fullScreen ? 0 : 25 // skip header of the window
          topMargin: 60
          rightMargin: 40
        }
        visible: dock_.danmakuChecked
        effectColor: settings_.grimoireDanmakuColor

        userId: statusPlugin_.userId
        readOnly: !statusPlugin_.online

        zoomFactor: root_.globalZoomFactor

        ignoresFocus: root_.ignoresFocus

        convertsChinese: settings_.convertsChinese

        //glowIntensity: grimoire_.glowIntensity
        //glowRadius: grimoire_.glowRadius
      }

      Kagami.OcrRegion { //id: ocrRegion_
        anchors.fill: gameWindowTracker_
        anchors.topMargin: gameWindowTracker_.fullScreen ? 0 : gameWindowTracker_.titleBarHeight // skip header of the window

        enabled: dock_.ocrRegionEnabledChecked && gamePanel_.visible && dock_.visibleChecked
        visible: dock_.ocrRegionVisibleChecked && gamePanel_.visible

        zoomFactor: root_.globalZoomFactor
        ignoresFocus: root_.ignoresFocus
        wine: root_.wine

        globalPosEnabled: dock_.ocrDesktopChecked
      }

      // Dock

      Rectangle { // left dock sensor
        anchors {
          left: gameWindowTracker_.left
          verticalCenter: gameWindowTracker_.verticalCenter
          leftMargin: -6 + Math.max(0, -gameWindowTracker_.x)
        }
        radius: 5
        width: 15
        height: gameWindowTracker_.height / 5
        color: root_.wine ? '#10000000' : '#01000000' // alpha = 1/255 is too small that do not work on wine

        MouseArea { id: dockSensorArea_
          anchors.fill: parent
          acceptedButtons: Qt.NoButton
          hoverEnabled: true
          onEntered: dock_.show()
          onExited: dock_.show()
        }
      }

      Kagami.Dock { id: dock_
        anchors {
          verticalCenter: gameWindowTracker_.verticalCenter
          //left: withinPanel ? gameWindowTracker_.left : undefined
          //right: withinPanel ? undefined : gameWindowTracker_.left
          left: gameWindowTracker_.left
          leftMargin: gameWindowTracker_.fullScreen ? 4 : Math.max(-floatingWidth + -2, -gameWindowTracker_.x)
        }

        zoomFactor: root_.globalZoomFactor

        Component.onCompleted: visible = false
        Timer { id: dockHideTimer_
          interval: 5000 // 5 seconds
          repeat: true
          onTriggered:
            if (dock_.hover) // || dockSensorArea_.containsMouse)
              //start()
              ;
            else if (dock_.autoHide)
              dock_.hide()
        }

        function show() {
          dockHideTimer_.restart()
          visible = true
        }

        ignoresFocus: root_.ignoresFocus

        //furiganaEnabled: root_.rubyEnabled

        ocrEnabled: settings_.ocrEnabled && !!root_.admin

        function toggleOcrRegionEnabled() {
          if (ocrEnabled)
            ocrRegionEnabledChecked = !ocrRegionEnabledChecked
        }

        onTextCheckedChanged: settings_.grimoireTextVisible = textChecked
        onNameCheckedChanged: settings_.grimoireNameVisible = nameChecked
        onTranslationCheckedChanged: settings_.grimoireTranslationVisible = translationChecked
        onSubtitleCheckedChanged: settings_.grimoireSubtitleVisible = subtitleChecked
        onCommentCheckedChanged: settings_.grimoireCommentVisible = commentChecked
        onDanmakuCheckedChanged: settings_.grimoireDanmakuVisible = danmakuChecked

        onGrowlCheckedChanged:
          if (settings_.growlEnabled !== growlChecked)
            settings_.growlEnabled = growlChecked

        onGameTextCapacityChanged:
          if (gameTextCapacity > 20)
            if (settings_.gameTextCapacity !== Math.round(gameTextCapacity))
              settings_.gameTextCapacity = Math.round(gameTextCapacity)

        onGrimoireZoomFactorChanged:
          if (grimoire_.zoomFactor != grimoireZoomFactor)
            grimoire_.zoomFactor = grimoireZoomFactor

        //onWindowHookCheckedChanged: settings_.windowHookEnabled = windowHookChecked
        //onWindowTextCheckedChanged: settings_.windowTextVisible = windowTextChecked

        onSpeaksTextCheckedChanged: updateTtsSettings()
        onSpeaksTranslationCheckedChanged: updateTtsSettings()

        function updateTtsSettings() {
          if (!speaksTextChecked && !speaksTranslationChecked) {
            if (settings_.speaksGameText)
              settings_.speaksGameText = false
          } else if (speaksTextChecked && !speaksTranslationChecked) {
            if (!settings_.speaksGameText)
              settings_.speaksGameText = true
            if (settings_.subtitleVoiceEnabled)
              settings_.subtitleVoiceEnabled = false
          } else if (!speaksTextChecked && speaksTranslationChecked) {
            if (!settings_.speaksGameText)
              settings_.speaksGameText = true
            if (!settings_.subtitleVoiceEnabled)
              settings_.subtitleVoiceEnabled = true
          } // else: both of them are checked, which does not make sense
        }

        onClockCheckedChanged:
          if (clockChecked !== clock_.visible)
            clock_.visible = clockChecked

        onCopiesTextCheckedChanged: settings_.copiesGameText = copiesTextChecked
        onCopiesSubtitleCheckedChanged: settings_.copiesGameSubtitle = copiesSubtitleChecked

        onHentaiCheckedChanged:
          if (settings_.hentai != hentaiChecked)
            settings_.hentai = hentaiChecked

        //onVoiceCheckedChanged: settings_.voiceCharacterEnabled = dock_.voiceChecked
        //onSubtitleVoiceCheckedChanged: settings_.subtitleVoiceEnabled = dock_.subtitleVoiceChecked

        onPaddingCheckedChanged:
          if (paddingChecked !== gamePanel_.paddingVisible)
            gamePanel_.paddingVisible = paddingChecked

        onPanelVisibleChanged: show()
        onHoverChanged: show()

        onSpeakTextRequested: textmanPlugin_.speakCurrentText()

        onCommentBarCheckedChanged:
          if (menuButton_.checked !== commentBarChecked)
            menuButton_.checked = commentBarChecked

        onGlowCheckedChanged: {
          shadowChecked = !glowChecked
          if (glowChecked) {
            glowIntensity = maximumGlowIntensity * 0.4
            glowRadius = maximumGlowRadius * 0.6
          } else { // settings default
            glowIntensity = 1 //minimumGlowIntensity
            glowRadius = 4 //minimumGlowRadius
          }

          if (gamePanel_.visible && gameWindowTracker_.width > 0 && gameWindowTracker_.height > 0) {
            var locked_bak = grimoire_.locked
            grimoire_.locked = true
            if (glowChecked) { // top left
              grimoire_.relativeX = 40
              grimoire_.relativeY = 40 + gameWindowTracker_.titleBarHeight
            } else { // top center
              grimoire_.relativeX = (gameWindowTracker_.width - grimoire_.width) / 2
              grimoire_.relativeY = gameWindowTracker_.titleBarHeight
            }
            grimoire_.locked = locked_bak
          }
        }

        //language: statusPlugin_.userLanguage === 'zhs' || statusPlugin_.userLanguage === 'zht' ? statusPlugin_.userLanguage : ''

        //alignment: root_.ignoresFocus ? Qt.AlignLeft : Qt.AlignRight
        //alignment: Qt.AlignLeft

        //onIgnoresFocusCheckedChanged:
        //  settings_.kagamiIgnoresFocus = ignoresFocusChecked

        //onUpButtonClicked: grimoire_.scrollBeginning()
        //onDownButtonClicked: grimoire_.scrollEnd()

        onResetTextPosRequested: grimoire_.resetPosition()

        onVisibleCheckedChanged: {
          if (textmanPlugin_.enabled !== visibleChecked)
            textmanPlugin_.enabled = visibleChecked
          if (visibleChecked !== grimoire_.visible) {
            if (visibleChecked)
              grimoire_.show()
            else
              grimoire_.hide()
          }
        }

        onStretchedCheckedChanged:
          if (root_.taskBarNeedsAutoHide)
            taskBar_.autoHide = stretchedChecked

        onWindowStretchedCheckedChanged:
          if (windowStretchedChecked !== gameWindow_.stretched)
            gameWindow_.stretched = windowStretchedChecked

        onDisplayStretchedCheckedChanged:
          if (displayStretchedChecked !== gameWindow_.displayStretched)
            gameWindow_.displayStretched = displayStretchedChecked

        onDisplayRatioCheckedChanged:
          if (displayRatioChecked !== gameWindow_.keepsDisplayRatio)
            gameWindow_.keepsDisplayRatio = displayRatioChecked
      }

      Kagami.CommentBar { id: commentBar_
        //anchors { // sits below gameWindowTracker_
        //  //left: gameWindowTracker_.left; right: gameWindowTracker_.right
        //  //leftMargin: 9; rightMargin: 9

        //  //top: gameWindowTracker_.fullScreen ? undefined : gameWindowTracker_.bottom
        //  //bottom: gameWindowTracker_.fullScreen ? gameWindowTracker_.bottom : undefined
        //  //bottom: gameWindowTracker_.bottom
        //  //margins: 12
        //  //bottomMargin: 12 + // avoid overlap with Windows task bar
        //  //    (graffiti_.alignment & Qt.AlignTop ? 0 : root_.taskBarHeight)
        //}

        fullScreen: gameWindowTracker_.fullScreenOrStretched

        property int relativeY: gameWindowTracker_.fullScreen ? (-8 - height) : 4
        y: Math.min(
            parent.height - height - 5 - (gameWindowTracker_.stretched ? 0 : taskBarHeight),
            gameWindowTracker_.y + gameWindowTracker_.height + relativeY)

        x: Math.max(menuButton_.width + 5, gameWindowTracker_.x) + 9

        width: Math.max(400, gameWindowTracker_.x + gameWindowTracker_.width - x - 12)
        //width: !activeFocus ? 400 : Math.max(400, gameWindowTracker_.x + gameWindowTracker_.width - x - 12)
        //Behavior on width { SmoothedAnimation { velocity: 600 } }
        //Behavior on width { SpringAnimation { velocity: 2000; spring: 5.0; damping: 0.1 } } // spring: strength; damping: speed

        //textLeftMargin: indicator_.width + 20

        //visible: indicator_.enabled && indicator_.checked && !root_.ignoresFocus
        visible: dock_.commentBarChecked && !root_.ignoresFocus
        //Component.onCompleted:
        //console.log("kagami.qml:CommentBar: binding loop warning ignored")
      }

      Kagami.MenuButton { id: menuButton_ // blue button
        anchors {
          verticalCenter: commentBar_.verticalCenter
          right: commentBar_.left
          //right: commentBar_.left
          rightMargin: 12
        }

        visible: dock_.slimChecked && !root_.ignoresFocus

        fadingEnabled: !checked && (gameWindowTracker_.stretched || gamePanel_.paddingVisible || gameWindowTracker_.fullScreen)

        //hoverEnabled: dock_.slimChecked
        //hoverEnabled: true

        onCheckedChanged:
          if (checked !== dock_.commentBarChecked)
            dock_.commentBarChecked = checked

        onClicked:
          if (enabled)
            checked = !checked
          else
            growl_.showWarning(qsTr("Not login or offline"))
      }
    }

    Kagami.OcrPopup { id: ocrPopup_
      anchors.fill: parent
      globalZoomFactor: root_.globalZoomFactor
      ignoresFocus: root_.ignoresFocus
    }

    Kagami.Growl { id: growl_
      //anchors {
      //  right: gameWindowTracker_.fullScreen ? gameWindowTracker_.right : parent.right
      //  verticalCenter: gameWindowTracker_.fullScreen ? gameWindowTracker_.verticalCenter : parent.verticalCenter
      //}

      zoomFactor: root_.globalZoomFactor

      property QtObject target: gameWindowTracker_.fullScreen ? gameWindowTracker_ : parent
      ignoresFocus: root_.ignoresFocus

      enabled: settings_.growlEnabled
      visible: enabled && dock_.growlChecked && (!gameWindowTracker_.fullScreen || dock_.visibleChecked)

      // Mac OS X menu bar height is around 22px
      // http://stackoverflow.com/questions/2867503/height-of-the-apple-menubar
      x: target.x + target.width - width - 5 // rightMargin: 5
      y: Math.max(0, target.y + (root_.wine ? 25 : 0)) // non-negative
      height: target.height
    }

    // - Top-level popups -

    Kagami.Shiori { id: shiori_
      minimumX: 0; minimumY: 0
      maximumX: parent.width - width
      maximumY: parent.height - height

      ignoresFocus: root_.ignoresFocus
      z: 999 // top most

      toolTipEnabled: !gameWindowTracker_.fullScreenOrStretched

      globalZoomFactor: root_.globalZoomFactor

      Component.onCompleted: {
        grimoire_.lookupRequested.connect(popupLookup)
        grimoire_.jsonPopupRequested.connect(popupJson)
      }
    }

    Kagami.AjaxIndicator { id: ajaxIndicator_
      anchors {
        left: parent.left
        bottom: parent.bottom
        leftMargin: 9 //dock_.stretchedChecked ? 9 : 9 + 40
        //bottomMargin: dock_.stretchedChecked ? 9 : 9 + taskBarHeight
        bottomMargin: 9 + taskBarHeight

        //leftMargin:
        //    !gamePanel_.visible ? 40 + 9 : // Considering taskbar width
        //    gameWindowTracker_.fullScreen ? 9 + gameWindowTracker_.x :
        //    2 + Math.max(0, -width/2 + gameWindowTracker_.x)

        //bottomMargin:
        //    !gamePanel_.visible ? 9 + taskBarHeight :
        //    gameWindowTracker_.fullScreen ? 9 + parent.height - gameWindowTracker_.y - gameWindowTracker_.height :
        //    2 + Math.max(0, -height/2 + parent.height - gameWindowTracker_.y - gameWindowTracker_.height)
      }
      //property int diameter: gamePanel_.visible ? 60 : 80
      //property int diameter: 80
      width: 60; height: 60

      //visible: !root_.ignoresFocus && count > 0
      visible: (!dock_.slimChecked || !gamePanel_.visible) && count > 0 && !gameWindowTracker_.fullScreenOrStretched

      //Behavior on x { SpringAnimation { spring: 3; damping: 0.3; mass: 1.0 } }
      //Behavior on y { SpringAnimation { spring: 3; damping: 0.3; mass: 1.0 } }
    }

    //Kagami.AppMenu { id: appMenu_ }

  } // end of container item

  // - Clock -

  Kagami.Clock { id: clock_
    drag {
      minimumX: 0; maximumX: root_.width - width
      minimumY: 0; maximumY: root_.height - height
    }
    zoomFactor: root_.globalZoomFactor

    onVisibleChanged:
      if (visible !== dock_.clockChecked)
        dock_.clockChecked = visible
  }

  // - Mirage -

  onMirageVisibleChanged: if (mirageVisible && !mirageComp) createMirage()

  property Component mirageComp
  function createMirage() {
    mirageComp = Qt.createComponent('textreader/mirage.qml');
    console.log("kagami.qml: createMirage: status:", mirageComp.status)
    switch (mirageComp.status) {
    case Component.Error:
      console.log("kagami.qml: ERROR: failed to create mirage component:", mirageComp.errorString());
      break
    case Component.Ready:
      onMirageCompFinished()
      break
    default:
      mirageComp.statusChanged.connect(onMirageCompFinished)
    }
    console.log("kagami.qml: createMirage: leave")
  }

  function onMirageCompFinished() {
    switch (mirageComp.status) {
    case Component.Ready:
      var mirage = mirageComp.createObject(root_, {
        x: 100
        , y: 100
        , width: 640
        , height: 480
      });
      if (mirage) {
        mirage.lookupRequested.connect(shiori_.popupLookup)
        console.log("kagami.qml: mirage created")
      } else
        console.log("kagami.qml: ERROR: failed to create mirage object")
      break
    case Component.Error:
    default:
      console.log("kagami.qml: ERROR: failed to create mirage component:", mirageComp.errorString());
    }
  }
}

// EOF

    /*
    Kagami.Graffiti { id: graffiti_
      property int alignment: graffitiDock_.checkedAlignment // Top/Bottom/Left/Right

      anchors { // anchored between central area and comment bar
        topMargin: 3; bottomMargin: 12
        // top:
        //   left: gameWindowTracker_.left; right: gameWindowTracker_.right
        //   top: parent.top; bottom: commentBar_.top
        // bottom:
        //   left: gameWindowTracker_.left; right: gameWindowTracker_.right
        //   top: gameWindowTracker_.bottom; bottom: commentBar_.top
        // left:
        //   left: parent.left; right: gameWindowTracker_.left
        //   top: parent.top; bottom: commentBar_.top
        // right:
        //   left: gameWindowTracker_.right; right: parent.right
        //   top: parent.top; bottom: commentBar_.top
        // top left:
        //   left: parent.left; right: parent.horizontalCenter
        //   top: parent.top; bottom: commentBar_.top
        // top right:
        //   left: parent.horizontalCenter; right: parent.right
        //   top: parent.top; bottom: commentBar_.top
        // bottom right:
        //   left: parent.horizontalCenter; right: parent.right
        //   top: parent.verticalCenter; bottom: commentBar_.top
        // bottom left:
        //   left: parent.left; right: parent.horizontalCenter
        //   top: parent.verticalCenter; bottom: commentBar_.top
        bottom: commentBar_.top
        left: {
          switch (alignment) {
            case Qt.AlignTop:
            case Qt.AlignBottom: return gameWindowTracker_.left
            case Qt.AlignRight: return gameWindowTracker_.right
            case Qt.AlignLeft:
            case Qt.AlignLeft|Qt.AlignTop:
            case Qt.AlignLeft|Qt.AlignBottom: return parent.left
            case Qt.AlignRight|Qt.AlignTop:
            case Qt.AlignRight|Qt.AlignBottom: return parent.horizontalCenter
            default: console.log("kagami.qml:graffiti: ERROR left anchor")
          }
        }
        right: {
          switch (alignment) {
            case Qt.AlignTop:
            case Qt.AlignBottom: return gameWindowTracker_.right
            case Qt.AlignLeft: return gameWindowTracker_.left
            case Qt.AlignRight:
            case Qt.AlignRight|Qt.AlignTop:
            case Qt.AlignRight|Qt.AlignBottom: return parent.right
            case Qt.AlignLeft|Qt.AlignTop:
            case Qt.AlignLeft|Qt.AlignBottom: return parent.horizontalCenter
            default: console.log("kagami.qml:graffiti: ERROR right anchor")
          }
        }
        top: {
          switch (alignment) {
            case Qt.AlignLeft:
            case Qt.AlignRight:
            case Qt.AlignTop:
            case Qt.AlignTop|Qt.AlignLeft:
            case Qt.AlignTop|Qt.AlignRight: return parent.top
            case Qt.AlignBottom: return gameWindowTracker_.bottom
            case Qt.AlignBottom|Qt.AlignLeft:
            case Qt.AlignBottom|Qt.AlignRight: return parent.verticalCenter
            default: console.log("kagami.qml:graffiti: ERROR top anchor")
          }
        }
      }

      userName: statusPlugin_.online ? statusPlugin_.userName : ""

      textVisible: graffitiDock_.textChecked
      translationVisible: graffitiDock_.translationChecked
      subtitleVisible: graffitiDock_.subtitleChecked
      commentVisible: graffitiDock_.commentChecked

      searchText: searchBar_.text

      Kagami.InputBar { id: searchBar_
        anchors { // sits at bottom-right corner of graffiti
          right: parent.right; bottom: parent.bottom
          margins: 10
        }
        width: editing ? Math.min(400, parent.width)
                       : Math.min(250, parent.width)
        placeholderText: qsTr("Search") + " ... (regexp)"
      }

      //Kagami.InputBar { id: prefixBar_
      //  anchors { // sits at bottom-left corner of graffiti
      //    left: parent.left; bottom: parent.bottom
      //    margins: 10
      //  }
      //  width: editing ? Math.min(400, parent.width)
      //                 : Math.min(150, parent.width)
      //  placeholderText: qsTr("Prefix") + " ..."
      //  text: "\\sub"
      //  visible: commentBar_.visible
      //}
    }

    Kagami.GraffitiDock { id: graffitiDock_
      anchors.verticalCenter: graffiti_.verticalCenter
      anchors.left: alignment === Qt.AlignLeft ? graffiti_.left : undefined
      anchors.right: alignment === Qt.AlignRight ? graffiti_.left : undefined
      alignment: Qt.AlignLeft

      onClearButtonClicked: graffiti_.clear()
      onAllButtonClicked: graffiti_.showAllComments()
      onAnalyticsButtonClicked: main_.showCommentAnalytics()
      onCreditsButtonClicked: main_.showCommentCredits()
    }
    */


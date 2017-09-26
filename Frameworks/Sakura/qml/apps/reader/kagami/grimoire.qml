/** grimoire.qml
 *  10/10/2012 jichi
 *
 *  Text order:
 *  - pageBreak
 *  - showText
 *  - showName
 *  - showTranslation
 *  - showNameTranslation
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/eval.min.js' as Eval
import '../../../js/util.min.js' as Util
import '../../../imports/qmleffects' as Effects
//import '../../../imports/qmltext' as QmlText
import '../../../imports/texscript' as TexScript
import '../../../components' as Components
import '../../../components/qt5' as Qt5
import '../share' as Share

Item { id: root_

  signal lookupRequested(string text, string language, int x, int y) // popup honyaku of text at (x, y)
  signal jsonPopupRequested(string json, int x, int y) // popup honyaku of text at (x, y)

  signal loadPosRequested
  signal savePosRequested
  //signal resetPosRequested
  signal speakTextRequested

  property int glowIntensity: 2
  property real glowRadius: 8

  //property int contourRadius: glowRadius
  //property int contourRadius: 8

  property bool alignCenter
  //property bool outlineEnabled
  property bool removesTextNewLine
  property bool splitsTranslation
  //property bool copiesText: false
  property alias locked: lockAct_.checked

  //property color fontColor //: 'snow'
  property string fontColor //: 'snow'

  property alias shadowColor: shadow_.color
  property color textColor //: '#aa007f' // dark magenta
  property color commentColor //: '#2d5f5f' // dark green

  property color translationColor: 'green'

  property bool toolTipEnabled: true

  //property string userLanguage

  property color bingColor
  property color googleColor
  property color babylonColor
  property color infoseekColor
  property color exciteColor
  property color systranColor
  property color niftyColor
  property color naverColor
  property color baiduColor
  property color youdaoColor
  property color hanVietColor
  property color jbeijingColor
  property color romajiColor
  property color vtransColor
  property color fastaitColor
  property color dreyeColor
  property color ezTransColor
  property color transcatColor
  property color atlasColor
  property color lecColor
  property color lecOnlineColor
  property color transruColor

  property string japaneseFont
  property string englishFont
  property string chineseFont
  //property string simplifiedChineseFont
  property string koreanFont
  property string thaiFont
  property string vietnameseFont
  property string malaysianFont
  property string indonesianFont
  property string hebrewFont
  property string bulgarianFont
  property string slovenianFont
  property string tagalogFont
  property string belarusianFont
  property string estonianFont
  property string latvianFont
  property string lithuanianFont
  property string arabicFont
  property string germanFont
  property string frenchFont
  property string italianFont
  property string spanishFont
  property string portugueseFont
  property string russianFont
  property string dutchFont
  property string polishFont
  property string czechFont
  property string danishFont
  property string finnishFont
  property string hungarianFont
  property string norwegianFont
  property string slovakFont
  property string swedishFont
  property string greekFont
  property string turkishFont
  property string ukrainianFont
  property string romanianFont

  property int shadowMargin: -8 // shadow_.margins

  property int contentHeight: shadow_.y + shadow_.height

  property bool dragging:
      headerMouseArea_.drag.active ||
      listTopMouseArea_.drag.active ||
      listBottomMouseArea_.drag.active ||
      !!highlightMouseArea && highlightMouseArea.drag.active
  property bool empty: !listModel_.count

  //property alias borderVisible: borderAct_.checked
  //onBorderVisibleChanged:
  //  if (_borderButton && _borderButton.checked !== borderVisible)
  //    _borderButton.checked = borderVisible

  property bool ignoresFocus: false

  property bool textVisible: true
  //onTextVisibleChanged: console.log("grimoire.qml: text visible =", textVisible)

  property bool nameVisible: true

  property bool translationVisible: true
  //onTranslationVisibleChanged: console.log("grimoire.qml: translation visible =", translationVisible)

  property bool termRubyEnabled: true

  property bool commentVisible: true
  //onCommentVisibleChanged: console.log("grimoire.qml: comment visible =", commentVisible)

  property bool popupEnabled: true
  //property bool readEnabled: true

  //property bool copyEnabled: true
  //onCopyEnabledChanged: console.log("grimoire.qml: copy enabled =", copyEnabled)

  property bool hoverEnabled: false
  //onHoverEnabledChanged: console.log("grimoire.qml: hover enabled =", hoverEnabled)

  property bool shadowEnabled: true
  //onShadowEnabledChanged: console.log("grimoire.qml: shadow enabled =", shadowEnabled)

  //property bool revertsColor: false

  property real globalZoomFactor: 1.0
  property real zoomFactor: 1.0
  property real minimumZoomFactor: 0.5
  property real maximumZoomFactor: 3.0

  property alias shadowOpacity: shadow_.opacity

  property string rubyType: 'hiragana'
  property bool rubyInverted

  property bool convertsChinese // convert Simplified Chinese to Chinese

  property bool rubyTextEnabled
  property bool rubyTranslationEnabled

  property bool chineseRubyEnabled
  property string chineseRubyType

  property bool koreanRubyEnabled
  property bool hanjaRubyEnabled
  property bool romajaRubyEnabled

  property bool japaneseRubyEnabled
  property bool japaneseRubyHighlight
  property bool japaneseRubyAnnotated
  property bool japaneseRubyKanaEnabled
  property bool japaneseRubyInverted
  property string japaneseRubyType

  function scrollBeginning() {
    listView_.positionViewAtBeginning()
    //showScrollBar()
  }
  function scrollEnd() {
    cls()
    //showScrollBar()
  }

  function show() {
    visible = true
    cls()
  }

  function hide() {
    listView_.positionViewAtEnd()
    visible = false
  }

  // - Private -

  property bool mouseLocked: false // click locked

  //function sameLanguageAsUser(lang) { // string -> bool
  //  return lang.substr(0, 2) === root_.userLanguage.substr(0, 2)
  //}

  function normalizeTtsText(text) { // string ->  string  remove HTML tags
    text = Util.removeHtmlTags(text)
    text = text.replace(/^【[^】]+】/, '') // remove character name for tts
    text = Util.removeBBCode(text)
    return text
  }

  function isRubyLanguage(lang) { // string -> bool
    switch (lang) {
    case 'ko': return root_.koreanRubyEnabled
    case 'zh': case 'zhs': case 'zht': return root_.chineseRubyEnabled
    default: return false
    }
    //if (lang.length === 3)
    //  lang = lang.substr(0, 2)
    //return !!~root_.rubyLanguages.indexOf(lang)
  }

  function renderJapanese(text, colorize) { // string, bool -> string
    return bean_.renderJapanese(text
      , root_.japaneseRubyType
      , root_.japaneseRubyKanaEnabled
      , Math.round(root_.width / (22 * root_._zoomFactor)) // * (root_.japaneseRubyInverted ? 0.85 : 1)) // char per line
      , 10 * root_._zoomFactor // ruby size of furigana
      , colorize // colorize
      , root_.japaneseRubyHighlight
      , root_.japaneseRubyAnnotated
      , root_.japaneseRubyInverted
      , root_.alignCenter
    )
  }

  function renderRuby(text, lang, colorize) { // string, string, bool -> string
    var chwidth = lang == 'ko' ? 13 : 18 // Korean : Chinese
                //: lang === 'ja' ? 22
                //: lang.indexOf('zh') === 0 ? 18
    var chperline = Math.round(root_.width / (chwidth * root_._zoomFactor)) // * (root_.rubyInverted ? 0.85 : 1)) // char per line
    if (lang == 'ko')
      return bean_.renderKoreanRuby(text
        , chperline
        , 10 * root_._zoomFactor // ruby size of furigana
        , root_.rubyInverted // ruby inverted
        , colorize // colorize
        , root_.alignCenter
        , root_.romajaRubyEnabled
        , root_.hanjaRubyEnabled
      )
    else
      return bean_.renderChineseRuby(text, lang == 'zhs' // lang needed to determine if it is simplified
        , root_.chineseRubyType
        , chperline
        , 10 * root_._zoomFactor // ruby size of furigana
        , root_.rubyInverted // ruby inverted
        , colorize // colorize
        , root_.alignCenter
      )
  }

  function renderAlignment(text, lang, alignObject, colorize) { // string, string, QObject -> string
    var chwidth = Util.isCJKLanguage(lang) ? 18 : 10 // wider font for CJK
    var chperline = Math.round(root_.width / (chwidth * root_._zoomFactor)) // char per line
    return bean_.renderAlignment(text, lang, alignObject
      , chperline
      , 10 * root_._zoomFactor // ruby size of furigana
      , colorize // colorize
      , root_.alignCenter
    )
  }

  function renderTranslationRuby(text, lang, width, fontFamily) {
    return bean_.renderTranslationRuby(text, lang
      , Math.max(width - 10, 0) // - 10 in case it is out of screen
      , fontFamily // rb font
      , 18 * root_.zoomFactor || 1 // rb pixel size
      , 'Tahoma' // rt font
      , 14 * root_.zoomFactor || 1 // rt pixel size
      , root_.alignCenter
    )
  }

  function translatorColor(host) { // string -> color
    switch(host) {
    case 'hanviet': return root_.hanVietColor
    case 'romaji': return root_.romajiColor
    case 'jbeijing': return root_.jbeijingColor
    case 'vtrans': return root_.vtransColor
    case 'fastait': return root_.fastaitColor
    case 'dreye': return root_.dreyeColor
    case 'eztrans': return root_.ezTransColor
    case 'transcat': return root_.transcatColor
    case 'atlas': return root_.atlasColor
    case 'lec': return root_.lecColor
    case 'lecol': return root_.lecOnlineColor
    case 'transru': return root_.transruColor
    case 'infoseek': return root_.infoseekColor
    case 'excite': return root_.exciteColor
    case 'babylon': return root_.babylonColor
    case 'systran': return root_.systranColor
    case 'nifty': return root_.niftyColor
    case 'bing': return root_.bingColor
    case 'google': return root_.googleColor
    case 'naver': return root_.naverColor
    case 'baidu': return root_.baiduColor
    case 'youdao': return root_.youdaoColor
    default:
      if (host) {
        var i = host.indexOf(',')
        if (i !== -1)
          return translatorColor(host.substr(0, i))
      }
      return root_.translationColor
    }
  }

  //property int _FADE_DURATION: 400

  // 10/15/2014: whether listmodel is locked. otherwise, VNR might crash when RBMT is turned on
  // Lock the insert/append/clear methods.
  property bool modelLocked: false

  property real _zoomFactor: zoomFactor * globalZoomFactor // actual zoom factor

  property real zoomStep: 0.05

  function zoomIn() {
    var v = zoomFactor + zoomStep
    if (v < maximumZoomFactor)
      zoomFactor = v
  }
  function zoomOut() {
    var v = zoomFactor - zoomStep
    if (v > minimumZoomFactor)
      zoomFactor = v
  }

  property bool highlightVisible: false // disable highlight by default unless pagebreak

  property QtObject highlightMouseArea

  property int _BBCODE_TIMESTAMP: 1363922891

  property int listFooterY: 0

  TexScript.TexHtmlParser { id: tex_
    settings: TexScript.TexHtmlSettings {
      tinySize: Math.round(root_._zoomFactor * 10) + 'px'
      smallSize: Math.round(root_._zoomFactor * 14) + 'px'
      normalSize: Math.round(root_._zoomFactor * 18) + 'px' // the same as textEdit_.font.pixelSize
      largeSize: Math.round(root_._zoomFactor * 28) + 'px'
      hugeSize: Math.round(root_._zoomFactor * 40) + 'px'

      hrefStyle: "color:" + root_.fontColor
      urlStyle: hrefStyle
    }
  }

  //Plugin.BBCodeParser { id: bbcodePlugin_ }
  function renderComment(c) {
    var t = c.text
    if (convertsChinese && c.language === 'zhs')
      t = bean_.convertChinese(t)

    if (c.timestamp > _BBCODE_TIMESTAMP)
      return ~t.indexOf('[') ? bbcodePlugin_.parse(t) :
             ~t.indexOf("\n") ? t.replace(/\n/g, '<br/>') :
             t
      //return bbcodePlugin_.parse(t)
    else
      return ~t.indexOf("\\") ? tex_.toHtml(t) : t
  }

  function renderSub(s) {
    var t = s.text
    if (convertsChinese && s.language === 'zhs')
      t = bean_.convertChinese(t)

    return ~t.indexOf('[') ? bbcodePlugin_.parse(t) :
           ~t.indexOf("\n") ? t.replace(/\n/g, '<br/>') :
           t
  }

  Plugin.GrimoireBean { id: bean_
    //width: root_.width; height: root_.heigh
    Component.onCompleted: {
      bean_.clear.connect(root_.clear)
      bean_.pageBreak.connect(root_.pageBreakLater)

      //bean_.showText.connect(root_.pageBreakCheck)
      //bean_.showTranslation.connect(root_.pageBreakCheck)
      //bean_.showComment.connect(root_.pageBreakCheck)
      //bean_.showSubtitle.connect(root_.pageBreakCheck)
      //bean_.showNameText.connect(root_.pageBreakCheck)
      //bean_.showNameTranslation.connect(root_.pageBreakCheck)

      bean_.showText.connect(root_.showText)
      bean_.showTranslation.connect(root_.showTranslation)
      bean_.showComment.connect(root_.showComment)
      bean_.showSubtitle.connect(root_.showSubtitle)
      bean_.showNameText.connect(root_.showNameText)
      bean_.showNameTranslation.connect(root_.showNameTranslation)
    }
  }

  //Plugin.Tts { id: ttsPlugin_ }
  //Plugin.ClipboardProxy { id: clipboardPlugin_ }
  //Plugin.SubtitleEditorManagerProxy { id: subeditPlugin_ }
  //Plugin.UserViewManagerProxy { id: userViewPlugin_ }

  function fontFamily(lang) {
    //return 'DFGirl Std W7'
    //return 'STCaiyun'
    switch (lang) {
    case 'ja': return japaneseFont
    case 'en': return englishFont
    case 'zhs': case 'zht': return chineseFont
    //case 'zhs': return simplifiedChineseFont
    case 'ko': return koreanFont
    case 'th': return thaiFont
    case 'vi': return vietnameseFont
    case 'id': return indonesianFont
    case 'he': return hebrewFont
    case 'bg': return bulgarianFont
    case 'sl': return slovenianFont
    case 'tl': return tagalogFont
    case 'be': return belarusianFont
    case 'et': return estonianFont
    case 'lv': return latvianFont
    case 'lt': return lithuanianFont
    case 'ms': return malaysianFont
    case 'ar': return arabicFont
    case 'cs': return czechFont
    case 'da': return danishFont
    case 'de': return germanFont
    case 'el': return greekFont
    case 'es': return spanishFont
    case 'fi': return finnishFont
    case 'fr': return frenchFont
    case 'hu': return hungarianFont
    case 'it': return italianFont
    case 'nl': return dutchFont
    case 'no': return norwegianFont
    case 'pl': return polishFont
    case 'pt': return portugueseFont
    case 'ru': return russianFont
    case 'sk': return slovakFont
    case 'sv': return swedishFont
    case 'tr': return turkishFont
    case 'uk': return ukrainianFont
    case 'ro': return romanianFont
    default: return "DFGirl"
    }
  }

  // string t, string lang, return string
  //function splitTranslation(t, lang) { // string, string -> string  insert \n
  //  if (Util.isKanjiLanguage(lang))
  //    return t.replace(/([。？！」\n])(?![。！？）」]|$)/g, "$1\n")
  //  else
  //    return t.replace(/([.?!」])(?![.!?)」]|$)/g, "$1\n").replace(/\.\.\n/g, '.. ') // do not split ".."
  //}

  function splitTranslation(t, lang) { // string, string -> string  insert <br/>
    if (Util.isKanjiLanguage(lang))
      return t.replace(/([。？！」\n])(?![。！？）」\n]|$)/g, '$1<br/>')
    else
      return t.replace(/([.?!」\n])(?![.!?)」\n]|$)/g, '$1<br/>').replace(/\.\.<br\/>/g, '.. ') // do not split ".."
  }

  //Rectangle {
  //  anchors.fill: parent
  //  anchors.margins: -8

  //  visible: root_.borderVisible

  //  //border.color: '#aaff0000' // red
  //  border.color: '#55000000' // black
  //  border.width: 8
  //  radius: 8

  //  color: 'transparent'
  //  MouseArea {
  //    anchors.fill: parent
  //    anchors.margins: -parent.border.width

  //    hoverEnabled: true
  //    acceptedButtons: Qt.LeftButton
  //    drag {
  //      target: root_
  //      axis: Drag.XandYAxis

  //      //minimumX: root_.minimumX; minimumY: root_.minimumY
  //      //maximumX: root_.maximumX; maximumY: root_.maximumY
  //    }

  //    Desktop.TooltipArea {
  //      anchors.fill: parent
  //      text: qsTr("Drag this border to move the text box, and don't forget to unlock the position first")
  //    }
  //  }
  //}

  Rectangle { id: header_
    anchors {
      //left: listView_.left
      left: listView_.left; leftMargin: -9
      bottom: listView_.top; bottomMargin: 4
    }
    //radius: 9
    radius: 0 // flat
    height: 20
    //width: 50
    width: buttonRow_.width + 30

    //visible: !root_.locked
    visible: root_.containsVisibleText

    property bool active: headerToolTip_.containsMouse ||
                          listTopMouseTip_.containsMouse ||
                          listBottomMouseTip_.containsMouse ||
                          buttonRow_.hover ||
                          !!highlightMouseArea && highlightMouseArea.hover

    //color: '#33000000' // black
    //color: active ? '#aa000000' : '#01000000'
    color: root_.shadowColor
    opacity: 0.01

    states: State { name: 'ACTIVE'
      when: header_.active
      PropertyChanges { target: header_; opacity: 0.8 }
      //PropertyChanges { target: horizontalScrollBar_; opacity: 1 }
    }

    transitions: Transition { from: 'ACTIVE'
      NumberAnimation { property: 'opacity'; duration: 400 }
    }

    //gradient: Gradient {  // color: aarrggbb
    //  //GradientStop { position: 0.0;  color: '#ec8f8c8c' }
    //  //GradientStop { position: 0.17; color: '#ca6a6d6a' }
    //  //GradientStop { position: 0.77; color: '#9f3f3f3f' }
    //  //GradientStop { position: 1.0;  color: '#ca6a6d6a' }
    //}

    MouseArea { id: headerMouseArea_
      anchors.fill: parent
      acceptedButtons: Qt.LeftButton
      //enabled: !root_.locked
      drag {
        target: root_
        axis: Drag.XandYAxis
        //minimumX: root_.minimumX; minimumY: root_.minimumY
        //maximumX: root_.maximumX; maximumY: root_.maximumY
      }

      Rectangle {
        anchors.fill: parent
        anchors.margins: -9
        color: '#01000000'

        Desktop.TooltipArea { id: headerToolTip_
          anchors.fill: parent
          text: qsTr("You can drag me to move the text box.")
        }
      }
    }

    Row { id: buttonRow_
      anchors {
        verticalCenter: parent.verticalCenter
        left: parent.left
        //leftMargin: header_.radius
        leftMargin: 1
      }

      spacing: 2

      property bool hover: closeButton_.hover
                        || ttsButton_.hover
                        || zoomOutButton_.hover
                        || zoomInButton_.hover

      //property int cellWidth: 15
      //property int pixelSize: 10
      property int cellWidth: 20
      property int pixelSize: 12

      Share.CircleButton { id: closeButton_
        diameter: parent.cellWidth
        font.pixelSize: parent.pixelSize
        font.bold: hover
        font.family: 'MS Gothic'
        backgroundColor: 'transparent'
        color: root_.fontColor

        text: "×" // ばつ
        toolTip: Sk.tr("Close")
        onClicked: root_.clear()
      }

      Share.CircleButton { id: ttsButton_
        diameter: parent.cellWidth
        font.pixelSize: parent.pixelSize
        font.bold: hover
        font.family: 'MS Gothic'
        backgroundColor: 'transparent'
        color: root_.fontColor

        text: "♪" // おんぷ
        //toolTip: My.tr("Speak")
        toolTip: qsTr("Read current Japanese game text using TTS") + " (" + Sk.tr("Middle-click")  + ")"
        onClicked: root_.speakTextRequested()
      }

      Share.CircleButton { id: zoomOutButton_
        diameter: parent.cellWidth
        font.pixelSize: parent.pixelSize
        font.bold: hover
        font.family: 'MS Gothic'
        backgroundColor: 'transparent'
        color: root_.fontColor

        text: "-"
        toolTip: Sk.tr("Zoom out") + " " + Math.floor(root_.zoomFactor * 100) + "%"
        onClicked: root_.zoomOut()
      }

      Share.CircleButton { id: zoomInButton_
        diameter: parent.cellWidth
        font.pixelSize: parent.pixelSize
        font.bold: hover
        font.family: 'MS Gothic'
        backgroundColor: 'transparent'
        color: root_.fontColor

        text: "+"
        toolTip: Sk.tr("Zoom in") + " " + Math.floor(root_.zoomFactor * 100) + "%"
        onClicked: root_.zoomIn()
      }
    }

    //Text { //id: placeHolder_
    //  anchors {
    //    verticalCenter: parent.verticalCenter
    //    left: closeButton_.right
    //    leftMargin: header_.width - closeButton_.width
    //  }
    //  font.pixelSize: 10
    //  //font.bold: true
    //  //font.italic: true
    //  text: "<= " + qsTr("Drag me to change the position of the text box!")

    //  color: 'snow'
    //  style: Text.Raised
    //  styleColor: 'gray'
    //  //styleColor: 'orangered'
    //  //styleColor: 'deepskyblue'
    //  //styleColor: 'black'
    //}

    //Desktop.Menu { id: headerMenu_

    //  //Desktop.MenuItem {
    //  //  text: qsTr("Scroll to the beginning")
    //  //  onTriggered: root_.scrollBeginning()
    //  //}

    //  //Desktop.MenuItem {
    //  //  text: qsTr("Scroll to the end")
    //  //  onTriggered: root_.scrollEnd()
    //  //}

    //  Desktop.MenuItem {
    //    text: qsTr("Hide text box")
    //    onTriggered: root_.hide()
    //  }

    //  Desktop.Separator {}

    //  Desktop.MenuItem { id: lockAct_
    //    text: qsTr("Lock Position")
    //    checkable: true
    //    checked: true // lock by default
    //  }

    //  Desktop.MenuItem {
    //    text: qsTr("Save Position")
    //    onTriggered: root_.savePosRequested()
    //  }

    //  Desktop.MenuItem {
    //    text: qsTr("Load Position")
    //    onTriggered: root_.loadPosRequested()
    //  }

    //  //Desktop.MenuItem {
    //  //  text: qsTr("Reset Position")
    //  //  onTriggered: root_.resetPosRequested()
    //  //}
    //}

    //MouseArea {
    //  anchors.fill: parent
    //  acceptedButtons: Qt.RightButton | Qt.MiddleButton
    //  onPressed: {
    //    switch (mouse.button) {
    //    case Qt.RightButton:
    //      if (!root_.ignoresFocus) {
    //        var gp = mapToItem(null, x + mouse.x, y + mouse.y)
    //        headerMenu_.showPopup(gp.x, gp.y)
    //      } break
    //    case Qt.MiddleButton:
    //      root_.speakTextRequested()
    //      break
    //    }
    //  }

    //}
  }

  // Hide shadow when no text/name/translation are visible
  property bool containsVisibleText: listView_.count > 0
      && (root_.textVisible || root_.nameVisible || !root_._pageIndex || root_._pageIndex < listView_.count - 1)

  Rectangle { id: shadow_
    anchors {
      left: listView_.left; right: listView_.right
      margins: root_.shadowMargin
    }
    y: Math.max(-listView_.contentY, 0)
    height: Math.min(listView_.height,
            -listView_.contentY + root_.listFooterY - y)
            + 5
    visible: root_.shadowEnabled && root_.containsVisibleText

    //color: root_.revertsColor ? '#99ffffff' : '#44000000'
    color: '#44000000'
    opacity: 0.27 // #44
    z: -1
    //radius: 18
    //radius: 8 * root_.zoomFactor
    //radius: 8
    radius: 0 // flat

    //Share.CloseButton {
    //  anchors { left: parent.left; top: parent.top; margins: 2 }
    //  //border.width: 2
    //  onClicked: root_.hide()
    //  toolTip: qsTr("Hide text box")
    //}
  }

  property int _RESIZABLE_AREA_HEIGHT: 10 // resizable mouse area thickness

  ListView { id: listView_
    anchors.fill: parent
    //width: root_.width; height: root_.height
    clip: true
    boundsBehavior: Flickable.DragOverBounds // no overshoot bounds
    snapMode: ListView.SnapToItem   // move to bounds

    MouseArea { id: listTopMouseArea_ // mouse area for the header
      anchors {
        left: parent.left; right: parent.right
        top: parent.top
      }
      //height: 9
      height: _RESIZABLE_AREA_HEIGHT
      //hoverEnabled: true
      acceptedButtons: Qt.LeftButton

      drag {
        target: root_
        axis: Drag.XandYAxis
        //minimumX: root_.minimumX; minimumY: root_.minimumY
        //maximumX: root_.maximumX; maximumY: root_.maximumY
      }

      Desktop.TooltipArea { id: listTopMouseTip_
        anchors.fill: parent
        text: Sk.tr("Move")
      }
    }

    MouseArea { id: listBottomMouseArea_ // mouse area for the header
      anchors {
        left: parent.left; right: parent.right
      }
      y: shadow_.height - height
      //height: 9
      height: _RESIZABLE_AREA_HEIGHT
      //hoverEnabled: true
      acceptedButtons: Qt.LeftButton

      drag {
        target: root_
        axis: Drag.XandYAxis
        //minimumX: root_.minimumX; minimumY: root_.minimumY
        //maximumX: root_.maximumX; maximumY: root_.maximumY
      }

      Desktop.TooltipArea { id: listBottomMouseTip_
        anchors.fill: parent
        text: Sk.tr("Move")
      }
    }

    //contentWidth: width
    //contentHeight: 2000

    //effect: Effect.DropShadow {
    //  blurRadius: 8
    //  offset: "1,1"
    //  color: '#aa007f' // purple-like
    //}

    model: ListModel { id: listModel_ }

    highlightFollowsCurrentItem: true
    highlightMoveDuration: 0
    highlightResizeDuration: 0

    highlight: Rectangle { //id: highlight_
      width: listView_.width
      //radius: 5
      radius: 0 // flat
      color: root_.shadowEnabled ? '#33000000' : 'transparent'
      visible: root_.highlightVisible && root_.containsVisibleText

      MouseArea { id: highlightMouseArea_ // drag area
        Component.onCompleted: root_.highlightMouseArea = highlightMouseArea_

        anchors.fill: parent
        acceptedButtons: Qt.LeftButton
        enabled: root_.shadowEnabled //&& !root_.locked
        drag {
          target: root_
          axis: Drag.XandYAxis
          //minimumX: root_.minimumX; minimumY: root_.minimumY
          //maximumX: root_.maximumX; maximumY: root_.maximumY
        }

        property alias hover: highlightToolTip_.containsMouse

        Desktop.TooltipArea { id: highlightToolTip_
          anchors.fill: parent
          text: qsTr("You can drag this black bar to move the text box.")
        }
      }

      //Share.CloseButton { id: closeButton_
      //  anchors {
      //    verticalCenter: parent.verticalCenter
      //    left: parent.left
      //    leftMargin: 10
      //  }
      //  onClicked: root_.hide()
      //  toolTip: qsTr("Hide the text box")
      //}

      Share.TextButton { id: saveButton_
        anchors {
          verticalCenter: parent.verticalCenter
          left: parent.left
          leftMargin: 9
        }
        width: 50; height: 25
        text: "[" + Sk.tr("save")
        font.pixelSize: 12
        font.bold: false
        font.family: "DFGirl"
        styleColor: 'deepskyblue'
        backgroundColor: hover ? '#336a6d6a' : 'transparent' // black
        //effect: Share.TextEffect {}
        style: Text.Raised
        onClicked: root_.savePosRequested()
        toolTip: qsTr("Save text box position")
      }

      Share.TextButton { id: loadButton_
        anchors {
          verticalCenter: parent.verticalCenter
          left: saveButton_.right
          leftMargin: -2
        }
        width: 50; height: 25
        text: Sk.tr("load") + "]"
        font.pixelSize: 12
        font.bold: false
        font.family: "DFGirl"
        styleColor: 'deepskyblue'
        backgroundColor: hover ? '#336a6d6a' : 'transparent' // black
        //effect: Share.TextEffect {}
        style: Text.Raised
        onClicked: root_.loadPosRequested()
        toolTip: qsTr("Move text box to the saved position")
      }

      //Share.TextButton { id: resetButton_
      //  anchors {
      //    verticalCenter: parent.verticalCenter
      //    left: loadButton_.right
      //    leftMargin: -6
      //  }
      //  width: 50; height: 25
      //  text: Sk.tr("reset") + "]"
      //  font.family: "DFGirl"
      //  font.pixelSize: 16
      //  font.bold: false
      //  styleColor: 'deepskyblue'
      //  backgroundColor: hover ? '#336a6d6a' : 'transparent' // black
      //  //effect: Share.TextEffect {}
      //  style: Text.Raised
      //  onClicked: root_.resetPosRequested()
      //  toolTip: qsTr("Move text box to the top")
      //}

      Share.TextButton { id: lockButton_
        anchors {
          verticalCenter: parent.verticalCenter
          left: loadButton_.right
          leftMargin: 5
        }
        width: 50; height: 25
        text: "[" + Sk.tr("lock")
        font.family: "DFGirl"
        font.pixelSize: 12
        font.bold: false
        styleColor: checked ? 'red' : 'deepskyblue'
        backgroundColor: hover ? '#336a6d6a' : 'transparent' // black
        //effect: Share.TextEffect {}
        style: Text.Raised
        property bool checked: root_.locked
        onClicked: root_.locked = true
        toolTip: qsTr("Lock text box position")
      }

      Share.TextButton { id: unlockButton_
        anchors {
          verticalCenter: parent.verticalCenter
          left: lockButton_.right
          leftMargin: -2
        }
        width: 50; height: 25
        text: Sk.tr("unlock") + "]"
        font.family: "DFGirl"
        font.pixelSize: 12
        font.bold: false
        styleColor: checked ? 'red' : 'deepskyblue'
        backgroundColor: hover ? '#336a6d6a' : 'transparent' // black
        //effect: Share.TextEffect {}
        style: Text.Raised
        property bool checked: !root_.locked
        onClicked: root_.locked = false
        toolTip: qsTr("Unlock text box position")
      }

      Text { //id: placeHolder_
        anchors {
          verticalCenter: parent.verticalCenter
          left: unlockButton_.right
          leftMargin: 20
        }
        visible: root_.shadowEnabled
        font.pixelSize: 12
        //font.bold: true
        //font.italic: true
        text: "<= " + qsTr("you can drag me!") + " >_<"
        font.family: "DFGirl"

        color: 'snow'
        //style: Text.Raised
        //styleColor: 'deepskyblue'
        //styleColor: 'black'
      }
    }

    // See: http://doc.qt.digia.com/4.7-snapshot/qml-textedit.html#selectWord-method
    //function ensureVisible(r) {
    //  if (contentX >= r.x)
    //    contentX = r.x
    //  else if (contentX+width <= r.x+r.width)
    //    contentX = r.x+r.width-width
    //  if (contentY >= r.y)
    //    contentY = r.y
    //  else if (contentY+height <= r.y+r.height)
    //    contentY = r.y+r.height-height
    //}

    // Behavior on x { SpringAnimation { spring: 3; damping: 0.3; mass: 1.0 } }
    // Behavior on y { SpringAnimation { spring: 3; damping: 0.3; mass: 1.0 } }

    //MouseArea {
    //  acceptedButtons: Qt.LeftButton
    //  anchors.fill: parent
    //  drag.target: parent; drag.axis: Drag.XandYAxis
    //  onPressed: { /*parent.color = 'red';*/ /*parent.styleColor = 'orange';*/ }
    //  onReleased: { /*parent.color = 'snow';*/ /*parent.styleColor = 'red';*/ }
    //}

    states: State {
      when: listView_.movingVertically || listView_.movingHorizontally
      PropertyChanges { target: verticalScrollBar_; opacity: 1 }
      //PropertyChanges { target: horizontalScrollBar_; opacity: 1 }
    }

    transitions: Transition {
      NumberAnimation { property: 'opacity'; duration: 400 }
    }

    delegate: textComponent_
    //delegate: Loader {
    //  sourceComponent: model.component
    //  property QtObject model: model
    //}

    footer: Item {
      width: listView_.width //height: model.height
      height: Math.max(0, listView_.height - 10) // margin: 10

      onYChanged: root_.listFooterY = y

      //Rectangle {
      //  anchors {
      //    left: parent.left; right: parent.right
      //    bottom: parent.top
      //  }
      //  height: listView_.childrenRect.height
      //  visible: root_.shadowEnabled
      //  color: root_.revertsColor ? '#99ffffff' : '#44000000'
      //  z: -1
      //  radius: 20
      //}
    }
  }

  Components.ScrollBar { id: verticalScrollBar_
    width: 12
    height: Math.max(0, listView_.height - 12)
    anchors {
      verticalCenter: listView_.verticalCenter
      left: listView_.right
      leftMargin: 2
    }
    opacity: 0
    orientation: Qt.Vertical
    position: listView_.visibleArea.yPosition
    pageSize: listView_.visibleArea.heightRatio
  }

  //Components.ScrollBar { id: horizontalScrollBar_
  //  width: Math.max(0, listView_.width - 12)
  //  height: 12
  //  anchors.bottom: listView_.bottom
  //  anchors.horizontalCenter: listView_.horizontalCenter
  //  opacity: 0
  //  orientation: Qt.Horizontal
  //  position: listView_.visibleArea.xPosition
  //  pageSize: listView_.visibleArea.widthRatio
  //}

  function showScrollBar() {
    verticalScrollBar_.opacity = 1
  }

  // - List components -

  //property string _JAPANESE_FONT: "MS Gothic"
  ////property string _JAPANESE_FONT: "Meiryo"
  //property string _CHINESE_FONT: "YouYuan"
  //property string _ENGLISH_FONT: "Helvetica"

  //Effect.DropShadow {
  //  blurRadius: 8
  //  offset: "1,1"
  //  color: model.color
  //}

  Component { id: textComponent_
    Item { id: textItem_
      width: visible ? textEdit_.width: 0
      height: visible ? textEdit_.height + 5: 0 // with margins

      property bool hover: toolTip_.containsMouse || textCursor_.containsMouse

      property bool canPopup:
        model.language === 'ja' && root_.japaneseRubyEnabled ||
        model.language === 'ko' && (
          (model.type === 'text' || model.type === 'name') ?
            root_.rubyTextEnabled : root_.rubyTranslationEnabled)

      visible: {
        if (model.comment && (model.comment.disabled || model.comment.deleted))
          return false
        switch (model.type) {
          case 'text': return root_.textVisible
          case 'name': return root_.nameVisible && root_.textVisible
          case 'tr': return root_.translationVisible
          case 'name.tr': return root_.nameVisible && root_.translationVisible
          case 'comment': return root_.commentVisible
          case 'sub': return root_.commentVisible
          default: return true
        }
      }

      //NumberAnimation on opacity { // fade in animation
      //  from: 0; to: 1; duration: _FADE_DURATION
      //}

      //property color itemColor: _itemColor() // cached
      function itemColor() {
        if (toolTip_.containsMouse || textCursor_.containsMouse)
          return 'red'
        switch (model.type) {
        case 'text':
        case 'name': return root_.textColor
        case 'comment': return (model.comment && model.comment.color) || root_.commentColor
        case 'sub': return (model.sub && model.sub.color) || root_.commentColor
        case 'tr': case 'name.tr': return root_.translatorColor(model.provider)
        default: return  'transparent'
        }
      }

      //QmlText.ContouredTextEdit { id: textEdit_
      Qt5.TextEdit5 { id: textEdit_
        Component.onCompleted:
          listModel_.setProperty(model.index, 'textEdit', textEdit_) // Needed for contextMenu event

        //contourEenabled: !!text
        //contourOffset: '4,4'
        ////contourRadius: root_.contourRadius
        //contourRadius: 6
        //contourColor: textItem_.itemColor
        //contourColor: '#aa0000bb'

        //Rectangle {   // Shadow
        //  color: '#44000000'
        //  anchors.fill: parent
        //  z: -1
        //  radius: 15
        //}

        //selectByMouse: true // conflicts with Flickable
        //onLinkActivated: Qt.openUrlExternally(link)

        MouseArea { id: textCursor_
          anchors.fill: parent
          //acceptedButtons: enabled ? Qt.LeftButton : Qt.NoButton
          acceptedButtons: Qt.LeftButton
          //acceptedButtons: Qt.NoButton
          enabled: !!model.text
          hoverEnabled: enabled //&& root_.hoverEnabled && model.language === 'ja'

          //preventStealing: true // no effect

          property string lastSelectedText
          onPositionChanged:
            if (root_.hoverEnabled && textItem_.canPopup) {
              textEdit_.cursorPosition = textEdit_.positionAt(mouse.x, mouse.y)
              textEdit_.selectWord()
              var t = textEdit_.selectedText
              if (t && t !== lastSelectedText) {
                lastSelectedText = t
                //var gp = Util.itemGlobalPos(parent)
                var gp = mapToItem(null, x + mouse.x, y + mouse.y)
                root_.lookupRequested(t, model.language, gp.x, gp.y)
              }
            }

          onClicked: {
            var link = textEdit_.linkAt(mouse.x, mouse.y)
            if (link) {
              if (link.indexOf('json://') === 0)
                link = link.replace('json://', '')
              else {
                Eval.evalLink(link)
                return
              }
            }
            //mouse.accepted = false // no effect due to Qt Bug
            if (root_.mouseLocked)
              return
            root_.mouseLocked = true
            if (model.language) {
              textEdit_.cursorPosition = textEdit_.positionAt(mouse.x, mouse.y)
              textEdit_.selectWord()
              var t = textEdit_.selectedText
              if (t || link) {
                if (t) {
                  lastSelectedText = t
                  //if (root_.copyEnabled)
                  textEdit_.copy()
                }
                if (link || (!root_.hoverEnabled && root_.popupEnabled && textItem_.canPopup)) {
                  //var gp = Util.itemGlobalPos(parent)
                  var gp = mapToItem(null, x + mouse.x, y + mouse.y)
                  if (link)
                    root_.jsonPopupRequested(link, gp.x, gp.y)
                  else
                    root_.lookupRequested(t, model.language, gp.x, gp.y)
                }
                //if (root_.readEnabled && model.language === 'ja')
                if ((model.type === 'text' || model.type !== 'name')) {
                    //&& !root_.sameLanguageAsUser(model.language)) {
                  t = Util.removeHtmlTags(t)
                  if (t) {
                    var lang = model.language
                    if (lang === 'ja')
                      lang = '?'
                    ttsPlugin_.speak(t, lang)
                  }
                }
              }
            }
            root_.mouseLocked = false
          }

          onDoubleClicked: {
            if (root_.mouseLocked)
              return
            root_.mouseLocked = true
            if (model.language) {
              var t = model.text
              if (t) {
                //if (root_.copyEnabled)
                clipboardPlugin_.text = t
                textEdit_.deselect()
                //if (root_.readEnabled)
                //if (model.type === 'text' || model.type !== 'name')
                //if (!root_.sameLanguageAsUser(model.language)) {
                t = root_.normalizeTtsText(t) || t
                ttsPlugin_.speak(t, model.language)
                //}
              }
            }
            root_.mouseLocked = false
          }
        }

        Desktop.TooltipArea { id: toolTip_
          anchors.fill: parent

          visible: !!model.text && model.type !== 'text' && model.type !== 'name'

          text: !textItem_.visible ? '' :
                model.comment ? commentSummary(model.comment) :
                model.sub ? subSummary(model.sub) :
                model.provider ? translationSummary() :
                model.type === 'name' ? My.tr("Character name") :
                My.tr("Game text")

          //function typeSummary() {
          //  switch (model.type) {
          //  case 'tr': return "Machine translation"
          //  case 'subtitle': return "Community subtitle"
          //  case 'comment': return "User comment"
          //  default: return ""
          //  }
          //}

          function translationSummary() {
            var tr = My.tr(Util.translatorName(model.provider))
            var lang = Sk.tr(Util.languageShortName(model.language))
            return tr + " (" + lang + ")"
          }

          function commentSummary(c) {
            var us = '@' + c.userName
            var lang = c.language
            //var lang = Sk.tr(Util.languageShortName(c.language)) // too long orz
            lang = "(" + lang + ")"
            var sec = c.updateTimestamp > 0 ? c.updateTimestamp : c.timestamp
            var ts = Util.timestampToString(sec)
            return us + lang + ' ' + ts
          }

          function subSummary(s) {
            var us = '@' + s.userName
            var lang = s.language
            //var lang = Sk.tr(i18n.languageShortName(c.language)) // too long orz
            lang = "(" + lang + ")"
            var sec = s.updateTime > 0 ? s.updateTime : s.createTime
            var ts = Util.timestampToString(sec)
            return us + lang + ' ' + ts
          }
        }

        // height is the same as painted height
        width: listView_.width

        //property QtObject effect: Effects.Glow {
        effect: Effects.Glow {
          //enabled2: root_.outlineEnabled
          //blurRadius2: 4
          //blurIntensity2: 2
          //offset2: '0,0'   // default
          //color2: 'black'  // default

          offset: '1,1'
          //blurRadius: 8
          blurRadius: root_.glowRadius
          blurIntensity: !textItem_.hover ? root_.glowIntensity :
                         root_.shadowEnabled ? 1 : 2
          enabled: !!textEdit_.text
          color: textItem_.itemColor()
        }

        anchors.centerIn: parent
        textFormat: TextEdit.RichText
        text: !textItem_.visible ? '' : renderText()

        readOnly: true
        focus: false
        //smooth: false // readonly, no translation

        wrapMode: model.language === 'ja' && root_.japaneseRubyEnabled &&
            (model.type === 'text' || model.type === 'name') ?
            TextEdit.NoWrap : TextEdit.Wrap
        verticalAlignment: TextEdit.AlignVCenter
        //horizontalAlignment: TextEdit.AlignHCenter
        horizontalAlignment: root_.alignCenter ? TextEdit.AlignHCenter : TextEdit.AlignLeft

        //onCursorRectangleChanged: listView_.ensureVisible(cursorRectangle)

        //font.italic: Util.isLatinLanguage(model.language)

        //color: root_.revertsColor ? '#050500' : 'snow'
        color: root_.fontColor

        property int fontPixelSize:
            (root_.rubyJaInverted && (model.type === 'text' || model.type === 'name')) ?
            14 * root_._zoomFactor :
            18 * root_._zoomFactor

        font.pixelSize: fontPixelSize

        font.family: root_.fontFamily(model.language)
        font.bold: model.language === 'ja' && fontPixelSize < 23 // MS Gothic
                // bold small DFGirl font for Korean, exclude NanumBarunGothic
                //|| model.language === 'ko' && font.family !== 'NanumBarunGothic' && fontPixelSize < 24 && !root_.rubyInverted

        function renderText() {
          var t
          if (model.comment)
            t = root_.renderComment(model.comment)
          else if (model.sub)
            t = root_.renderSub(model.sub)
          else if (model.text) {
            t = root_.nameVisible ? model.text
              : Util.removeTextName(model.text, model.type === 'text' ? 16 : 0) // max name limit
            if (!t)
              return ""
            if (model.language === 'ja' && (model.type === 'text' || model.type === 'name')) {
              if (root_.removesTextNewLine && ~t.indexOf("\n"))
                t = t.replace(/\n/g, '')
              if (root_.japaneseRubyEnabled)
                t = root_.renderJapanese(t, textItem_.hover)
              return t
            }
          }
          if (!t)
            return ""
          if (root_.isRubyLanguage(model.language) &&
              ((model.type === 'text' || model.type === 'name') ?
              root_.rubyTextEnabled : root_.rubyTranslationEnabled))
            t = root_.renderRuby(t, model.language, textItem_.hover)
          else if (model.alignObject)
            t = root_.renderAlignment(t || model.text, model.language, model.alignObject, textItem_.hover)
          else {
            if ((model.type === 'tr' || model.type === 'name.tr')
                && root_.termRubyEnabled && ~t.indexOf('[ruby='))
              t = root_.renderTranslationRuby(t, model.language, textEdit_.width, font.family)
            else if (root_.splitsTranslation && model.type === 'tr')
              t = root_.splitTranslation(t, model.language)
          }
          if (~t.indexOf("</a>"))
            t = '<style>a{color:"' + root_.fontColor + '"}</style>' + t
          //clipboardPlugin_.text = t // for debugging purpose
          return t || ""
          //return !t ? "" : root_.shadowEnabled ? t :
          //  '<span style="background-color:rgba(0,0,0,10)">' + t + '</span>'
        }
      }
    }
  }

  // Index of the first item on the last page
  // Assume page index is always less then list view count
  property int _pageIndex: 0 // always pointed the place where new item can be inserted
  property int _timestamp: 0 // current text timestamp

  //Component.onCompleted: {
    //pageBreak()
    //console.log("grimoire.qml: pass")
  //}

  function createTextItem(text, lang, type, alignObject, provider, comment) {
    return {
      comment: type === 'sub' ? null : comment
      , sub: type === 'sub' ? comment : null
      , language: lang
      , text: text
      , type: type // text, tr, comment, name, or name.tr
      , alignObject: alignObject // opaque object or null
      , provider: provider
      , textEdit: undefined // placeHolder property
    }
  }

  function addText(text, lang, type, provider, comment) {
    if (modelLocked)
      return
    modelLocked = true
    var item = createTextItem(text, lang, type, null, provider, comment)
    listModel_.append(item) // I assume the text always comes before translation
    listView_.currentIndex = _pageIndex
    modelLocked = false
  }

  function showText(text, lang, timestamp) {
    //if (!listModel_.count)
    //  pageBreak()

    _timestamp = timestamp

    if  (root_.textVisible) {
      pageBreakCheck()
      addText(text, lang, 'text')
    }
  }

  function showNameText(text, lang) {
    //if (!listModel_.count)
    //  pageBreak()
    if  (!root_.nameVisible)
      return
    if (modelLocked)
      return
    pageBreakCheck()
    modelLocked = true

    text = "【" + text + "】"
    var item = createTextItem(text, lang, 'name')
    var index = _pageIndex + 1 // fix index

    if (index <= listModel_.count)
      listModel_.insert(index, item)
    else
      listModel_.append(item)

    listView_.currentIndex = _pageIndex
    //if (_pageIndex + 1 < listView_.count) {
    //  listView_.positionViewAtIndex(_pageIndex +1, ListView.Beginning)
    //}
    modelLocked = false
  }

  function showTranslation(text, lang, provider, alignObject, timestamp) {
    if  (!root_.translationVisible)
      return
    if (modelLocked)
      return
    pageBreakCheck()
    modelLocked = true

    //if (!listModel_.count)
    //  pageBreak()

    //text = text.replace(/\n/g, "<br/>")
    var item = createTextItem(text, lang, 'tr', alignObject, provider)
    if (_timestamp === Number(timestamp))
      listModel_.append(item)
    else if (_pageIndex <= listModel_.count)
      listModel_.insert(_pageIndex++, item)
    else // this should never happen
      listModel_.append(item)
    listView_.currentIndex = _pageIndex
    modelLocked = false
  }

  function showNameTranslation(text, lang, provider) {
    if  (!root_.translationVisible || !root_.nameVisible)
      return
    //if (!listModel_.count)
    //  pageBreak()
    if (modelLocked)
      return
    pageBreakCheck()
    modelLocked = true

    var alignObject = null // TODO: mapping is not implemented for name
    text = "【" + text + "】"
    var item = createTextItem(text, lang, 'name.tr', alignObject, provider)
    var index = _pageIndex + 3
    if (index <= listModel_.count)
      listModel_.insert(index, item)
    else
      listModel_.append(item)
    listView_.currentIndex = _pageIndex
    modelLocked = false
  }

  function showComment(c) { // actually subtitle rather than comment
    //if (!listModel_.count)
    //  pageBreak()
    pageBreakCheck()
    addText(c.text, c.language, 'comment', undefined, c)
  }

  function showSubtitle(s) {
    pageBreakCheck()
    addText(s.text, s.language, 'sub', undefined, s)
  }

  // Insert a page break
  function pageBreak() {
    if (listModel_.count) { // only add pagebreak if there are texts

      slimList()
      _pageIndex = listModel_.count
      addText()
      cls()
      //highlight_.visible = true // no idea why this does not work
      root_.highlightVisible = true
    }
  }

  property bool pageBreakChecked: true

  function pageBreakCheck() {
    if (pageBreakChecked) {
      pageBreakChecked = false
      pageBreak()
    }
  }
  function pageBreakLater() {
    pageBreakChecked = true
  }

  // Limit total number of items in the list by removing extra items in the beginning
  function slimList() {
    // 1 paragraph is around 4 tr + 1 game text + 1 game name + 1 pagebreak = 7
    // 30 < 5 * 7
    if (listModel_.count > 30) {   // if the list size is greater than 30
      if (modelLocked)
        return
      modelLocked = true
      //console.log("grimoire.qml:slimList: enter: count =", listModel_.count)
      while (listModel_.count > 20) // remove the first 10 items
        listModel_.remove(0)
      if (listView_.currentIndex >= 10) // 10 = 30 - 20
        listView_.currentIndex -= 10
      modelLocked = false
      //console.log("grimoire.qml:slimList: leave: count =", listModel_.count)
      //console.log("grimoire.qml:slimList: pass")
    }
  }

  // Clean the screen by scrolling
  function cls() {
    if (_pageIndex + 1 < listView_.count)
      listView_.positionViewAtIndex(_pageIndex + 1, ListView.Beginning)
    else
      listView_.positionViewAtEnd()
  }

  function clear() {
    if (modelLocked)
      return
    modelLocked = true
    pageBreakChecked = false
    _pageIndex = 0
    listModel_.clear()
    //highlight_.visible = false
    root_.highlightVisible = false
    modelLocked = false
    console.log("grimoire.qml:clear: pass")
  }

  // - Context Menu -

  // Popup globalPos

  property int popupX
  property int popupY

  function popupIndex() {
    var pos = listView_.mapFromItem(null, popupX, popupY)
    return listView_.indexAt(listView_.contentX + pos.x, listView_.contentY + pos.y)
  }

  function textEditAt(index) {
    if (index >= 0 && index < listModel_.count) {
      var item = listModel_.get(index)
      if (item)
        return item.textEdit
    }
    return undefined
  }

  function textEditHoveredText(textEdit) {
    if (!textEdit.selectedText) {
      var pos = textEdit.mapFromItem(null, popupX, popupY)
      textEdit.cursorPosition = textEdit.positionAt(pos.x, pos.y)
      textEdit.selectWord()
    }
    return textEdit.selectedText
  }

  //function textEditHighlightText(textEdit) {
  //  textEditHoveredText(textEdit)
  //}

  function popupHoveredText() {
    var e = textEditAt(popupIndex())
    return e ? textEditHoveredText(e) : ''
  }

  Desktop.Menu { id: menu_
    function popup(x, y) {
      popupX = x; popupY = y

      var item = listModel_.get(popupIndex())
      //textEditHighlightText(item.textEdit)

      termAct_.enabled = !!item && item.type !== 'comment' && item.type !== 'sub'
      if (termAct_.enabled) {
        termAct_.itemType = item.type
        termAct_.itemLanguage = item.language
      }

      var hasComment = !!(item && item.comment)
      editAct_.enabled = hasComment
      userAct_.enabled = hasComment

      showPopup(x, y)
    }

    Desktop.MenuItem { id: editAct_
      text: Sk.tr("Edit")
      onTriggered: {
        var item = listModel_.get(popupIndex())
        if (item && item.comment)
          mainPlugin_.showSubtitleEditor(item.comment)
      }
    }

    Desktop.MenuItem { id: userAct_
      text: Sk.tr("User information")
      onTriggered: {
        var item = listModel_.get(popupIndex())
        if (item && item.comment)
          mainPlugin_.showUser(item.comment.userId)
      }
    }

    Desktop.Separator {}

    Desktop.MenuItem { id: termAct_
      property string itemType
      property string itemLanguage

      text: qsTr("Add to the Shared Dictionary")

      onTriggered: {
        var t = popupHoveredText()
        if (t) {
          var type = itemType === 'tr' || itemType == 'name.tr' ? 'output' : ''
          var lang = type === 'output' ? itemLanguage : ''
          mainPlugin_.showNewTerm(t, type, lang)
        }
      }
    }

    Desktop.Separator {}

    Desktop.MenuItem {
      text: Sk.tr("Copy")
      //shortcut: "Ctrl+A"
      onTriggered: {
        var item = listModel_.get(popupIndex())
        if (item && item.text)
          clipboardPlugin_.text = Util.removeHtmlTags(item.text)
          //clipboardPlugin_.text = item.text
      }
    }

    //Desktop.MenuItem { id: copyAct_
    //  text: Sk.tr("Copy")
    //  shortcut: "Ctrl+C"
    //  onTriggered: {
    //    var e = textEditAt(popupIndex())
    //    if (e) {
    //      var t = textEditHoveredText(e)
    //      if (t)
    //        e.copy()
    //      //console.log("grimoire.qml:copy: pass")
    //    }
    //  }
    //}

    //Desktop.MenuItem {
    //  text: Sk.tr("Paste")
    //  shortcut: "Ctrl+V"
    //  onTriggered: {
    //    var e = textEditAt(popupIndex())
    //    if (e) {
    //      e.paste()
    //      console.log("grimoire.qml:paste: pass")
    //    }
    //  }
    //}

    //Desktop.MenuItem {
    //  text: Sk.tr("Cut")
    //  shortcut: "Ctrl+X"
    //  onTriggered: {
    //    var e = textEditAt(popupIndex())
    //    if (e && e.selectedText) {
    //      e.cut()
    //      console.log("grimoire.qml:cut: pass")
    //    }
    //  }
    //}

    //Desktop.MenuItem {
    //  text: qsTr("Select Word")
    //  //shortcut: "Ctrl+A"
    //  onTriggered: {
    //    var e = textEditAt(popupIndex())
    //    if (e) {
    //      var pos = e.mapFromItem(null, popupX, popupY)
    //      e.cursorPosition = e.positionAt(pos.x, pos.y)
    //      e.selectWord()
    //      console.log("grimoire.qml:selectWord: pass")
    //    }
    //  }
    //}

    //Desktop.MenuItem {
    //  text: Sk.tr("Select All")
    //  shortcut: "Ctrl+A"
    //  onTriggered: {
    //    var e = textEditAt(popupIndex())
    //    if (e) {
    //      e.selectAll()
    //      console.log("grimoire.qml:selectAll: pass")
    //    }
    //  }
    //}

    //Desktop.MenuItem {
    //  text: qsTr("Lookup selection")
    //  //shortcut: "Ctrl+A"
    //  onTriggered: {
    //    var e = textEditAt(popupIndex())
    //    if (e) {
    //      if (t) {
    //        var t = e.selectedText
    //        lookupRequested(t, 'ja', popupX, popupY)
    //        console.log("grimoire.qml:lookup: pass")
    //      }
    //    }
    //  }
    //}

    //Desktop.MenuItem {
    //  text: qsTr("Read Selection")
    //  //shortcut: "Ctrl+A"
    //  onTriggered: {
    //    var e = textEditAt(popupIndex())
    //    if (e && e.selectedText) {
    //      var lang = listModel_.get(popupIndex()).language
    //      if (lang) {
    //        ttsPlugin_.speak(e.selectedText, lang)
    //        console.log("grimoire.qml:read: pass")
    //      }
    //    }
    //  }
    //}

    Desktop.MenuItem {
      text: My.tr("Read Sentence") + " (" + Sk.tr("Double-click") + ")"
      //shortcut: "Ctrl+A"
      onTriggered: {
        var item = listModel_.get(popupIndex())
        if (item && item.text && item.language) {
          var t = item.text
          t = root_.normalizeTtsText(t) || t
          ttsPlugin_.speak(t, item.language)
          console.log("grimoire.qml:readAll: pass")
        }
      }
    }

    Desktop.MenuItem {
      text: qsTr("Read Current") + " (" + Sk.tr("Middle-click") + ")"
      //shortcut: "Ctrl+A"
      onTriggered: root_.speakTextRequested()
    }

    Desktop.MenuItem {
      text: qsTr("Scroll to the Beginning")
      onTriggered: root_.scrollBeginning()
    }

    Desktop.MenuItem {
      text: qsTr("Scroll to the End")
      onTriggered: root_.scrollEnd()
    }

    //Desktop.MenuItem { id: borderAct_
    //  text: qsTr("Show draggable border")
    //  checkable: true
    //  checked: false // hide border by default
    //}

    Desktop.Separator {}

    Desktop.MenuItem { id: lockAct_
      text: qsTr("Lock Position")
      checkable: true
      checked: true // lock by default
    }

    Desktop.MenuItem {
      text: qsTr("Save Position")
      onTriggered: root_.savePosRequested()
    }

    Desktop.MenuItem {
      text: qsTr("Load Position")
      onTriggered: root_.loadPosRequested()
    }

    //Desktop.MenuItem {
    //  text: qsTr("Reset Position")
    //  onTriggered: root_.resetPosRequested()
    //}

    Desktop.Separator {}

    Desktop.MenuItem {
      text: Sk.tr("Clear")
      onTriggered: root_.clear()
    }

    Desktop.MenuItem { //id: hideAct_
      text: qsTr("Hide text box")
      onTriggered: root_.hide()
    }
  }

  MouseArea {
    anchors.fill: parent
    acceptedButtons: Qt.RightButton | Qt.MiddleButton
    onPressed: {
      switch (mouse.button) {
      case Qt.RightButton:
        if (!root_.ignoresFocus) {
          var gp = mapToItem(null, x + mouse.x, y + mouse.y)
          menu_.popup(gp.x, gp.y)
        } break
      case Qt.MiddleButton:
        root_.speakTextRequested()
        break
      }
    }

  }
}

// EOF

/*
  Component { id: paddingComponent_ // one of list delegate components
    Item {
      Rectangle { // Shadow
        anchors {
          bottom: parent.top
          left: parent.left; right: parent.right
        }
        height: listView_.childrenRect.height - parent.height
        visible: root_.shadowEnabled

        color: '#44000000'
        z: -1
        radius: 15
      }
      width: root_.width; height: modelData.height
    }
  }

  function createPaddingItem() {
    return {
      'component': paddingComponent_,
      'comment': undefined,
      'color': undefined,
      'height': 0,
      'language': undefined,
      'needsWrap': undefined,
      'text': undefined,
      'type': undefined,
    }
  }

*/

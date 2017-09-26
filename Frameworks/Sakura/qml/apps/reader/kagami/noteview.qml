/** noteview.qml
 *  12/21/2012 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/eval.min.js' as Eval
import '../../../js/util.min.js' as Util
import '../../../imports/texscript' as TexScript
import '../../../components' as Components
import '../share' as Share

Item { id: root_

  property int minimumX
  property int minimumY
  property int maximumX
  property int maximumY

  property bool ignoresFocus: false
  property real globalZoomFactor: 1.0
  property real zoomFactor: 1.0

  property bool commentVisible
  property bool convertsChinese

  property color effectColor

  // - Private -

  property real _zoomFactor: zoomFactor * globalZoomFactor

  property real zoomStep: 0.05
  property real minimumZoomFactor: 0.5
  property real maximumZoomFactor: 3.0

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

  property int _BBCODE_TIMESTAMP: 1363922891

  property int _MAX_HEIGHT: 400 * _zoomFactor

  property int _DEFAULT_WIDTH: 400 * _zoomFactor
  property int _MIN_WIDTH: 50 * _zoomFactor
  property int _MAX_WIDTH: 1000 * _zoomFactor

  property int _RESIZABLE_AREA_WIDTH: 15 // resizable mouse area thickness

  property int _HEADER_MARGIN: 2

  property int _FADE_DURATION: 800

  property QtObject comment
  property string language: comment ? comment.language : 'en'

  property QtObject comments: ListModel {}

  width: scrollArea_.width + 20; height: scrollArea_.height + 20

  opacity: 0 // initial opacity is zero

  visible: commentVisible && (
    comments.count !== 0 ||
    !comment ||
    !comment.disabled && !comment.deleted
  )

  //gradient: Gradient {  // color: aarrggbb
  //  GradientStop { position: 0.0;  color: '#ec8f8c8c' }
  //  GradientStop { position: 0.17; color: '#ca6a6d6a' }
  //  GradientStop { position: 0.77; color: '#9f3f3f3f' }
  //  GradientStop { position: 1.0;  color: '#ca6a6d6a' }
  //}

  Rectangle { // shadow
    anchors.fill: parent
    //radius: 10
    radius: 0 // flat
    color: root_.hover ? '#aa000000' : '#88000000'
  }

  MouseArea { //id: dragArea_
    anchors.fill: parent
    hoverEnabled: true
    acceptedButtons: Qt.LeftButton
    drag {
      target: parent
      axis: Drag.XandYAxis

      minimumX: root_.minimumX; minimumY: root_.minimumY
      maximumX: root_.maximumX; maximumY: root_.maximumY
    }
  }

  MouseArea { // left draggable area
    anchors {
      top: parent.top; bottom: parent.bottom
      left: parent.left
    }
    width: _RESIZABLE_AREA_WIDTH
    acceptedButtons: Qt.LeftButton

    property int pressedX
    onPressed: pressedX = mouseX
    onPositionChanged:
      if (pressed) {
        var dx = mouseX - pressedX
        var w = textEdit_.width - dx
        if (w > _MIN_WIDTH && w < _MAX_WIDTH) {
          textEdit_.width = w
          root_.x += dx
        }
      }

    Desktop.TooltipArea { id: leftResizeTip_
      anchors.fill: parent
      text: Sk.tr("Resize")
    }
  }

  MouseArea { // right draggable area
    anchors {
      top: parent.top; bottom: parent.bottom
      right: parent.right
    }
    width: _RESIZABLE_AREA_WIDTH
    acceptedButtons: Qt.LeftButton

    property int pressedX
    onPressed: pressedX = mouseX
    onPositionChanged:
      if (pressed) {
        var w = textEdit_.width + mouseX - pressedX
        if (w > _MIN_WIDTH && w < _MAX_WIDTH)
          textEdit_.width = w
      }

    Desktop.TooltipArea { id: rightResizeTip_
      anchors.fill: parent
      text: Sk.tr("Resize")
    }
  }

  Flickable { id: scrollArea_
    anchors.centerIn: parent
    height: Math.min(_MAX_HEIGHT, textEdit_.paintedHeight)
    width: textEdit_.width

    //contentWidth: textEdit_.paintedWidth
    contentHeight: textEdit_.paintedHeight
    clip: true

    states: State {
      when: scrollArea_.movingVertically || scrollArea_.movingHorizontally
      PropertyChanges { target: verticalScrollBar_; opacity: 1 }
      //PropertyChanges { target: horizontalScrollBar_; opacity: 1 }
    }

    transitions: Transition {
      NumberAnimation { property: 'opacity'; duration: 400 }
    }

    TextEdit { id: textEdit_
      anchors.centerIn: parent
      //width: _DEFAULT_WIDTH // FIXME: automatically adjust width
      readOnly: true

      selectByMouse: true // conflicts with flickable

      // Disable rich text, so that we can tell if TextEdit is empty
      textFormat: TextEdit.RichText

      text: {
        if (!root_.comment)
          return ""
        var ret = root_.renderComment(root_.comment)
        if (root_.comments.count > 0)
          for (var i = root_.comments.count - 1; i >= 0; i-=1)
            ret = root_.renderComment(root_.comments.get(i)) + "<br/>" + ret
        return ret
      }

      //visible:
      //  root_.comments.count !== 0 ||
      //  !root_.comment ||  ||
      //  !root_.comment.disabled && !root_.comment.deleted

      wrapMode: TextEdit.Wrap
      verticalAlignment: TextEdit.AlignVCenter
      horizontalAlignment: TextEdit.AlignLeft
      focus: false
      color: 'snow'

      //font.family: Util.fontFamilyForLanguage(root_.language)
      font.family: 'DFGirl'


      //font.italic: Util.isLatinLanguage(root_.language)
      font.pixelSize: 16 * root_._zoomFactor

      // Not working, which cause textedit width to shrink
      //onTextChanged: width = Math.min(_MAX_WIDTH, paintedWidth)

      onLinkActivated: Eval.evalLink(link)

      //console.log("shiori.qml: link activated:", link)

      effect: Share.TextEffect {
        highlight: toolTip_.containsMouse
        color: highlight ? 'red' :
               (comment && comment.color) ? comment.color :
               root_.effectColor
      }
    }
  }

  Components.ScrollBar { id: verticalScrollBar_
    width: 12
    height: Math.max(0, scrollArea_.height - 12)
    anchors.right: scrollArea_.right
    anchors.verticalCenter: scrollArea_.verticalCenter
    opacity: 0
    orientation: Qt.Vertical
    position: scrollArea_.visibleArea.yPosition
    pageSize: scrollArea_.visibleArea.heightRatio
  }

  //Components.ScrollBar { id: horizontalScrollBar_
  //  width: Math.max(0, scrollArea_.width - 12)
  //  height: 12
  //  anchors.bottom: scrollArea_.bottom
  //  anchors.horizontalCenter: scrollArea_.horizontalCenter
  //  opacity: 0
  //  orientation: Qt.Horizontal
  //  position: scrollArea_.visibleArea.xPosition
  //  pageSize: scrollArea_.visibleArea.widthRatio
  //}

  //NumberAnimation on opacity { id: fadeOutAni_
  NumberAnimation { id: fadeOutAni_
    target: root_; property: 'opacity'
    to: 0; duration: _FADE_DURATION
  }

  TexScript.TexHtmlParser { id: tex_
    settings: TexScript.TexHtmlSettings {
      tinySize: "10px"
      smallSize: "14px"
      normalSize: "16px" // the same as textEdit_.font.pixelSize
      largeSize: "28px"
      hugeSize: "40px"

      hrefStyle: "color:snow"
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

  //Plugin.SubtitleEditorManagerProxy { id: subeditPlugin_ }
  //Plugin.UserViewManagerProxy { id: userViewPlugin_ }

  Plugin.GospelBean { id: bean_
    Component.onCompleted: {
      bean_.clear.connect(root_.clear)
      bean_.hide.connect(root_.hide)
      bean_.showComment.connect(root_.showComment)
    }
  }

  function clear() {
    textEdit_.width = _DEFAULT_WIDTH
    root_.comment = null
    if (root_.comments.count > 0)
      root_.comments.clear()
  }

  function showComment(c) {
    if (!commentVisible)
      return
    if (!opacity)
      clear()
    if (root_.comment)
      root_.comments.append(root_.comment)
    root_.comment = c

    //root_.x = x + _X_OFFSET; root_.y = y + _Y_OFFSET
    ensureVisible()
    show()
  }

  function hide() { fadeOutAni_.start() }
  function show() { fadeOutAni_.stop(); opacity = 1 }

  // So that the popup will not be out of screen
  function ensureVisible() {
    if (x < minimumX)
      x = minimumX
    if (y < minimumY)
      y = minimumY
    if (x > maximumX)
      x = maximumX
    if (y > maximumY)
      y = maximumY
  }

  // - Context Menu -

  Desktop.Menu { id: menu_

    Desktop.MenuItem { //id: editAct_
      text: Sk.tr("Edit")
      onTriggered:
        if (comment)
          mainPlugin_.showSubtitleEditor(comment)
    }

    Desktop.MenuItem {
      text: Sk.tr("Copy")
      //shortcut: "Ctrl+A"
      onTriggered: {
        textEdit_.selectAll()
        textEdit_.copy()
      }
    }

    Desktop.MenuItem {
      text: Sk.tr("User information")
      onTriggered:
        if (comment)
          mainPlugin_.showUser(comment.userId)
    }

    //Desktop.MenuItem {
    //  text: qsTr("Read All")
    //  //shortcut: "Ctrl+A"
    //  onTriggered: {
    //    textEdit_.selectAll()
    //    if (textEdit_.selectedText) {
    //      tts_.speak(textEdit_.selectedText, 'en')
    //      console.log("shiori.qml:readAll: pass")
    //    }
    //  }
    //}

    Desktop.Separator {}

    Desktop.MenuItem {
      text: Sk.tr("Hide")
      //shortcut: "Esc"
      onTriggered: root_.hide()
    }
  }

  MouseArea { id: mouse_
    anchors.fill: parent
    //hoverEnabled: true
    acceptedButtons: Qt.RightButton
    enabled: !root_.ignoresFocus
    onPressed: if (!root_.ignoresFocus) {
      //var gp = Util.itemGlobalPos(parent)
      var gp = mapToItem(null, x + mouse.x, y + mouse.y)
      menu_.showPopup(gp.x, gp.y)
    }
  }

  property bool hover: toolTip_.containsMouse || header_.hover

  Desktop.TooltipArea { id: toolTip_
    anchors.fill: parent
    text: comment ? commentSummary(comment) : ""
  }

  function commentSummary(c) {
    var us = '@' + c.userName
    var lang = c.language
    lang = "(" + lang + ")"
    var sec = c.updateTimestamp > 0 ? c.updateTimestamp : c.timestamp
    var ts = Util.timestampToString(sec)
    return us + lang + ' ' + ts
  }

  Row { id: header_
    anchors { left: parent.left; top: parent.top; margins: -4 }
    spacing: _HEADER_MARGIN * 2

    property bool hover: closeButton_.hover
                      || zoomInButton_.hover
                      || zoomOutButton_.hover

    property int cellWidth: 15
    property int pixelSize: 10

    Share.CircleButton { id: closeButton_
      diameter: parent.cellWidth
      font.pixelSize: parent.pixelSize
      font.bold: hover
      font.family: 'MS Gothic'
      backgroundColor: 'transparent'

      text: "×" // ばつ
      toolTip: Sk.tr("Close")
      onClicked: root_.hide()
    }

    Share.CircleButton { id: zoomOutButton_
      diameter: parent.cellWidth
      font.pixelSize: parent.pixelSize
      font.bold: hover
      font.family: 'MS Gothic'
      backgroundColor: 'transparent'

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

      text: "+"
      toolTip: Sk.tr("Zoom in") + " " + Math.floor(root_.zoomFactor * 100) + "%"
      onClicked: root_.zoomIn()
    }
  }
}

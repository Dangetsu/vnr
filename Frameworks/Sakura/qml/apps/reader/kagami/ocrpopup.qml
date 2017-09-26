/** ocrpopup.qml
 *  8/16/2014 jichi
 *  Text popup manager for OCR.
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
//import '../../../js/eval.min.js' as Eval
import '../../../js/util.min.js' as Util
import '../../../components' as Components
import '../../../js/local.js' as Local // Local.comet
import '../share' as Share
import '.' as Kagami

Item { id: root_

  property real globalZoomFactor: 1.0
  property bool ignoresFocus: false

  property real zoomFactor: 1.0

  // - Private -

  Component { id: editComp_
    Kagami.OcrEdit {
      zoomFactor: root_._zoomFactor
      ignoresFocus: root_.ignoresFocus
    }
  }

  property real _zoomFactor: zoomFactor * globalZoomFactor // actual zoom factor

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

  property int _MAX_HEIGHT: 200 * _zoomFactor

  property int _DEFAULT_WIDTH: 200 * _zoomFactor
  property int _MIN_WIDTH: 50 * _zoomFactor
  property int _MAX_WIDTH: 800 * _zoomFactor

  property int _RESIZABLE_AREA_WIDTH: 15 // resizable mouse area thickness

  property int _HEADER_MARGIN: 2

  Component.onCompleted: Local.items = [] // [item]

  Plugin.OcrPopupBean { //id: bean_
    Component.onCompleted:
      popupRequested.connect(root_.showPopup)
  }

  function showPopup(x, y, imgobj, winobj, text, lang) { // int, int, OcrImageObject, WindowObject, string, string ->
    var items = Local.items
    for (var i in items) {
      var item = items[i]
      if (!item.visible && !item.locked) {
        console.log("ocrpopup.qml:showPopup: reuse existing item")
        item.show(text, lang, x, y, imgobj, winobj)
        return
      }
    }
    console.log("ocrpopup.qml:showPopup: create new item")
    var item = comp_.createObject(root_)
    item.show(text, lang, x, y, imgobj, winobj)
    items.push(item)
  }

  // Component

  Component { id: comp_
    Rectangle { id: item_
      property int minimumX: root_.x
      property int minimumY: root_.y
      property int maximumX: minimumX + root_.width - width
      property int maximumY: minimumY + root_.height - height

      //property alias text: textEdit_.text
      //property alias textWidth: textEdit_.width

      property string language: 'ja'

      property bool locked: false // indicate whether this object is being translated

      property QtObject window // WindowObject  window proxy
      property QtObject image // OcrImageObject  ocr controller

      function show(text, lang, x, y, image, window) { // string, string, int, int, OcrImageObject, WindowObject ->
        reset()

        item_.originalText = item_.translatedText = text
        textEdit_.text = text || ('(' + Sk.tr('empty') + ')')

        item_.language = lang //|| 'ja'

        item_.image = image

        item_.window = window

        if (window) {
          item_.relativeX = x - window.x
          item_.relativeY = y - window.y
          window.visibleChanged.connect(setVisible)
        } else {
          item_.x = x
          item_.y = y
        }

        ensureVisible()
        visible = window ? window.visible : true
      }

      function hide() { visible = false }

      // - Private -

      property string originalText // OCR text
      property string translatedText // text when translate button is pressed
      property string currentText: translatedText || originalText

      property Item editItem

      function hideEdit() {
        if (editItem)
          editItem.hide()
      }

      function showEdit() {
        if (!editItem) {
          console.log("ocregion.qml: create ocr editor")
          editItem = editComp_.createObject(root_, {
            visible: false // hide on startup
          })
          editItem.textChanged.connect(loadEditText)
        } else if (editItem.busy) {
          growl_.showWarning(qsTr("Waiting for previous OCR to finish") + ' ...')
          return
        }

        editItem.x = Math.min(item_.x + item_.width + 10, root_.x + root_.width - item_.width)
        editItem.y = Math.min(item_.y, root_.x + root_.height - item_.height)
        editItem.show(image, originalText)
      }

      function loadEditText() {
        if (editItem) {
          resetText()
          textEdit_.text = originalText = translatedText = editItem.text
        }
      }

      function release() {
        hideEdit() // release image in edit first
        releaseWindow()
        releaseImage()
      }

      function releaseImage() {
        if (image) {
          image.release()
          image = null
        }
      }

      function releaseWindow() {
        if (window) {
          window.visibleChanged.disconnect(setVisible)
          window.release()
          window = null
        }
      }

      function setVisible(t) { visible = t }

      //property bool hidden: true
      //visible: !hidden && (!window || window.visible)

      onVisibleChanged: if (!visible) release()

      property int relativeX
      property int relativeY

      property bool dragging:
          dragArea_.drag.active ||
          headerDragArea_.drag.active
          //leftResizeArea_.pressed ||
          //rightResizeArea_.pressed

      onDraggingChanged: keepPosotion()
      function keepPosotion() {
        if (window) {
          relativeX = x - window.x
          relativeY = y - window.y
        }
      }

      x: (!dragging && window) ? relativeX + window.x : x
      y: (!dragging && window) ? relativeY + window.y : y

      function setX(v) { // int ->
        if (!dragging && window)
          relativeX = v - window.x
        else
          x = v
      }

      function setY(v) { // int ->
        if (!dragging && window)
          relativeY = v - window.y
        else
          y = v
      }

      function resetPosition() {
        relativeX = relativeY = 0
        textEdit_.width = _DEFAULT_WIDTH
      }

      function resetText() {
        translateButton_.enabled = true
        toolTip_.text = qsTr("You can drag the border to move the text box")
      }

      function reset() {
        resetPosition()
        resetText()
        release()
      }

      Component.onCompleted: console.log("ocrpopup.qml:onCompleted: pass")
      Component.onDestruction: console.log("ocrpopup.qml:onDestruction: pass")

      //radius: 9
      radius: 0 // flat

      color: '#99000000' // black

      property int _CONTENT_MARGIN: 10

      width: scrollArea_.width + _CONTENT_MARGIN * 2
      height: scrollArea_.height + _CONTENT_MARGIN * 2

      // So that the popup will not be out of screen
      function ensureVisible() {
        if (x < minimumX)
          setX(minimumX)
        if (y < minimumY)
          setY(minimumY)
        if (x > maximumX)
          setX(maximumX)
        if (y > maximumY)
          setY(maximumY)
      }

      function speak() {
        if (currentText)
          ttsPlugin_.speak(currentText, language)
      }

      function translate() {
        item_.locked = true
        var text = textEdit_.text
        if (text) {
          item_.translatedText = text
          var str = trPlugin_.translators(language)
          if (str) {
            var keys = str.split(',')
            if (keys.length)
              //textEdit_.textFormat = TextEdit.RichText
              for (var i in keys) {
                var key = keys[i]
                var tr = trPlugin_.translate(text, language, key)
                if (tr && tr != text)
                  appendTranslation(tr, key)

                var name = My.tr(Util.translatorName(key))
                if (i == 0)
                  toolTip_.text = name
                else
                  toolTip_.text += ", " + name
              }
          }
        }
        item_.locked = false
      }

      function appendTranslation(tr, key) { // translator key, translation text
        var text = textEdit_.text
        if (text)
          text += '\n'
        text += tr
        textEdit_.text = text
      }

      // Draggable margins

      Desktop.TooltipArea { id: toolTip_
        anchors.fill: parent
      }

      MouseArea { id: dragArea_
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton
        drag {
          target: item_
          axis: Drag.XandYAxis

          minimumX: item_.minimumX; minimumY: item_.minimumY
          maximumX: item_.maximumX; maximumY: item_.maximumY
        }

        //Desktop.TooltipArea { id: dragTip_
        //  anchors.fill: parent
        //  text: Sk.tr("Move")
        //}
      }

      MouseArea { id: leftResizeArea_
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

              //item_.x += dx
              //setX(item_.x + dx)
              if (window)
                item_.relativeX += dx
              else
                item_.x += dx
            }
          }

        Desktop.TooltipArea { id: leftResizeTip_
          anchors.fill: parent
          text: Sk.tr("Resize")
        }
      }

      MouseArea { id: rightResizeArea_
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
            var dx = mouseX - pressedX
            var w = textEdit_.width + dx
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
          //width: _MAX_WIDTH // FIXME: automatically adjust width

          //selectByMouse: true // conflicts with flickable

          // Not enabled since RichText is not used
          //onLinkActivated: Eval.evalLink(link)
          textFormat: TextEdit.PlainText
          wrapMode: TextEdit.Wrap
          focus: true
          color: 'snow'
          font.pixelSize: 12 * root_._zoomFactor
          //font.bold: true
          //font.family: 'MS Mincho' // 明朝

          // Not working, which cause textedit width to shrink
          //onTextChanged: width = Math.min(_MAX_WIDTH, paintedWidth)

          //console.log("shiori.qml: link activated:", link)

          effect: Share.TextEffect {}

          MouseArea { //id: textCursor_
            anchors.fill: parent
            //acceptedButtons: enabled ? Qt.LeftButton : Qt.NoButton
            acceptedButtons: Qt.LeftButton
            //enabled: !!model.text
            //hoverEnabled: enabled

            // Disabled since TTS does not work in admin
            //onDoubleClicked: {
            //  textEdit_.cursorPosition = textEdit_.positionAt(mouse.x, mouse.y)
            //  textEdit_.selectWord()
            //  var t = textEdit_.selectedText
            //  if (t) {
            //    clipboardPlugin_.text = t
            //    ttsPlugin_.speak(t, 'ja')
            //  }
            //}
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

      Desktop.Menu { id: menu_
        //property int popupX
        //property int popupY

        //function popup(x, y) {
        //  //popupX = x; popupY = y
        //  showPopup(x, y)
        //}

        Desktop.MenuItem { //id: copyAct_
          text: Sk.tr("Copy")
          shortcut: "Ctrl+C"
          onTriggered: {
            var t = textEdit_.text || item_.currentText
            if (t)
              clipboardPlugin_.text = t
          }
        }

        Desktop.MenuItem { //id: editAct_
          text: qsTr("Select Color")
          //shortcut: "Ctrl+C"
          onTriggered: item_.showEdit()
        }

        Desktop.Separator {}

        Desktop.MenuItem {
          text: Sk.tr("Close")
          //shortcut: "Esc"
          onTriggered: item_.hide()
        }
      }

      MouseArea { id: mouse_
        anchors.fill: parent
        //hoverEnabled: true
        acceptedButtons: Qt.RightButton
        //onEntered: item_.show()
        //onExited: item_.show() // bypass restart timer issue
        onPressed: if (!root_.ignoresFocus) {
          //var gp = Util.itemGlobalPos(parent)
          var gp = mapToItem(null, x + mouse.x, y + mouse.y)
          menu_.showPopup(gp.x, gp.y)
        }
      }

      Rectangle { id: header_
        anchors {
          left: parent.left
          bottom: parent.top
          //bottomMargin: -_HEADER_MARGIN*2
        }
        //radius: 7
        radius: 0 // flat

        width: headerRow_.width + _HEADER_MARGIN * 2 + _HEADER_MARGIN * 8
        height: headerRow_.height + _HEADER_MARGIN * 2

        color: item_.color

        opacity: 0.01 // invisible by default

        property bool active: toolTip_.containsMouse
                           //|| dragTip_.containsMouse
                           || leftResizeTip_.containsMouse
                           || rightResizeTip_.containsMouse
                           || headerTip_.containsMouse
                           || headerRow_.hover

        states: State { name: 'ACTIVE'
          when: header_.active
          PropertyChanges { target: header_; opacity: 0.8 }
          //PropertyChanges { target: horizontalScrollBar_; opacity: 1 }
        }

        transitions: Transition { from: 'ACTIVE'
          NumberAnimation { property: 'opacity'; duration: 400 }
        }

        MouseArea { id: headerDragArea_
          anchors.fill: parent
          acceptedButtons: Qt.LeftButton
          drag {
            target: item_
            axis: Drag.XandYAxis

            minimumX: item_.minimumX; minimumY: item_.minimumY
            maximumX: item_.maximumX; maximumY: item_.maximumY
          }
        }

        Desktop.TooltipArea { id: headerTip_
          anchors.fill: parent
          text: qsTr("You can drag the border to move the text box")
        }

        Row { id: headerRow_
          //anchors.centerIn: parent
          anchors {
            verticalCenter: parent.verticalCenter
            left: parent.left
            leftMargin: _HEADER_MARGIN
          }

          property bool hover:
              closeButton_.hover ||
              editButton_.hover ||
              translateButton_.hover ||
              ttsButton_.hover ||
              zoomInButton_.hover ||
              zoomOutButton_.hover

          spacing: _HEADER_MARGIN * 2

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
            onClicked: item_.hide()
          }

          Share.CircleButton { id: editButton_
            diameter: parent.cellWidth
            font.pixelSize: parent.pixelSize
            //font.bold: hover    // bold make the text too bold
            font.family: 'MS Gothic'
            backgroundColor: 'transparent'

            color: enabled ? 'snow' : 'gray'
            text: '色'
            toolTip: qsTr("Select color")
            onClicked: showEdit()
          }

          Share.CircleButton { id: translateButton_
            diameter: parent.cellWidth
            font.pixelSize: parent.pixelSize
            //font.bold: hover    // bold make the text too bold
            font.family: 'MS Gothic'
            backgroundColor: 'transparent'

            color: enabled ? 'snow' : 'gray'
            text: '訳'
            toolTip: Sk.tr("Translate")
            onClicked:
              if (enabled && textEdit_.text) {
                enabled = false
                toolTip_.text = qsTr('Translating') + '...'
                item_.translate()
              }
          }

          Share.CircleButton { id: ttsButton_
            diameter: parent.cellWidth
            font.pixelSize: parent.pixelSize
            font.bold: hover
            font.family: 'MS Gothic'
            backgroundColor: 'transparent'

            text: "♪" // おんぷ
            toolTip: My.tr("Speak")
            onClicked: item_.speak()
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
    }
  }
}

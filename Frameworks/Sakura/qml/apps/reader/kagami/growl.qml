/** growl.qml
 *  10/27/2012 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../components' as Components
import '../share' as Share

Item { id: root_
  width: 300
  property int alignment: Qt.AlignRight // horizontal

  property bool ignoresFocus: false

  property bool hidden: _pageIndex === listModel_.count // no visible items

  property real zoomFactor: 1.0

  property bool enabled: true

  function show() { showMe() }

  // - Private -

  property int _VISIBLE_DURATION: 5000

  ListView { id: listView_
    anchors.fill: parent
    //width: root_.width; height: root_.height
    clip: true
    boundsBehavior: Flickable.DragOverBounds // no overshoot bounds
    snapMode: ListView.SnapToItem   // move to bounds

    //contentWidth: width
    //contentHeight: 2000

    //effect: Effects.DropShadow {
    //  blurRadius: 1
    //  offset: Qt.point(1, 1)
    //  color: 'magenta'
    //}

    model: ListModel { id: listModel_ }

    //highlight: Rectangle { color: 'black'; radius: 5; opacity: 0.2 }
    //highlightFollowsCurrentItem: true

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

    footer: Item {
      width: listView_.width
      height: listView_.height - 40 // with margins
    }

    delegate: textComponent_
    //delegate: Loader {
    //  sourceComponent: model.component
    //  property QtObject modelData: model
    //}
  }

  Components.ScrollBar { id: verticalScrollBar_
    width: 12
    height: Math.max(0, listView_.height - 12)
    anchors.right: listView_.right
    anchors.verticalCenter: listView_.verticalCenter
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

  Component { id: textComponent_ // list delegate
    Item { id: textItem_
      width: textEdit_.width + 20
      height: textEdit_.height + 30

      //Component.onCompleted: fadeInAni_.start()

      //opacity: 0
      //states: State {
      //  when: textItem_.visible
      //  PropertyChanges { target: textItem_; opacity: 1 }
      //}
      //transitions: Transition {
      //  NumberAnimation { property: 'opacity'; duration: 400 } // same as jquery.fade duration
      //}
      //Component.onCompleted: state = 'FADEIN'

      NumberAnimation on opacity { id: fadeInAni_
        from: 0; to: 1; duration: 600
      }

      // Shadow
      Rectangle {
        color: {
          switch (model.type) {
          case 'message': return '#55000000' // black
          case 'error': return '#55ff0000' // red
          case 'warning': return '#55a52a2a' // brown
          case 'note': return '#550000aa' // blue
          default: return 'transparent'
          }
        }

        anchors {
          verticalCenter: parent.verticalCenter
          left: root_.alignment === Qt.AlignLeft ? parent.left : undefined
          right: root_.alignment === Qt.AlignRight ? parent.right : undefined
        }
        z: -1
        width: textEdit_.paintedWidth + 20
        height: textEdit_.paintedHeight + 20
        //radius: 15
        //radius: 8 * root_.zoomFactor
        //radius: 8
        radius: 0 // flat
      }

      TextEdit { id: textEdit_
        anchors.centerIn: parent
        // height is the same as painted height
        width: Math.max(0, listView_.width - 20)

        onLinkActivated: {
          growl_.showMessage(My.tr("Open in external browser"))
          Qt.openUrlExternally(link)
        }

        effect: Share.TextEffect { highlight: mouse_.containsMouse }

        focus: false
        //smooth: true  // not used
        textFormat: TextEdit.RichText
        text: renderText(model.text)
        //readOnly: true

        wrapMode: TextEdit.Wrap
        verticalAlignment: TextEdit.AlignVCenter
        horizontalAlignment: root_.alignment === Qt.AlignLeft ? TextEdit.AlignLeft : TextEdit.AlignRight

        selectByMouse: true

        //font.family: "Helvetica"
        //font.family: "MS Mincho"
        //font.family: "Heiti TC"
        //font.family: "Tahoma"
        //font.family: "NanumBarunGothic"
        font.family: "YouYuan"
        font.bold: true

        //onCursorRectangleChanged: listView_.ensureVisible(cursorRectangle)

        font.pixelSize: 18 * root_.zoomFactor
        color: 'snow'

        function renderText(t) { return t ? t : "" }

        //onActiveFocusChanged: {
        //  console.log(activeFocus)
        //  listModel_.setProperty(model.index, 'focused', activeFocus)
        //  //visibleTimer_.restart()
        //}

        MouseArea { id: mouse_
          anchors.fill: parent
          hoverEnabled: true
          acceptedButtons: Qt.RightButton
          onPressed: if (!root_.ignoresFocus) {
            //var gp = Util.itemGlobalPos(parent)
            var gp = mapToItem(null, x + mouse.x, y + mouse.y)
            menu_.popup(gp.x, gp.y, textEdit_)
          }
        }
      }
    }
  }

  Plugin.GrowlBean { id: bean_
    Component.onCompleted: {
      bean_.show.connect(root_.showMe)
      bean_.pageBreak.connect(root_.pageBreak)
      bean_.message.connect(root_.showMessage)
      bean_.warning.connect(root_.showWarning)
      bean_.error.connect(root_.showError)
      bean_.notification.connect(root_.showNotification)
    }
  }

  Timer { id: visibleTimer_
    interval: _VISIBLE_DURATION
    onTriggered: {
      root_.lastText = ''
      root_.hideMe()
    }
  }

  NumberAnimation on opacity { id: fadeOutAni_
    to: 0; duration: 1000
  }

  // Show me without stop
  function alwaysShowMe() {
    if (fadeOutAni_.running)
      fadeOutAni_.stop()
    root_.opacity  = 1
    if (visibleTimer_.running)
      visibleTimer_.stop()
  }

  function showMe() {
    if (fadeOutAni_.running)
      fadeOutAni_.stop()
    root_.opacity  = 1
    visibleTimer_.restart()
  }

  function hideMe() {
    //if (isFocused()) {
    //  showMe()
    //  return
    //}

    if (visibleTimer_.running)
      visibleTimer_.stop()
    fadeOutAni_.restart()
    pageBreak()
  }

  //function isFocused() {
  //  for (var i = 0; i < listModel_.count; ++i)
  //    if (listModel_.get(i).focused)
  //      return true
  //  return false
  //}

  // Index of the first item on the last page
  // Assume page index is always less then list view count
  property int _pageIndex: 0

  //Component.onCompleted: console.log("growl.qml: pass")

  property bool modelLocked: false // otherwise, VNR might crash when switching fullscreen

  property string lastText // previous showed message text

  function appendItem(item) {
    if (modelLocked)
      return false
    modelLocked = true
    listModel_.append(item) // contention
    modelLocked = false
    return true
  }

  function addText(text, type) {
    if (text === root_.lastText)
      return
    root_.lastText = text
    var item = {text:text, type:type}
    //listModel_.append(item)
    if (appendItem(item)) {
      listView_.currentIndex = _pageIndex + 1
      cls()
    }
  }

  function showMessage(text) { addText(text, 'message'); showMe() }
  function showWarning(text) { addText(text, 'warning'); showMe() }
  function showError(text) { addText(text, 'error'); showMe() }
  function showNotification(text) { addText(text, 'note'); showMe() }

  function msg(text) { showMessage(text) }
  function warn(text) { showWarning(text) }
  function error(text) { showError(text) }
  function notify(text) { showNotification(text) }

  // Insert a page break
  function pageBreak() {
    if (root_.enabled && _pageIndex !== listModel_.count) {
      addText("*", 'pagebreak', 'transparent') // green
      _pageIndex = listModel_.count
    }
  }

  function cls() { listView_.positionViewAtIndex(_pageIndex, ListView.Beginning) }

  // - Context Menu -

  property QtObject selectedTextEdit
  Desktop.Menu { id: menu_

    function popup(x, y, textEdit) {
      selectedTextEdit = textEdit
      showPopup(x, y)
    }

    Desktop.MenuItem {
      text: Sk.tr("Copy")
      onTriggered:
        if (selectedTextEdit) {
          if (!selectedTextEdit.selectedText)
            selectedTextEdit.selectAll()
          selectedTextEdit.copy()
        }
    }

    Desktop.Separator {}

    Desktop.MenuItem { id: autoHideAct_
      text: My.tr("Auto Hide")
      checkable: true
      //shortcut: "Esc"
      checked: true
      onTriggered:
        if (checked)
          root_.showMe()
        else
          root_.alwaysShowMe()
    }

    Desktop.MenuItem {
      text: Sk.tr("Hide")
      //shortcut: "Esc"
      onTriggered: root_.hideMe()
    }
  }
}

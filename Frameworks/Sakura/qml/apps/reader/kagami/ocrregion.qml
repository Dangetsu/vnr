/** ocrregion.qml
 *  9/10/2014 jichi
 *  Region selector for OCR.
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/local.js' as Local // Local.comet
import '../share' as Share
import '.' as Kagami

Item { id: root_

  property real zoomFactor: 1.0
  property bool ignoresFocus: false
  property bool wine: false
  property bool enabled: false
  property bool globalPosEnabled: false // capture desktop instead of window
  visible: false

  // - Private -

  Component { id: editComp_
    Kagami.OcrEdit {
      zoomFactor: root_.zoomFactor
      ignoresFocus: root_.ignoresFocus
    }
  }

  Component.onCompleted: Local.items = [] // [item]

  Plugin.OcrRegionBean { id: bean_
    enabled: root_.enabled
    visible: root_.visible
    desktopSelected: root_.globalPosEnabled

    Component.onCompleted:
      regionRequested.connect(root_.showRegion)
  }

  function showRegion(globalX, globalY, width, height) { // int, int, int, int, OcrImageObject, WindowObject, string, string ->
    var pos = mapFromItem(null, globalX, globalY)

    var items = Local.items
    for (var i in items) {
      var item = items[i]
      if (!item.active) {
        console.log("ocrregion.qml:showRegion: reuse existing item")
        item.show(pos.x, pos.y, width, height)
        return
      }
    }
    console.log("ocrregion.qml:showRegion: create new item")
    var item = comp_.createObject(root_)
    item.show(pos.x, pos.y, width, height)
    items.push(item)
    bean_.addRegionItem(item)
  }

  // Component

  property int _ITEM_BORDER_WIDTH: 7
  property int _MIN_WIDTH: _ITEM_BORDER_WIDTH * 2 + 5

  Component { id: comp_
    Item { id: item_
      property bool active: true
      property alias enabled: enableAct_.checked

      property string recognizedText // last ocr-ed text

      property QtObject imageObject // OcrImageObject

      property int globalX: root_.mapToItem(null, x, y).x // revert of the mapFromItem at root
      property int globalY: root_.mapToItem(null, x, y).y

      property bool dragging:
          leftArea_.drag.active ||
          rightArea_.drag.active ||
          topArea_.drag.active ||
          bottomArea_.drag.active ||
          topLeftArea_.pressed ||
          topRightArea_.pressed ||
          bottomLeftArea_.pressed ||
          bottomRightArea_.pressed

      function show(x, y, width, height) { // int, int, int, int
        item_.x = x
        item_.y = y
        setWidth(width)
        setHeight(height)
        active = visible = true
      }

      function close() {
        active = visible = false
      }


      // - Private -

      onActiveChanged: if (!active) release()

      onVisibleChanged: if (!visible) hideEdit()

      property real normalizedWidth: 1.0
      property real normalizedHeight: 1.0
      width: normalizedWidth * root_.width
      height: normalizedHeight * root_.height

      function setWidth(v) { normalizedWidth = root_.width ? v / root_.width : 0 }
      function setHeight(v) { normalizedHeight = root_.height ? v / root_.height : 0 }

      property bool hover: header_.hover
                        || leftTip_.containsMouse
                        || rightTip_.containsMouse
                        || topTip_.containsMouse
                        || bottomTip_.containsMouse
                        || topLeftTip_.containsMouse
                        || topRightTip_.containsMouse
                        || bottomLeftTip_.containsMouse
                        || bottomRightTip_.containsMouse

      property Item editItem
      property bool editLocked: false

      property color pauseColor: enabled ? '#aa00bfff' : '#aa800080' // blue : purple
      property color runningColor: pauseColor
      property color runningColor2: '#aafffafa' // snow
      property int twinkleInterval: 400 * 2 // 2 times of jQuery animation interval
      //property color runningColor2: '#aabebebe' // gray

      function release() {
        if (imageObject) {
          imageObject.release()
          imageObject = null
          console.log("ocregion.qml: release image object")
        }
      }

      function hideEdit() {
        if (editItem)
          editItem.hide()
      }

      function showEdit() {
        if (editLocked)
          return

        if (!editItem) {
          console.log("ocregion.qml: create ocr editor")
          editItem = editComp_.createObject(root_, {
            visible: false // hide on startup
          })
        } else if (editItem.busy) {
          growl_.showWarning(qsTr("Waiting for previous OCR to finish") + ' ...')
          return
        }

        editLocked = true
        if (!imageObject) {
          console.log("ocregion.qml: create image object")
          imageObject = bean_.createImageObject()
        }

        imageObject.width = width
        imageObject.height = height

        if (root_.globalPosEnabled) {
          imageObject.x = globalX
          imageObject.y = globalY
        } else {
          imageObject.x = x
          imageObject.y = y
        }

        if (root_.globalPosEnabled)
          imageObject.captureDesktop()
        else
          imageObject.captureWindow()

        var text = imageObject.ocr()
        editItem.x = Math.min(item_.x, root_.x + root_.width - item_.width)
        editItem.y = Math.min(item_.y, root_.y + root_.height - item_.height)
        editItem.show(imageObject, text)
        editLocked = false
      }

      // Resizable

      Share.TwinkleRectangle { id: leftBorder_
        anchors {
          top: parent.top; bottom: parent.bottom
          right: parent.left
          topMargin: -_ITEM_BORDER_WIDTH
          bottomMargin: -_ITEM_BORDER_WIDTH
        }
        width: _ITEM_BORDER_WIDTH
        radius: _ITEM_BORDER_WIDTH / 2

        pauseColor: item_.pauseColor
        runningColor: item_.runningColor
        runningColor2: item_.runningColor2
        duration: item_.twinkleInterval
        running: visible && ((!!item_.editItem && item_.editItem.visible)
              || leftTip_.containsMouse || topLeftTip_.containsMouse || bottomLeftTip_.containsMouse)
      }

      Share.TwinkleRectangle { id: rightBorder_
        anchors {
          top: parent.top; bottom: parent.bottom
          left: parent.right
          topMargin: -_ITEM_BORDER_WIDTH
          bottomMargin: -_ITEM_BORDER_WIDTH
        }
        width: _ITEM_BORDER_WIDTH
        radius: _ITEM_BORDER_WIDTH / 2

        pauseColor: item_.pauseColor
        runningColor: item_.runningColor
        runningColor2: item_.runningColor2
        duration: item_.twinkleInterval
        running: visible && ((!!item_.editItem && item_.editItem.visible)
              || rightTip_.containsMouse || topRightTip_.containsMouse || bottomRightTip_.containsMouse)
      }

      Share.TwinkleRectangle { id: topBorder_
        anchors {
          left: parent.left; right: parent.right
          bottom: parent.top
          leftMargin: -_ITEM_BORDER_WIDTH
          rightMargin: -_ITEM_BORDER_WIDTH
        }
        height: _ITEM_BORDER_WIDTH
        radius: _ITEM_BORDER_WIDTH / 2

        pauseColor: item_.pauseColor
        runningColor: item_.runningColor
        runningColor2: item_.runningColor2
        duration: item_.twinkleInterval
        running: visible && ((!!item_.editItem && item_.editItem.visible)
              || topTip_.containsMouse || topLeftTip_.containsMouse || topRightTip_.containsMouse)
      }

      Share.TwinkleRectangle { id: bottomBorder_
        anchors {
          left: parent.left; right: parent.right
          top: parent.bottom
          leftMargin: -_ITEM_BORDER_WIDTH
          rightMargin: -_ITEM_BORDER_WIDTH
        }
        height: _ITEM_BORDER_WIDTH
        radius: _ITEM_BORDER_WIDTH / 2

        pauseColor: item_.pauseColor
        runningColor: item_.runningColor
        runningColor2: item_.runningColor2
        duration: item_.twinkleInterval
        running: visible && ((!!item_.editItem && item_.editItem.visible)
              || bottomTip_.containsMouse || bottomLeftTip_.containsMouse || bottomRightTip_.containsMouse)
      }

      MouseArea { id: leftArea_
        anchors.fill: leftBorder_
        acceptedButtons: Qt.LeftButton
        drag {
          target: item_
          axis: Drag.XandYAxis
        }

        //property int pressedX
        //onPressed: pressedX = mouseX
        //onPositionChanged:
        //  if (pressed) {
        //    var dx = mouseX - pressedX
        //    var w = item_.width - dx
        //    if (w > _MIN_WIDTH) {
        //      item_.setWidth(w)
        //      item_.x += dx
        //    }
        //  }

        Desktop.TooltipArea { id: leftTip_
          anchors.fill: parent
          text: Sk.tr("Move")
        }
      }

      MouseArea { id: rightArea_
        anchors.fill: rightBorder_
        acceptedButtons: Qt.LeftButton
        drag {
          target: item_
          axis: Drag.XandYAxis
        }

        //property int pressedX
        //onPressed: pressedX = mouseX
        //onPositionChanged:
        //  if (pressed) {
        //    var dx = mouseX - pressedX
        //    var w = item_.width + dx
        //    if (w > _MIN_WIDTH)
        //      item_.setWidth(w)
        //  }

        Desktop.TooltipArea { id: rightTip_
          anchors.fill: parent
          text: Sk.tr("Move")
        }
      }

      MouseArea { id: topArea_
        anchors.fill: topBorder_
        acceptedButtons: Qt.LeftButton
        drag {
          target: item_
          axis: Drag.XandYAxis
        }

        //property int pressedY
        //onPressed: pressedY = mouseY
        //onPositionChanged:
        //  if (pressed) {
        //    var dy = mouseY - pressedY
        //    var h = item_.height - dy
        //    if (h > _MIN_WIDTH) {
        //      item_.setHeight(h)
        //      item_.y += dy
        //    }
        //  }

        Desktop.TooltipArea { id: topTip_
          anchors.fill: parent
          text: Sk.tr("Move")
        }
      }

      MouseArea { id: bottomArea_
        anchors.fill: bottomBorder_
        acceptedButtons: Qt.LeftButton
        drag {
          target: item_
          axis: Drag.XandYAxis
        }

        //property int pressedY
        //onPressed: pressedY = mouseY
        //onPositionChanged:
        //  if (pressed) {
        //    var dy = mouseY - pressedY
        //    var h = item_.height + dy
        //    if (h > _MIN_WIDTH)
        //      item_.setHeight(h)
        //  }

        Desktop.TooltipArea { id: bottomTip_
          anchors.fill: parent
          text: Sk.tr("Move")
        }
      }

      MouseArea { id: topLeftArea_
        anchors {
          bottom: parent.top
          right: parent.left
        }
        width: _ITEM_BORDER_WIDTH
        height: _ITEM_BORDER_WIDTH
        acceptedButtons: Qt.LeftButton

        property int pressedX
        property int pressedY
        onPressed: {
          pressedX = mouseX
          pressedY = mouseY
        }
        onPositionChanged:
          if (pressed) {
            var dx = mouseX - pressedX
            var dy = mouseY - pressedY
            var w = item_.width - dx
            var h = item_.height - dy
            if (w > _MIN_WIDTH) {
              item_.setWidth(w)
              item_.x += dx
            }
            if (h > _MIN_WIDTH) {
              item_.setHeight(h)
              item_.y += dy
            }
          }

        Desktop.TooltipArea { id: topLeftTip_
          anchors.fill: parent
          text: Sk.tr("Resize")
        }
      }

      MouseArea { id: topRightArea_
        anchors {
          bottom: parent.top
          left: parent.right
        }
        width: _ITEM_BORDER_WIDTH
        height: _ITEM_BORDER_WIDTH
        acceptedButtons: Qt.LeftButton

        property int pressedX
        property int pressedY
        onPressed: {
          pressedX = mouseX
          pressedY = mouseY
        }
        onPositionChanged:
          if (pressed) {
            var dx = mouseX - pressedX
            var dy = mouseY - pressedY
            var w = item_.width + dx
            var h = item_.height - dy
            if (w > _MIN_WIDTH) {
              item_.setWidth(w)
              //item_.x += dx
            }
            if (h > _MIN_WIDTH) {
              item_.setHeight(h)
              item_.y += dy
            }
          }

        Desktop.TooltipArea { id: topRightTip_
          anchors.fill: parent
          text: Sk.tr("Resize")
        }
      }

      MouseArea { id: bottomLeftArea_
        anchors {
          top: parent.bottom
          right: parent.left
        }
        width: _ITEM_BORDER_WIDTH
        height: _ITEM_BORDER_WIDTH
        acceptedButtons: Qt.LeftButton

        property int pressedX
        property int pressedY
        onPressed: {
          pressedX = mouseX
          pressedY = mouseY
        }
        onPositionChanged:
          if (pressed) {
            var dx = mouseX - pressedX
            var dy = mouseY - pressedY
            var w = item_.width - dx
            var h = item_.height + dy
            if (w > _MIN_WIDTH) {
              item_.setWidth(w)
              item_.x += dx
            }
            if (h > _MIN_WIDTH) {
              item_.setHeight(h)
              //item_.y += dy
            }
          }

        Desktop.TooltipArea { id: bottomLeftTip_
          anchors.fill: parent
          text: Sk.tr("Resize")
        }
      }

      MouseArea { id: bottomRightArea_
        anchors {
          top: parent.bottom
          left: parent.right
        }
        width: _ITEM_BORDER_WIDTH
        height: _ITEM_BORDER_WIDTH
        acceptedButtons: Qt.LeftButton

        property int pressedX
        property int pressedY
        onPressed: {
          pressedX = mouseX
          pressedY = mouseY
        }
        onPositionChanged:
          if (pressed) {
            var dx = mouseX - pressedX
            var dy = mouseY - pressedY
            var w = item_.width + dx
            var h = item_.height + dy
            if (w > _MIN_WIDTH) {
              item_.setWidth(w)
              //item_.x += dx
            }
            if (h > _MIN_WIDTH) {
              item_.setHeight(h)
              //item_.y += dy
            }
          }

        Desktop.TooltipArea { id: bottomRightTip_
          anchors.fill: parent
          text: Sk.tr("Resize")
        }
      }

      // Header

      Rectangle { // header shadow
        anchors.fill: header_
        color: root_.wine ? '#10000000' : '#01000000' // alpha = 1/255 is too small that do not work on wine
      }

      Row { id: header_
        anchors {
          left: topBorder_.left
          bottom: topBorder_.bottom
          leftMargin: -1
          //bottomMargin: 1
        }
        spacing: 0

        property bool hover: closeButton_.hover
                          || enableButton_.hover
                          || editButton_.hover

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
          onClicked: item_.close()
        }

        Share.CircleButton { id: enableButton_
          diameter: parent.cellWidth
          font.pixelSize: parent.pixelSize
          font.bold: hover
          font.family: 'MS Gothic'
          backgroundColor: 'transparent'

          text: checked ? "◯" : "｜" //  まる
          //text: "◯" // まる
          toolTip: checked ? Sk.tr("Enabled") : Sk.tr("Disabled")

          property alias checked: enableAct_.checked
          onClicked: checked = !checked
        }

        Share.CircleButton { id: editButton_
          diameter: parent.cellWidth
          font.pixelSize: parent.pixelSize
          font.bold: hover
          font.family: 'MS Gothic'
          backgroundColor: 'transparent'

          text: "⌘" // U+2318 コマンド記号
          toolTip: Sk.tr("Option")

          onClicked: showEdit()
        }
      }

      // Context menu

      Desktop.Menu { id: menu_
        Desktop.MenuItem {
          text: Sk.tr("Close")
          onTriggered: item_.close()
        }

        Desktop.MenuItem { id: enableAct_
          text: Sk.tr("Enable")
          checkable: true
          checked: true
        }

        Desktop.MenuItem {
          text: Sk.tr("Edit")
          onTriggered: item_.showEdit()
        }
      }

      MouseArea { id: mouse_
        anchors.fill: parent
        anchors.margins: -_ITEM_BORDER_WIDTH
        acceptedButtons: Qt.RightButton
        onPressed:
          if (!root_.ignoresFocus) {
            //var gp = Util.itemGlobalPos(parent)
            var gp = mapToItem(null, x + mouse.x, y + mouse.y)
            menu_.showPopup(gp.x, gp.y)
          }
      }
    }
  }
}

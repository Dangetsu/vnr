/** contextedit.qml
 *  6/5/2013 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
//import '../../../imports/qmlhelper' as Helper
import '../../../js/sakurakit.min.js' as Sk
import '../../../components' as Components
import '../../../components/qt5' as Qt5

Item { id: root_

  // - Private -

  //Helper.QmlHelper { id: qmlhelper_ }

  Plugin.SubtitleContextBean { id: bean_
    onRefresh: root_.refresh()
  }

  Component.onCompleted: refresh()

  function refresh() { textEdit_.text = bean_.renderText() }


  clip: true

  Flickable { id: scrollArea_
    anchors {
      fill: parent
      margins: 9
    }
    contentHeight: textEdit_.paintedHeight
    clip: true

    // See: http://doc.qt.digia.com/4.7-snapshot/qml-textedit.html#selectWord-method
    function ensureVisible(r) {
      if (contentX >= r.x)
        contentX = r.x
      else if (contentX+width <= r.x+r.width)
        contentX = r.x+r.width-width
      if (contentY >= r.y)
        contentY = r.y
      else if (contentY+height <= r.y+r.height)
        contentY = r.y+r.height-height
    }

    states: State {
      when: scrollArea_.movingVertically || scrollArea_.movingHorizontally
      PropertyChanges { target: verticalScrollBar_; opacity: 1 }
      //PropertyChanges { target: horizontalScrollBar_; opacity: 1 }
    }

    transitions: Transition {
      NumberAnimation { property: 'opacity'; duration: 400 }
    }

    Qt5.TextEdit5 { id: textEdit_
      //anchors.centerIn: parent
      width: parent.width
      wrapMode: TextEdit.WordWrap
      focus: true
      selectByMouse: true

      readOnly: true

      onCursorRectangleChanged: scrollArea_.ensureVisible(cursorRectangle)

      // 4/10/2015: Temporarily disabled
      //Plugin.MeCabHighlighter {
      //  document: textEdit_.getTextDocument()
      //  enabled: root_.visible && toolTip_.containsMouse
      //}

      //anchors.fill: parent
      // height = paintedHeight
      color: 'black'
      font.pixelSize: 14
      font.family: 'MS Gothic'
      //font.bold: true
      //onAccepted: root_.returnPressed()

      //onTextChanged:
      //  if (text.length > root_.maximumLength && root_.maximumLength >=0)
      //    text = text.substr(0, root_.maximumLength)
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

  //Plugin.TextManagerProxy { id: textManager_ }

  Desktop.Menu { id: menu_
    Desktop.MenuItem {
      text: Sk.tr("Copy")
      shortcut: "Ctrl+C"
      onTriggered: {
        if (!textEdit_.selectedText)
          textEdit_.selectAll()
        textEdit_.copy()
      }
    }

    Desktop.MenuItem {
      text: Sk.tr("Select All")
      shortcut: "Ctrl+A"
      onTriggered: textEdit_.selectAll()
    }

    Desktop.MenuItem {
      text: Sk.tr("Read")
      onTriggered: bean_.read()
    }
  }

 Desktop.TooltipArea { id: toolTip_
   anchors.fill: parent
   text: Sk.tr("Context") + " (" + Sk.tr("read-only") + ")"
 }

  MouseArea { id: mouse_
    anchors.fill: parent
    acceptedButtons: Qt.RightButton
    onPressed: {
      //var gp = Util.itemGlobalPos(parent)
      var gp = mapToItem(null, x + mouse.x, y + mouse.y)
      menu_.showPopup(gp.x, gp.y)
    }
  }
}

/** textarea.qml
 *  9/7/2014 jichi
 *  Only scroll vertically.
 */

import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import '../../../js/sakurakit.min.js' as Sk
import '../../../components' as Components

Item { id: root_
  property alias textEdit: textEdit_
  property bool menuEnabled: true

  signal copyTriggered

  // - Private -

  Flickable { id: scrollArea_
    anchors.fill: parent

    //height: Math.min(_MAX_HEIGHT, textEdit_.paintedHeight)
    //width: textEdit_.width

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
      //anchors.fill: parent
      anchors.centerIn: parent
      width: parent.width
      //readOnly: true

      selectByMouse: true // conflicts with flickable
      //font.pixelSize: 16 //* root_._zoomFactor

      // Disable rich text, so that we can tell if TextEdit is empty
      //textFormat: TextEdit.RichText

      //wrapMode: TextEdit.WordWrap
      //verticalAlignment: TextEdit.AlignTop
      //horizontalAlignment: TextEdit.AlignLeft

      //focus: false
      //color: 'snow'

      //font.family: Util.fontFamilyForLanguage(root_.language)
      //font.family: 'DFGirl'

      //font.italic: Util.isLatinLanguage(root_.language)

      // Not working, which cause textedit width to shrink
      //onTextChanged: width = Math.min(_MAX_WIDTH, paintedWidth)

      //onLinkActivated: Qt.openUrlExternally(link)

      //effect: Share.TextEffect {
      //  highlight: toolTip_.containsMouse
      //  color: highlight ? 'red' :
      //         (comment && comment.color) ? comment.color :
      //         root_.effectColor
      //}
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

  Desktop.Menu { id: menu_
    Desktop.MenuItem { //id: copyAct_
      text: Sk.tr("Copy")
      shortcut: "Ctrl+C"
      onTriggered: root_.copyTriggered()
    }
  }

  MouseArea { id: mouse_
    anchors.fill: parent
    //hoverEnabled: true
    acceptedButtons: Qt.RightButton
    //onEntered: item_.show()
    //onExited: item_.show() // bypass restart timer issue
    onPressed:
      if (root_.menuEnabled) {
        //var gp = Util.itemGlobalPos(parent)
        var gp = mapToItem(null, x + mouse.x, y + mouse.y)
        menu_.showPopup(gp.x, gp.y)
      }
  }
}

/** inputbox.qml
 *  10/21/2012 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import '../../../js/sakurakit.min.js' as Sk

Rectangle { id: root_
  property alias text: textInput_.text
  property alias font: textInput_.font
  property alias placeholderText: placeholder_.text
  property alias toolTip: toolTip_.text
  property alias activeFocus: textInput_.activeFocus
  property alias hover: toolTip_.containsMouse
  property alias maximumLength: textInput_.maximumLength

  signal accepted

  implicitWidth: 400
  implicitHeight: textInput_.height + 5

  // - Private -

  //radius: 10
  //gradient: Gradient {  // color: aarrggbb
  //  GradientStop { position: 0.0;  color: '#8c8f8c8c' }
  //  GradientStop { position: 0.17; color: '#6a6a6d6a' }
  //  GradientStop { position: 0.77; color: '#3f3f3f3f' }
  //  GradientStop { position: 1.0;  color: '#6a6a6d6a' }
  //}

  TextInput { id: textInput_
    anchors {
      left: parent.left
      right: parent.right
      verticalCenter: parent.verticalCenter
      leftMargin: 5; rightMargin: 5
    }

    selectByMouse: true
    //focus: true

    color: '#4a4b4d'
    font.pixelSize: 20
    //font.bold: true
    //font.italic: true
    onAccepted: root_.accepted()

    //onTextChanged:
    //  if (text.length > root_.maximumLength && root_.maximumLength >=0)
    //    text = text.substr(0, root_.maximumLength)

    Text { id: placeholder_
      anchors.fill: parent
      anchors.topMargin: 2
      color: '#7f8185'
      //font: textInput_.font
      font.italic: parent.font.italic
      font.pixelSize: Math.max(1, parent.font.pixelSize - 2)

      //visible: !textInput_.activeFocus && !textInput_.text
      visible: !textInput_.text
    }

    Rectangle {
      anchors.fill: parent
      //anchors.margins: -8
      z: -1
      //radius: 15
      border.width: textInput_.activeFocus ? 1 : 0
      border.color: '#aaffffff'

      //gradient: Gradient {  // color: aarrggbb
      //  //GradientStop { position: 0.0;  color: '#9c8f8c8c' }
      //  //GradientStop { position: 0.17; color: '#7a6a6d6a' }
      //  //GradientStop { position: 0.77; color: '#4f3f3f3f' }
      //  //GradientStop { position: 1.0;  color: '#7a6a6d6a' }
      //  GradientStop { position: 0.0;  color: '#ec8f8c8c' }
      //  GradientStop { position: 0.17; color: '#ca6a6d6a' }
      //  GradientStop { position: 0.77; color: '#9f3f3f3f' }
      //  GradientStop { position: 1.0;  color: '#ca6a6d6a' }
      //}
    }
  }

  // - Context Menu -

  Desktop.Menu { id: menu_
    Desktop.MenuItem {
      text: Sk.tr("Copy")
      //shortcut: "Ctrl+C"
      onTriggered: {
        textInput_.selectAll()
        if (textInput_.selectedText)
          textInput_.copy()
      }
    }
    Desktop.MenuItem {
      text: Sk.tr("Paste")
      shortcut: "Ctrl+V"
      onTriggered: textInput_.paste()
    }
    Desktop.MenuItem {
      text: Sk.tr("Cut")
      //shortcut: "Ctrl+X"
      onTriggered: {
        textInput_.selectAll()
        if (textInput_.selectedText)
          textInput_.cut()
      }
    }
    Desktop.MenuItem {
      text: Sk.tr("Clear")
      //shortcut: "Ctrl+X"
      onTriggered: textInput_.text = ""
    }
  }

  Desktop.TooltipArea { id: toolTip_
    anchors.fill: parent
  }

  MouseArea {
    anchors.fill: parent
    acceptedButtons: Qt.RightButton
    onPressed: {
      //var gp = Util.itemGlobalPos(parent)
      var gp = mapToItem(null, x + mouse.x, y + mouse.y)
      menu_.showPopup(gp.x, gp.y)
    }
  }
}

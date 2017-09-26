/** inputbar.qml
 *  10/21/2012 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
//import QtEffects 1.0 as Effects
import '../../../js/sakurakit.min.js' as Sk
import '.' as Share

Rectangle { id: root_
  property alias text: textInput_.text
  property alias font: textInput_.font
  property alias placeholderText: placeholder_.text
  property alias placeholderColor: placeholder_.color
  //property alias rightPlaceholderText: rightPlaceholder_.text
  property alias activeFocus: textInput_.activeFocus
  property alias maximumLength: textInput_.maximumLength
  property alias hover: toolTip_.containsMouse
  property alias toolTip: toolTip_.text

  signal accepted

  width: 400
  height: textInput_.height + 16

  property int textLeftMargin: 8
  property int textRightMargin: 8

  radius: 10
  //radius: 0 // flat

  //radius: 12
  //radius: 4

  property color borderColor
  //property alias effectColor: effect_.color
  property int borderWidth: 1

  // - Private -

  property bool active: textInput_.activeFocus || root_.hover
  Rectangle { id: border_
    anchors.fill: parent
    radius: parent.radius
    border.width: root_.borderWidth
    border.color: root_.borderColor
    color: 'transparent'

    //effect: Effects.DropShadow { id: effect_
    //  blurRadius: 4
    //  offset: '0,0'
    //}

    states: [
      State { // default
        when: !root_.active
        PropertyChanges { target: root_
          //borderWidth: 1
          color: '#aaffffff'
          //effectColor: '#ffffaa' // yellow
          //effectColor: '#2d5f5f' // dark green
          //borderColor: '#55ffffaa'  // yellow
          borderColor: '#33555555'  // gray
          placeholderColor: '#aa555555'
        }
      }
      , State { // active
        when: root_.active
        PropertyChanges { target: root_
          //borderWidth: 1
          color: '#ddffffff'
          //effectColor: '#52a8ec'
          //borderColor: Qt.rgba(82, 168, 236, 0.8) // blue, from bootstrap
          //borderColor: '#9952a8ec' // blue
          //borderColor: '#99ffffaa' // yellow
          borderColor: '#cc555555' // gray
          placeholderColor: '#555555'
        }
      }
    ]
    transitions: Transition { ColorAnimation {} }
  }

  TextInput { id: textInput_
    anchors {
      left: parent.left; right: parent.right
      verticalCenter: parent.verticalCenter
      leftMargin: textLeftMargin; rightMargin: textRightMargin
    }
    //focus: true
    selectByMouse: true
    //color: '#555555'
    //font.pixelSize: 16
    font.pixelSize: 12
    //font.bold: true
    onAccepted: root_.accepted()

    //onTextChanged:
    //  if (text.length > root_.maximumLength && root_.maximumLength >=0)
    //    text = text.substr(0, root_.maximumLength)

    effect: Share.TextEffect {}

    Text { id: placeholder_
      anchors.fill: parent
      //color: '#88ddf5ee'
      //color: '#999999'
      //color: '#555555'
      font: textInput_.font
      //visible: !textInput_.activeFocus && !textInput_.text
      visible: !textInput_.text
    }

    //Text { id: rightPlaceholder_
    //  anchors.fill: parent
    //  color: '#88ddf5ee'
    //  font: textInput_.font
    //  horizontalAlignment: Text.AlignRight
    //  //visible: !textInput_.activeFocus && !textInput_.text
    //  visible: !textInput_.text
    //}
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

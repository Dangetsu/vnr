/** commentedit.qml
 *  10/21/2012 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
//import '../../../imports/qmlhelper' as Helper
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/util.min.js' as Util
import '../../../components' as Components
import '../../../components/qt5' as Qt5

Item { id: root_

  property alias text: textEdit_.text
  property bool acceptsReturn
  property bool acceptsShiftReturn
  property bool lockComments
  property string submitType
  //property bool popupEnabled
  property alias spellCheckEnabled: spell_.enabled

  //property alias placeholderText: placeholder_.text

  //function addTag(tag) {
  //  if (!~textEdit_.text.indexOf(tag))
  //    textEdit_.text = tag + " " + textEdit_.text
  //}

  // Slots
  // - submit()

  // - Private -

  property int _GUEST_USER_ID: 4

  function typeName(type) {
    switch (type) {
    case 'danmaku': return Sk.tr("danmaku")
    case 'comment': return Sk.tr("comment")
    case 'subtitle': return Sk.tr("subtitle")
    case 'popup': return My.tr("note")
    default: return type
    }
  }

  //border.width: textEdit_.activeFocus ? 1 : 0
  //border.color: '#aaffffff'

  //color: '#f1f1f3'

  //gradient: Gradient {  // color: aarrggbb
  //  GradientStop { position: 0.0;  color: '#eeeff2' }
  //  //GradientStop { position: 0.17; color: '#6a6d6a' }
  //  //GradientStop { position: 0.77; color: '#3f3f3f' }
  //  GradientStop { position: 1.0;  color: '#f1f1f3' }
  //}

  //gradient: Gradient {
  //  GradientStop { position: 0.0;  color: '#c8c9d0' }
  //  GradientStop { position: 0.17; color: '#dfdfe3' }
  //  GradientStop { position: 0.77; color: '#f1f1f3' }
  //  GradientStop { position: 1.0;  color: '#f0f0f3' }
  //}

  //Image {
  //  anchors.fill: parent
  //  fillMode: Image.Tile
  //  source: 'image://rc/texture-black'
  //  z: -1
  //}

  clip: true

  Flickable { id: scrollArea_
    anchors {
      fill: parent
      topMargin: 3
      leftMargin: 9; rightMargin: 9
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
      wrapMode: TextEdit.Wrap
      focus: true
      selectByMouse: true

      onCursorRectangleChanged: scrollArea_.ensureVisible(cursorRectangle)

      Plugin.SpellChecker { id: spell_
        document: textEdit_.getTextDocument()
        language: Util.spellSupportsLanguage(status_.userLanguage) ? status_.userLanguage : 'en'
        enabled: true
      }

      //anchors.fill: parent
      // height = paintedHeight
      color: 'black'
      font.pixelSize: 18
      //font.bold: true
      //onAccepted: root_.returnPressed()

      //onTextChanged:
      //  if (text.length > root_.maximumLength && root_.maximumLength >=0)
      //    text = text.substr(0, root_.maximumLength)

      Keys.onPressed: {
        // ENTER || SHIFT+ENTER
        if ((event.key === Qt.Key_Return || event.key === Qt.Key_Enter) && (
            root_.acceptsReturn ||
            event.modifiers === Qt.ShiftModifier)) {
          event.accepted = true
          var ok = root_.submit()
          if (root_.acceptsShiftReturn && event.modifiers === Qt.ShiftModifier) {
            if (ok)
              game_.postReturnLater()
            else
              game_.postReturn()
          }
        }
      }

      Text { id: placeholder_
        anchors.fill: parent
        color: '#7F8185'
        //font: textEdit_.font
        font.italic: textEdit_.font.italic
        font.pixelSize: Math.max(1, textEdit_.font.pixelSize - 2)

        //visible: !textEdit_.activeFocus && !textEdit_.text
        visible: !textEdit_.text
        wrapMode: Text.Wrap

        text: {
          var type = typeName(root_.submitType)
          var ret = qsTr("Type {0} here").replace('{0}', type)
          //ret += " (" + qsTr("bBCode supported") + ")"
          ret += " ... "
          if (root_.acceptsReturn)
            ret += qsTr("Enter to submit, or") + " "
          if (root_.acceptsShiftReturn)
            ret += qsTr("Shift+Enter to submit and forward game")
          else
            ret += qsTr("Shift+Enter to submit")
          return ret
        }
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

  //Helper.QmlHelper { id: qmlhelper_ }

  Plugin.TextManagerProxy { id: textManager_ }

  Plugin.GameProxy { id: game_ }

  Plugin.SystemStatus { id: status_ }

  //Share.TextButton { id: typeButton_
  //  anchors {
  //    right: parent.right
  //    verticalCenter: parent.verticalCenter
  //    rightMargin: 4
  //  }
  //  width: 60; height: parent.height
  //  font.pixelSize: 10
  //  font.bold: true
  //  //align: 'right'
  //  text: state === 'subtitle' ? qsTr("Subtitle") : qsTr("Comment")

  //  onClicked: toggleState()

  //  //states: [
  //  //  State { name: 'subtitle'
  //  //    PropertyChanges { target: typeButton_; backgroundColor: '#aaff33cc' }
  //  //  },
  //  //  State { name: 'comment';
  //  //    PropertyChanges { target: typeButton_; backgroundColor: '#aa00bfff' }
  //  //  }
  //  //]
  //  backgroundColor: state === 'subtitle' ? '#aaff33cc' : '#aa00bfff' // magenta : deep sky blue

  //  state: 'subtitle'

  //  function toggleState() {
  //    switch (state) {
  //      case 'subtitle': state = 'comment'; break
  //      case 'comment': state = 'subtitle'; break
  //    }
  //  }
  //}

  //Share.TextButton { id: submitButton_
  //  anchors {
  //    right: parent.right
  //    verticalCenter: parent.verticalCenter
  //    rightMargin: 10
  //  }
  //  width: 80; height: parent.height
  //  font.pixelSize: 16
  //  backgroundColor: '#aaff33cc'
  //  //align: 'right'
  //  text: qsTr("Submit")
  //  onClicked: root_.submit()
  //}

  //onAccepted: submit()

  ///  @return  bool  if ok
  function submit() {
    var t = Util.trim(textEdit_.text)
    if (t) {
      var locked = status_.userId !== _GUEST_USER_ID && lockComments
      var ok = textManager_.submitComment(t, submitType, locked)
      if (ok)
        textEdit_.text = ""
      return ok
    } else
      return false
  }

  Desktop.Menu { id: menu_
    Desktop.MenuItem {
      text: Sk.tr("Copy")
      shortcut: "Ctrl+C"
      onTriggered: {
        textEdit_.selectAll()
        if (textEdit_.selectedText)
          textEdit_.copy()
      }
    }

    Desktop.MenuItem {
      text: Sk.tr("Paste")
      shortcut: "Ctrl+V"
      onTriggered: textEdit_.paste()
    }
    Desktop.MenuItem {
      text: Sk.tr("Cut")
      shortcut: "Ctrl+X"
      onTriggered: {
        textEdit_.selectAll()
        if (textEdit_.selectedText)
          textEdit_.cut()
      }
    }
    Desktop.MenuItem {
      text: Sk.tr("Select All")
      shortcut: "Ctrl+A"
      onTriggered: textEdit_.selectAll()
    }
    Desktop.MenuItem {
      text: Sk.tr("Clear")
      //shortcut: "Ctrl+X"
      onTriggered: textEdit_.text = ""
    }
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

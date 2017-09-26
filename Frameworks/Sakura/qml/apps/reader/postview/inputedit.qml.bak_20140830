/** inputedit.qml
 *  2/22/2014 jichi
 */
import QtQuick 1.1
//import QtDesktop 0.1 as Desktop
import '../../../js/ajax.min.js' as Ajax
import '../../../js/define.min.js' as Define
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/util.min.js' as Util
import '../../../components' as Components
import '../../../components/bootstrap3' as Bootstrap

Item { id: root_

  property alias text: textEdit_.text

  // - Private -

  property string postUrl: Define.DOMAIN_COM + '/api/json/post/create'
  //property string postUrl: 'http://sakurakit.com/api/json/post/create'
  //property string postUrl: 'http://localhost:8080/api/json/post/create'
  property string topicKey

  clip: true

  Flickable { id: scrollArea_
    anchors {
      //fill: parent
      topMargin: 3; bottomMargin: 3
      leftMargin: 9; rightMargin: 9

      left: parent.left; right: parent.right
      top: parent.top
      bottom: footer_.top
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

    TextEdit { id: textEdit_
      //anchors.centerIn: parent
      width: parent.width
      wrapMode: TextEdit.Wrap
      focus: true
      selectByMouse: true

      onCursorRectangleChanged: scrollArea_.ensureVisible(cursorRectangle)

      //anchors.fill: parent
      // height = paintedHeight
      color: 'black'
      font.pixelSize: 14
      //font.bold: true
      //onAccepted: root_.returnPressed()


      Keys.onPressed:
        // SHIFT+ENTER
        if (event.modifiers === Qt.ShiftModifier &&
            (event.key === Qt.Key_Return || event.key === Qt.Key_Enter)) {
          event.accepted = true
          root_.submit()
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

        text: qsTr("Shift+Enter to submit")
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

  Row { id: footer_
    anchors {
      left: parent.left; right: parent.right
      bottom: parent.bottom
      //margins: 10
      rightMargin: 5
    }
    layoutDirection: Qt.RightToLeft
    spacing: 5

    Bootstrap.Button { id: submitButton_
      styleClass: 'btn btn-primary'
      //width: 40
      text: Sk.tr("Submit")
      toolTip: Sk.tr("Submit")
      onClicked: root_.submit()
    }

    Bootstrap.Button { id: browseButton_
      styleClass: 'btn btn-default'
      //width: 40
      text: Sk.tr("Browse")
      toolTip: My.tr("Open in external browser")
      onClicked: Qt.openUrlExternally("http://sakuradite.com/topic/51")
    }
  }

  function submit() {
    console.log("postview.qml:inputedit: submit")
    var t = Util.trim(textEdit_.text)
    if (t) {
      var user = statusPlugin_.userName
      var pass = statusPlugin_.userPassword
      if (user && pass) {
        root_.lastText = t
        textEdit_.text = ''
        send(t, user, pass)
      }
    }
  }

  property string lastText // back up last text

  function send(content, userName, password) { // string, string, string
    Ajax.postJSON(root_.postUrl, {
      login: userName
      , password: password
      , topic: topicKey
      , content: content
    }, function (obj) {
      if (obj.status)
        sendError()
    }, sendError)
  }

  function sendError() {
    growlPlugin_.warn(qsTr("I am sorry that I am failed to save the changes")
        + '<br/>' +
        qsTr("Something might be wrong with the Internet connection"))
    if (!Util.trim(textEdit_.text) && root_.lastText)
      textEdit_.text = root_.lastText
  }
}

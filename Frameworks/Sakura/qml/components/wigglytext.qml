/** wigglytext.qml
 *  9/30/2012 jichi
 *  See: animations from Qt 4.8
 */
import QtQuick 1.1
import '../imports/qmleffects' as Effects

Item { id: root_

  property string text: "Text is not set"
  property bool animated: true

  //property color pressColor: 'magenta'
  property color pressColor: '#2d5f5f'

  //property color releaseColor: 'deepskyblue'
  property color releaseColor: 'orange'

  Keys.onPressed: {
    if (event.key === Qt.Key_Delete || event.key === Qt.Key_Backspace)
      root_.remove()
    else if (event.text !== '') {
      root_.append(event.text)
    }
  }

  function append(text) {
    root_.animated = false
    var lastLetter = root_.children[root_.children.length - 1]
    var newLetter = letterComponent_.createObject(root_)
    newLetter.text = text
    newLetter.follow = lastLetter
    root_.animated = true
  }

  function remove() {
    if (root_.children.length)
      root_.children[root_.children.length - 1].destroy()
  }

  function doLayout() {
    var follow = null
    for (var i = 0; i < root_.text.length; ++i) {
      var newLetter = letterComponent_.createObject(root_)
      newLetter.text = root_.text[i]
      newLetter.follow = follow
      follow = newLetter
    }
  }

  Component { id: letterComponent_
    Text { id: letter_
      property variant follow

      x: follow ? follow.x + follow.width : root_.width / 3
      y: follow ? follow.y : root_.height / 2

      font.pixelSize: 30; font.bold: true
      color: 'snow'

      style: Text.Raised
      styleColor: root_.releaseColor

      effect: Effects.TextShadow {
        blurRadius: 8
        offset: '1,1'
        color: 'red'
      }

      MouseArea {
        anchors.fill: parent
        drag.target: letter_; drag.axis: Drag.XandYAxis
        onPressed: { letter_.styleColor = root_.pressColor }
        onReleased: { letter_.styleColor = root_.releaseColor }
      }

      Behavior on x { enabled: root_.animated; SpringAnimation { spring: 3; damping: 0.3; mass: 1.0 } }
      Behavior on y { enabled: root_.animated; SpringAnimation { spring: 3; damping: 0.3; mass: 1.0 } }
    }
  }

  Component.onCompleted: doLayout()
}

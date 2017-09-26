/** switchbutton.qml
 *  11/19/2012 jichi
 */
import QtQuick 1.1
import '../../../components/slideswitch' as Components

Item { id: root_
  property alias checked: switch_.checked
  property alias text: text_.text
  property alias font: text_.font

  // - Private -
  Components.SlideSwitch { id: switch_
    anchors {
      left: parent.left
      verticalCenter: parent.verticalCenter
      margins: 10
    }
    width: 130; height: 56
  }

  Text { id: text_
    anchors {
      left: switch_.right
      right: parent.right
      verticalCenter: parent.verticalCenter
      margins: 10
    }
    style: Text.Sunken
    color: 'snow'
    font.strikeout: !switch_.checked
    //font.bold: true
    //font.italic: true
    wrapMode: Text.Wrap
  }
}

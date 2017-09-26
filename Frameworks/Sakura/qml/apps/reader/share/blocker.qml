/** blocker.qml
 *  6/8/2013 jichi
 */
import QtQuick 1.1
import '../../../js/sakurakit.min.js' as Sk

Rectangle {

  property alias textColor: text_.color
  property alias text: text_.text

  // - Private -

  color: '#99ffffff'

  Text { id: text_
    anchors.centerIn: parent
    textFormat: Text.PlainText
    color: 'gray'
    //font.bold: true
    font.pixelSize: 40
    font.family: 'DFGirl'

    text: Sk.tr("Empty") + "! ><"
  }
}

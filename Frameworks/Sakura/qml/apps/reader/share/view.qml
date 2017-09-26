/** view.qml
 *  6/1/2013 jichi
 *  Window view.
 */
import QtQuick 1.1

Item { id: root_
  property int windowFlags: Qt.Dialog | Qt.WindowMinMaxButtonsHint

  Image {
    anchors.fill: parent
    fillMode: Image.Tile
    source: 'image://rc/background'
    z: -1
  }
}

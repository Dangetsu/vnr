/** gamecoverimage.qml
 *  2/21/2013 jichi
 */
import QtQuick 1.1

Image { id: root_

  property int gameId // itemId
  property int fileId // tokenId

  // - Private -

  property string url: (!gameId && !fileId) ? '' : datamanPlugin_.queryGameImage(fileId, gameId)

  fillMode: Image.PreserveAspectFit

  //clip: true
  //fillMode: Image.Stretch
  //visible: status == Image.Ready

  //sourceSize: Qt.size(50, 50) // small: 50x50

  visible: !!source && status === Image.Ready

  asynchronous: !!url && url.indexOf('http://') === 0
  source: url

  MouseArea {
    acceptedButtons: Qt.LeftButton
    anchors.fill: parent
    onClicked: if (root_.fileId) mainPlugin_.showGameView(root_.fileId)
  }
}

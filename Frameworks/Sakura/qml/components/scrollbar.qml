/** scrollbar.qml
 *  9/30/2012 jichi
 *  See: ui-components from Qt 4.8
 *  See: http://projects.developer.nokia.com/qmluiexamples/browser/qml/qmluiexamples?rev=11
 *  See: svn co https://projects.developer.nokia.com/svn/qmluiexamples
 */
import QtQuick 1.1

Item { id: root_

  // The properties that define the scrollbar's state.
  // position and pageSize are in the range 0.0 - 1.0.  They are relative to the
  // height of the page, i.e. a pageSize of 0.5 means that you can see 50%
  // of the height of the view.
  // orientation can be either Qt.Vertical or Qt.Horizontal
  property real position
  property real pageSize
  property int orientation : Qt.Vertical  // { Qt.Vertical, Qt.Horizontal }

  // - Private -

  clip: true

  // A light, semi-transparent background
  Rectangle {
    anchors.fill: parent
    radius: orientation === Qt.Vertical ? (width/2 - 1) : (height/2 - 1)
    color: 'white'
    opacity: 0.3
  }

  // Size the bar to the required size, depending upon the orientation.
  Rectangle {
    x: orientation === Qt.Vertical ? 1 : (root_.position * (root_.width-2) + 1)
    y: orientation === Qt.Vertical ? (root_.position * (root_.height-2) + 1) : 1
    width: orientation === Qt.Vertical ? (parent.width-2) : (root_.pageSize * (root_.width-2))
    height: orientation === Qt.Vertical ? (root_.pageSize * (root_.height-2)) : (parent.height-2)
    radius: orientation === Qt.Vertical ? (width/2 - 1) : (height/2 - 1)
    color: 'black'
    opacity: 0.7
  }
}

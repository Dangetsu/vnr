/** centralarea.qml
 *  10/10/2012 jichi
 */
import QtQuick 1.1

Rectangle { id: root_
  implicitWidth: 800; implicitHeight: 600
  property bool borderVisible: false

  // - Private -
  color: 'transparent'
  z: -1

  border.width: borderVisible ? 2 : 0
  border.color: '#aaff0000'

  //Component.onCompleted: console.log("kagami:centralarea.qml: pass")
}

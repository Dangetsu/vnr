/** text.qml
 *  6/27/2014 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
//import '../components/buttongroup' as ButtonGroup

Item {
  implicitWidth: 250; implicitHeight: 400

  // - Private -

  Desktop.TextArea {
    anchors.centerIn: parent
  }
}

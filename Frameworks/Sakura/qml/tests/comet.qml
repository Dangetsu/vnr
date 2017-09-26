/** comet.qml
 *  3/4/2014 jichi
 */
import QtQuick 1.1
import '../apps/reader/comet' as Comet

Item {
  implicitWidth: 250; implicitHeight: 400

  // - Private -

  Comet.GlobalComet {
    active: true
    onConnectionCountChanged:
      console.log("connection count changed:", connectionCount)
  }
}

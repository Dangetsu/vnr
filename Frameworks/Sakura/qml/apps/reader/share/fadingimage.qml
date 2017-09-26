/** fadingimage.qml
 *  11/2/2013 jichi
 */
import QtQuick 1.1
import '.' as Share

Item { //id: root_

  property alias source: in_.source
  property alias sourceSize: in_.sourceSize
  property alias fillMode: in_.fillMode
  property alias asynchronous: in_.asynchronous
  property alias fadingDuration: in_.fadingDuration

  // - Private -

  Share.FadeOutImage { //id: out_
    anchors.fill: in_
    sourceSize: in_.sourceSize
    fillMode: in_.fillMode
    asynchronous: in_.asynchronous
    z: in_.z -1
    visible: !!source
    source: in_.previousSource

    fadingDuration: in_.fadingDuration
  }

  Share.FadeInImage { id: in_
    anchors.fill: parent
    visible: !!source
    z: parent.z
    asynchronous: false  // only load local source file, or it might cause loop binding issue

    fadingDuration: 1000

    onSourceChanged: {
      previousSource = currentSource
      currentSource = source
    }
    property string previousSource
    property string currentSource
  }
}

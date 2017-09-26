/** globalcomet.qml
 *  3/4/2014 jichi
 */
import QtQuick 1.1
import '.' as Comet

Comet.PostDataComet { //id: root_

  // http://developer.nokia.com/community/wiki/Using_objectName_to_find_QML_elements_from_Qt
  objectName: 'globalComet' // Use objectName to communicate with C++

  path: 'global'

  // Require SystemStatus plugin
  active: statusPlugin_.online
}

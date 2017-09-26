/** termcomet.qml
 *  2/21/2014 jichi
 */
import QtQuick 1.1
import '.' as Comet

Comet.PostComet { //id: root_
  objectName: 'termComet' // Use objectName to communicate with C++

  // - Private -

  path: 'topic/term'
}

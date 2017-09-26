/** postcomet.qml
 *  2/21/2014 jichi
 */
import QtQuick 1.1
import '.' as Comet

Comet.Comet { id: root_

  property int connectionCount
  signal postReceived(variant obj)
  signal postUpdated(variant obj)
  signal topicReceived(variant obj)
  signal topicUpdated(variant obj)

  // - Private -

  onMessage: {
    var obj
    try { obj = JSON.parse(data) } // may throw if server return wrong string
    catch (e) {
      console.log("postcomet.qml: JSON error", data)
      return
    }
    // No idea why switch-case does not work here ...
    if (obj.type === 'count')
      root_.connectionCount = Number(obj.data) // may becomes NaN
    else if (obj.type === 'post') {
      if (obj.data.id)
        root_.postReceived(obj.data)
    } else if (obj.type === 'post/update') {
      if (obj.data.id)
        root_.postUpdated(obj.data)
    } else if (obj.type === 'topic') {
      if (obj.data.id)
        root_.topicReceived(obj.data)
    } else if (obj.type === 'topic/update') {
      if (obj.data.id)
        root_.topicUpdated(obj.data)
    } else
      console.log("postcomet.qml:onMessage: unknown data type:", obj.type)
  }
}

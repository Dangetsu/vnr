/** postdatacomet.qml
 *  3/4/2014 jichi
 */
import QtQuick 1.1
import '.' as Comet

Comet.PostComet { //id: root_

  signal postDataReceived(string obj)
  signal postDataUpdated(string obj)
  signal topicDataReceived(string obj)
  signal topicDataUpdated(string obj)

  // - Private -

  onPostReceived: postDataReceived(JSON.stringify(obj))
  onPostUpdated: postDataUpdated(JSON.stringify(obj))
  onTopicReceived: topicDataReceived(JSON.stringify(obj))
  onTopicUpdated: topicDataUpdated(JSON.stringify(obj))
}

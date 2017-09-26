/** comet.qml
 *  2/21/2014 jichi
 */
import QtQuick 1.1
import '../../../js/atmosphere.min.js' as Atmosphere
import '../../../js/define.min.js' as Define
import '../../../js/local.js' as Local // Local.comet

QtObject { id: root_

  property string path
  //string path: 'topic/term'

  property bool active

  signal message(string data)

  // Expose to C++, since connect/disconnect names are already taken by QObject
  // http://stackoverflow.com/questions/18712095/how-to-call-a-qml-function-from-c-in-bb10
  //function start() { connect() }
  //function stop() { disconnect() }

  // - Private -

  property string url: Define.DOMAIN_COM + '/push/vnr/' + path
  //property string url: 'http://localhost:8080/push/vnr/' + path

  property QtObject reconnectTimer: Timer {
    interval: 5000 // 5 seconds
    repeat: false
    onTriggered:
      if (root_.active && Local.comet)
        Local.comet.reconnect()
    //onRunningChanged: console.log("timer: running = ", running)
  }

  Component.onCompleted: if (active) connect()
  Component.onDestruction: disconnect()

  onActiveChanged:
    if (active) connect()
    else disconnect()

  onPathChanged:
    if (Local.comet && Local.comet.url != root_.url) {
      if (active) {
        destroyComet()
        connect()
      } else
        Local.comet = undefined
    }

  function connect() {
    if (!Local.comet)
      createComet()
    console.log("comet.qml:connect: path =", root_.path)
    Local.comet.connect()
  }

  function disconnect() {
    if (Local.comet) {
      console.log("comet.qml:disconnect: path =", root_.path)
      Local.comet.disconnect()
    }
  }

  function createComet() {
    //console.log("comet.qml:createComet: path =", root_.path)
    var comet = Local.comet = Atmosphere.subscribe(root_.url)
    comet.reconnectTimer = reconnectTimer
    comet.onMessage = function (xhr, data) {
      if (data) root_.message(data)
    }
    comet.onError = function (xhr, msg) {
      console.log("comet.qml: error: path =", root_.path, msg)
    }
    comet.onReconnect = function (xhr) {
      console.log("comet.qml: reconnect: path =", root_.path)
    }
  }

  function destroyComet() {
    if (Local.comet) {
      console.log("comet.qml:destroyComet: path =", root_.path)
      Local.comet.disconnect()
      Local.comet = undefined
    }
  }

}

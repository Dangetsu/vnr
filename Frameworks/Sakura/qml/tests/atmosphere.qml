/** atmosphere.qml
 *  2/21/2014 jichi
 */
import QtQuick 1.1
//import '../js/ajax.js' as Ajax
import '../js/atmosphere.js' as Atmosphere
import '../js/global.js' as Global

Item { id: root_
  implicitWidth: 250; implicitHeight: 400

  // - Private -

  Timer { id: reconnectTimer_
    onRunningChanged: console.log("timer: running = ", running)

    interval: 5000 // 5 seconds
    repeat: false
    onTriggered: Global.comet.reconnect()
  }

  Component.onCompleted: {
    //var url = "http://localhost:8080/push/vnr/topic/term"
    Atmosphere.DEBUG = true;
    var url = 'http://sakuradite.com/push/vnr/topic/term'
    var comet = Global.comet = Atmosphere.subscribe(url)
    comet.reconnectTimer = reconnectTimer_

    //var url = "http://localhost:8080/push/vnr/topic/term"
    comet.onError = function (xhr, msg) { console.log(msg) }
    comet.onMessage = function (xhr, data) { console.log(data) }
    comet.onConnect = function (xhr) { console.log("connect: pass") }
    comet.onDisconnect = function (xhr) { console.log("disconnect: pass") }
    comet.onReconnect = function (xhr) { console.log("reconnect: pass") }
    var xhr = comet.connect()
    //comet.push("revive")
    //comet.disconnect()
    console.log("onCompleted: pass")
  }

  Component.onDestruction: Global.comet.disconnect()
}

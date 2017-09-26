/** globalcomet.qml
 *  3/4/2014 jichi
 */
import QtQuick 1.1
import '../../../js/global.js' as Global // Global.globalCometClients  [QML objects]

QtObject { id: root_

  property bool active // read-only
  property int connectionCount
  signal postReceived(variant obj)
  signal postUpdated(variant obj)

  // Require statusPlugin_ to be created
  //Plugin.SystemStatus { id: statusPlugin_ }

  // - Private -

  Component.onCompleted: subscribe(root_)

  // All following functions are almost stateless

  function subscribe(obj) { // Qt object
    if (Global.globalCometClients)
      Global.globalCometClients.push(obj)
    else {
      Global.globalCometClients = [obj] // first, save list of callback object in comet
      createComet(bindComet)
    }
  }

  function createComet(callback) { // function (comet) ->
    var comp = Qt.createComponent('postcomet.qml')

    function finished() {
      console.log("globalcomet.qml: create finished")
      callback(comp.createObject(root_, {
        path: 'global' // /push/vnr/global
      }))
    }

    //comp = Qt.createComponent('comet.qml');
    console.log("globalcomet.qml: create: status:", comp.status)
    switch (comp.status) {
    case Component.Error:
      console.log("globalcomet.qml: ERROR: failed to create component:", comp.errorString())
      break
    case Component.Ready: // == 1
      finished()
      break
    default:
      comp.statusChanged.connect(finished) // wait
    }
    console.log("globalcomet.qml: create: leave")
  }

  function bindComet(comet) {

    var objs = Global.globalCometClients

    // Bind

    comet.connectionCountChanged.connect(function() {
      var count = comet.connectionCount
      for (var i in objs)
        objs[i].connectionCount = count
    })
    comet.activeChanged.connect(function() {
      var t = comet.active
      for (var i in objs)
        objs[i].active = t
    })

    comet.postReceived.connect(function() {
      for (var i in objs)
        objs[i].postReceived.apply(it, arguments)
    })
    comet.postUpdated.connect(function() {
      for (var i in objs)
        objs[i].postReceived.apply(it, arguments)
    })

    // Detect online, require SystemStatus plugin
    statusPlugin_.onlineChanged.connect(function(t) {
      comet.active = t
    })
    if (statusPlugin_.online)
      comet.active = true
  }
}

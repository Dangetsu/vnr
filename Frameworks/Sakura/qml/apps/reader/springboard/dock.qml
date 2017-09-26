/** dock.qml
 *  9/29/2012 jichi
 *  Launchers
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import '../../../js/eval.min.js' as Eval

/**
 *  Model requirements
 *  - icon
 *  - qml
 */
ListView {

  // - Private -

  // Dragging is disabled anyway
  //boundsBehavior: Flickable.DragOverBounds // no overshoot bounds

  snapMode: ListView.SnapToItem   // move to bounds

  //Component.onCompleted: console.log("springboard:dock.qml: pass")

  delegate: Item { id: delegateItem_
    width: 50; height: 50

    Image { id: image_
      source: model.icon
      smooth: true
      scale: 0.8
    }

    MouseArea { id: mouse_
      anchors.fill: parent
      //hoverEnabled: true
      acceptedButtons: Qt.LeftButton

      onClicked: Eval.evalLink(model.link)
      //if (model.qml !== undefined) {
      //  var q = Qt.createQmlObject(model.qml, delegateItem_, 'dockItemOnClicked')
      //  if (q !== null) { // && 'run' in q) {
      //    console.log('dashboard.qml:runQml: running')
      //    q.run()
      //    console.log('dashboard.qml:runQml: destroying')
      //    q.destroy()
      //    console.log('dashboard.qml:runQml: pass')
      //  }
      //}
    }

    Desktop.TooltipArea { id: toolTip_
      // Note this will eat hover events
      anchors.fill: parent
      text: model.name + ": " + model.toolTip
    }

    property bool active: toolTip_.containsMouse
    states: [
      State { // default
        when: !delegateItem_.active
        PropertyChanges { target: image_; y: 0; scale: 0.8 } // the same as image_ initial values
      }
      , State {
        when: delegateItem_.active
        PropertyChanges { target: image_; y: -7; scale: 1.2 } // dock item magnified size
      }
    ]
    transitions: Transition {
      NumberAnimation { properties: 'scale,y' }
      //SpringAnimation {
      //  properties: 'scale,y'
      //  spring: 3.5; damping: 0.08 // spring: strength; damping: speed
      //}
    }
  }

  // Dock shadow
  Rectangle {
    color: '#60ffffff' // dock color
    anchors { fill: parent; margins: -10 }
    z: -1
    //radius: 10
    radius: 0 // flat
  }
}

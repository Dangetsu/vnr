/** slideswitch.qml
 *  11/19/2012 jichi
 *  See: Qt 4.8.3/declarative/ui-components/slideswitch
 */
import QtQuick 1.1

Item { id: root_

  property bool checked: true

  // - Private -

  property int dragWidth: background_.width - knob_.width

  state: checked ? 'on' : 'off'
  function toggle() { checked = !checked }

  function releaseSwitch() {
    if (knob_.x === 1) {
      if (root_.state === 'off') return
    }
    if (knob_.x === root_.dragWidth) {
      if (root_.state === 'on') return
    }
    toggle()
  }

  Image { id: background_
    width: root_.width; height: root_.height
    source: "background.svg"
    MouseArea { anchors.fill: parent; onClicked: toggle() }
  }

  Image { id: knob_
    x: 1; y: 2
    source: "knob.svg"
    height: Math.max(0, background_.height -4)
    width: height

    MouseArea {
      anchors.fill: parent
      drag.target: knob_; drag.axis: Drag.XAxis; drag.minimumX: 1; drag.maximumX: root_.dragWidth
      onClicked: toggle()
      onReleased: releaseSwitch()
    }
  }

  states: [
    State {
      name: 'on'
      PropertyChanges { target: knob_; x: root_.dragWidth }
      PropertyChanges { target: root_; checked: true }
    },
    State {
      name: 'off'
      PropertyChanges { target: knob_; x: 1 }
      PropertyChanges { target: root_; checked: false }
    }
  ]

  transitions: Transition {
    NumberAnimation { properties: 'x'; easing.type: Easing.InOutQuad; duration: 200 }
  }
}

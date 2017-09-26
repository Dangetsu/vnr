/** drawer.qml
 *  9/30/2012 jichi
 *  Drawer menu, the curtain container.
 */
import QtQuick 1.1
import '.' as SpringBoard

Item { id: root_

  property int drawerHeight: 12
  property int curtainHeight: Math.max(height - drawerHeight, 0)  ///< Max drawer height

  state: 'CLOSED'

  // - Private -
  //Component.onCompleted: console.log("springboard:drawer.qml: pass")

  SpringBoard.Curtain { id: curtain_
    anchors.horizontalCenter: parent.horizontalCenter
    height: root_.curtainHeight; width: root_.width
    z: 1
  }

  Rectangle { id: drawer_
    height: root_.drawerHeight; width: parent.width
    //border { color: 'red'; width: mouse_.containsMouse ? 1 : 0 }
    z: 1
    gradient: Gradient {
      GradientStop { position: 0.0;  color: '#8c8f8c' }
      GradientStop { position: 0.17; color: '#6a6d6a' }
      GradientStop { position: 0.77; color: '#3f3f3f' }
      GradientStop { position: 1.0;  color: '#6a6d6a' }
    }

    Image { id: arrowIcon_
      source: 'image://rc/arrow-down'
      anchors.horizontalCenter: parent.horizontalCenter
      Behavior on rotation {
        NumberAnimation { easing.type: Easing.OutExpo }
      }
    }

    MouseArea { id: mouse_
      anchors.fill: parent
      acceptedButtons: Qt.LeftButton

      //hoverEnabled: true
      //onEntered: parent.border.color = 'red'
      //onExited:  parent.border.color = '#6a6d6a'
      onClicked: root_.toggleState()
    }
  }

  states: [
    State { name: 'OPEN'
      //PropertyChanges { target: textArea; y: curtainHeight + drawer_.height}
      PropertyChanges { target: curtain_; y: 0}
      PropertyChanges { target: drawer_; y: curtainHeight}
      PropertyChanges { target: arrowIcon_; rotation: 180}
    }
    , State { name: 'CLOSED'
      //PropertyChanges { target: textArea; y: drawer_.height; height: root_.height - drawer_.height }
      PropertyChanges { target: curtain_; y:-height; }
      PropertyChanges { target: drawer_; y: 0 }
      PropertyChanges { target: arrowIcon_; rotation: 0 }
    }
  ]

  function toggleState() {
    switch (root_.state) {
      case 'CLOSED': root_.state = 'OPEN'; break
      case 'OPEN': root_.state = 'CLOSED'; break
    }
  }

  transitions: Transition {
    to: '*'
    //NumberAnimation { target: textArea; properties: 'y,height'; duration: 1000; easing.type:Easing.OutExpo }
    NumberAnimation { target: curtain_; property: 'y'; duration: 1000; easing.type: Easing.OutExpo }
    NumberAnimation { target: drawer_; property: 'y'; duration: 1000; easing.type: Easing.OutExpo }
  }
}

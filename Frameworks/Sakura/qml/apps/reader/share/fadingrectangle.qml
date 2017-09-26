/** fadingrectangle.qml
 *  5/22/2013 jichi
 */
import QtQuick 1.1

Rectangle { id: root_

  // - Private -

  states: [
    State { // visible
      when: root_.visible
      PropertyChanges { target: root_
        opacity: 1
      }
    }
    , State { // hidden
      when: !root_.visible
      PropertyChanges { target: root_
        opacity: 0
     }
    }
  ]
  transitions: Transition {
    NumberAnimation { property: 'opacity' }
  }
}

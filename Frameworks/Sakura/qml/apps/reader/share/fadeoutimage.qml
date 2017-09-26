/** fadeoutimage.qml
 *  11/2/2013 jichi
 */
import QtQuick 1.1

Image { id: root_

  property alias fadingDuration: fadeAni_.duration

  property bool fading: false
  function fade() {
    opacity = 1
    fading = false
    fading = true
  }

  // - Private -

  onSourceChanged: if (visible) fade()

  states: State { // visible
    when: root_.fading
    PropertyChanges { target: root_
      opacity: 0
    }
  }

  transitions: Transition {
    NumberAnimation { id: fadeAni_
      property: 'opacity'
      easing.type: Easing.InQuad
    }
  }
}

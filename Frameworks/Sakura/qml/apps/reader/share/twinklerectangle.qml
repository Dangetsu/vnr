/** twinklerectangle.qml
 *  9/14/2014 jichi
 */
import QtQuick 1.1

Rectangle { id: root_

  property int duration: 400 * 2 // two times of jquery interval
  property bool running: false
  property color pauseColor: '#aaff0000' // red
  property color runningColor: '#aa00bfff' // blue
  property color runningColor2: '#aa00ff00' // green

  // - Private -

  onRunningChanged: {
    if (!running)
      state = 'pause'
    else if (state === 'running')
      state = 'running2'
    else
      state = 'running'
  }

  Component.onCompleted:
    if (running) {
      if (state !== 'running')
        state = 'running'
      else
        state = 'running2'
    }

  //Behavior on color { ColorAnimation {} }

  state: 'pause'
  states: [
    State { name: 'pause' // stopped
      PropertyChanges { target: root_
        color: root_.pauseColor
      }
    }
    , State { name: 'running' // twinkling
      PropertyChanges { target: root_
        color: root_.runningColor
      }
    }
    , State { name: 'running2' // twinkling
      PropertyChanges { target: root_
        color: root_.runningColor2
     }
    }
  ]

  //transitions: Transition { ColorAnimation {} }
  transitions: [
    Transition {
      to: 'running2'
      SequentialAnimation {
        ColorAnimation { duration: root_.duration }
        ScriptAction {
          script: if (root_.running) root_.state = 'running'
        }
      }
    }
    , Transition {
      to: 'running'
      SequentialAnimation {
        ColorAnimation { duration: root_.duration }
        ScriptAction {
          script: if (root_.running) root_.state = 'running2'
        }
      }
    }
  ]
}

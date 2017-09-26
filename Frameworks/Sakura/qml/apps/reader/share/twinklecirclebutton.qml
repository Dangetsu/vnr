/** twinklecirclebutton.qml
 *  3/2/2014 jichi
 */
import QtQuick 1.1
import '.' as Share

Share.CircleButton { id: root_

  property int duration: 1000
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

  //Behavior on backgroundColor { ColorAnimation {} }

  state: 'pause'
  states: [
    State { name: 'pause' // stopped
      PropertyChanges { target: root_
        backgroundColor: root_.pauseColor
      }
    }
    , State { name: 'running' // twinkling
      PropertyChanges { target: root_
        backgroundColor: root_.runningColor
      }
    }
    , State { name: 'running2' // twinkling
      PropertyChanges { target: root_
        backgroundColor: root_.runningColor2
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

  //transitions: Transition {
  //  ParallelAnimation {
  //    ColorAnimation {}
  //    //NumberAnimation { property: 'scale'; duration: 100 }
  //    SpringAnimation {
  //      property: 'scale'; duration: 100
  //      spring: 5.0; damping: 0.05 // spring: strength; damping: speed
  //    }
  //  }
  //}

/** twinkle.qml
 *  3/2/2014 jichi
 */
import QtQuick 1.1
import '../apps/reader/share' as Share

Item {
  implicitWidth: 250; implicitHeight: 400

  // - Private -

  //Share.TwinkleCircleButton { id: root_
  //  anchors.centerIn: parent

  //  diameter: 30

  //  font.pixelSize: 12

  //  text: "123"

  //  onClicked: running = !running

  //  //onClicked: toggleState()

  //  function toggleState() {
  //    switch (state) {
  //      case 'pause':
  //        state = 'running'
  //        break
  //      case 'running':
  //      case 'running2':
  //        state = 'pause'
  //        break
  //    }
  //  }

  //  duration: 1000
  //  pauseColor: 'gray'
  //  //pauseColor: '#aaff0000' // red
  //  runningColor: '#aa00bfff' // blue
  //  //runningColor2: '#aa00ff00' // green
  //  runningColor2: 'gray' // green
  //}

  Share.TwinkleRectangle {
    anchors.centerIn: parent
    width: 100
    height: 100

    running: true

    duration: 1000
    pauseColor: 'gray'
    //pauseColor: '#aaff0000' // red
    runningColor: '#aa00bfff' // blue
    //runningColor2: '#aa00ff00' // green
    runningColor2: 'gray' // green
  }
}

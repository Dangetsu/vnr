/** grayrangeslider.qml
 *  9/14/2014 jichi
 *  See: QML dial control example
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import '.' as Share

Rectangle { id: root_
  height: 16
  opacity: 0.7
  smooth: true
  radius: 7
  //radius: 0 // flat

  property alias toolTip: toolTip_.text
  property alias startHandleToolTip: startToolTip_.text
  property alias stopHandleToolTip: stopToolTip_.text

  property bool enabled: true

  property int handleWidth: 8
  property bool hover:
      toolTip_.containsMouse ||
      startToolTip_.containsMouse ||
      stopToolTip_.containsMouse

  property real minimumValue: 0 // 0%
  property real maximumValue: 1.0 // 100%

  property real startValue: 0
  property real stopValue: 0

  property string startColor: 'black'
  property string stopColor: 'white'

  // - Private -

  onWidthChanged: updateHandles()

  onStartValueChanged: updateStartHandle()
  onStopValueChanged: updateStopHandle()

  onMaximumValueChanged: updateHandles()
  onMinimumValueChanged: updateHandles()

  function updateHandles() {
    updateStartHandle()
    updateStopHandle()
  }

  function updateStartHandle() {
    if (width > startHandle_.width) {
      var t = Math.round((startValue - minimumValue) * (width - startHandle_.width) / (maximumValue - minimumValue))
      if (t !== startHandle_.x)
        startHandle_.x = t
    }
  }

  function updateStopHandle() {
    if (width > stopHandle_.width) {
      var t = Math.round((stopValue - minimumValue) * (width - stopHandle_.width) / (maximumValue - minimumValue))
      if (t !== stopHandle_.x)
        stopHandle_.x = t
    }
  }

  function updateStartValue() {
    if (width > startHandle_.width) {
      var t = minimumValue + startHandle_.x * (maximumValue - minimumValue) / (width - startHandle_.width)
      if (t !== startValue)
        startValue = t
    }
  }

  function updateStopValue() {
    if (width > stopHandle_.width) {
      var t = minimumValue + stopHandle_.x * (maximumValue - minimumValue) / (width - stopHandle_.width)
      if (t !== stopValue)
        stopValue = t
    }
  }

  //Plugin.SliderBean { Component.onCompleted: init() }

  gradient: Gradient { // black
    GradientStop { position: 0.0; color: 'gray' }
    GradientStop { position: 1.0; color: 'white' } // lighter
  }

  Share.LinearGradient { id: grad_ // horizontal gradient
    anchors.fill: parent
    colors: [root_.startColor, root_.stopColor]
    positions: [0.0, 1.0]

    startPoint: Qt.point(0,0)
    stopPoint: Qt.point(1,0)

    visible: root_.enabled
    opacity: 0.7
  }

  Share.FadingRectangle { //id: groove_
    anchors {
      left: startHandle_.right
      right: stopHandle_.left
      top: parent.top
      bottom: parent.bottom
      margins: 1
    }
    //radius: root_.radius

    visible: root_.enabled

    gradient: Gradient { // blue
      //GradientStop { position: 0.0; color: '#aa87cefa' } // lightskyblue
      GradientStop { position: 0.0; color: root_.hover ? '#87cefa' : '#cc87cefa' } // lightskyblue
      GradientStop { position: 1.0; color: root_.hover ? '#00bfff' : '#cc00bfff' } // deepskyblue, darker, clear transparency when hover
    }
  }

  Desktop.TooltipArea { id: toolTip_
    anchors.fill: parent
    text: startValue.toFixed(2) + ' - ' + stopValue.toFixed(2)
  }

  Share.FadingRectangle { id: startHandle_
    anchors.verticalCenter: parent.verticalCenter
    width: root_.handleWidth
    height: 14
    y: 1
    x: 0
    radius: 3
    //radius: 0 // flat
    smooth: true
    gradient: Gradient {
      GradientStop { position: 0.0; color: startMouse_.pressed ? 'black' : '#555555' }
      GradientStop { position: 1.0; color: 'black' }
    }
    //border.color: '#99ff0000' // red
    border.color: '#bbffffaa' // yellow
    border.width: root_.enabled && root_.hover ? 2 : 0

    visible: root_.enabled

    onXChanged: updateStartValue()
    onWidthChanged: updateStartHandle()

    MouseArea { id: startMouse_
      anchors.fill: parent

      //anchors.margins: -16 // Increase mouse area a lot outside the slider
      anchors.leftMargin: -4
      anchors.topMargin: -4
      anchors.bottomMargin: -4

      drag.target: parent; drag.axis: Drag.XAxis
      drag.minimumX: 0
      drag.maximumX: stopHandle_.x - startHandle_.width
      enabled: root_.enabled
    }

    Desktop.TooltipArea { id: startToolTip_
      anchors.fill: parent
      text: root_.startValue.toFixed(2)
    }
  }

  Share.FadingRectangle { id: stopHandle_
    anchors.verticalCenter: parent.verticalCenter
    width: root_.handleWidth
    height: 14
    y: 1
    x: 0
    radius: 3
    //radius: 0 // flat
    smooth: true
    gradient: Gradient {
      GradientStop { position: 0.0; color: stopMouse_.pressed ? 'black' : '#555555' }
      GradientStop { position: 1.0; color: 'black' }
    }
    //border.color: '#99ff0000' // red
    border.color: '#bbffffaa' // yellow
    border.width: root_.enabled && root_.hover ? 2 : 0

    visible: root_.enabled

    onXChanged: updateStopValue()
    onWidthChanged: updateStopHandle()

    MouseArea { id: stopMouse_
      anchors.fill: parent

      //anchors.margins: -16 // Increase mouse area a lot outside the slider
      anchors.leftMargin: -4
      anchors.topMargin: -4
      anchors.bottomMargin: -4

      drag.target: parent; drag.axis: Drag.XAxis
      drag.minimumX: startHandle_.x + startHandle_.width
      drag.maximumX: root_.width - stopHandle_.width
      enabled: root_.enabled
    }

    Desktop.TooltipArea { id: stopToolTip_
      anchors.fill: parent
      text: root_.stopValue.toFixed(2)
    }
  }
}

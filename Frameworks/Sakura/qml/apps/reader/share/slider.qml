/** slider.qml
 *  1/6/2013 jichi
 *  See: QML dial control example
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import '.' as Share

Rectangle { id: root_
  height: 16
  opacity: 0.7
  smooth: true

  radius: 8
  //radius: 0 // flat

  property alias toolTip: toolTip_.text

  property alias enabled: mouse_.enabled

  property alias handleWidth: handle_.width
  property alias hover: toolTip_.containsMouse

  property real minimumValue: 0
  property real maximumValue: 100

  //property real value: min + (handle_.x * (max-min) / (width - handle_.width)

  property real value: 0

  // - Private -

  onValueChanged: updateHandle()
  onMaximumValueChanged: updateHandle()
  onMinimumValueChanged: updateHandle()
  onWidthChanged: updateHandle()

  function updateHandle() {
    if (width > handle_.width) {
      var t = Math.round((value - minimumValue) * (width - handle_.width) / (maximumValue - minimumValue))
      if (t !== handle_.x)
        handle_.x = t
    }
  }

  function updateValue() {
    if (width > handle_.width) {
      var t = minimumValue + handle_.x * (maximumValue - minimumValue) / (width - handle_.width)
      if (t !== value)
        value = t
    }
  }

  //Plugin.SliderBean { Component.onCompleted: init() }

  gradient: Gradient { // black
    GradientStop { position: 0.0; color: 'gray' }
    GradientStop { position: 1.0; color: 'white' } // darker
  }

  Share.FadingRectangle { //id: groove_
    anchors {
      top: parent.top
      bottom: parent.bottom
      left: parent.left
      right: handle_.left
      margins: 1
    }
    //radius: root_.radius * 1.5
    visible: root_.enabled

    gradient: Gradient { // blue
      //GradientStop { position: 0.0; color: '#cc87ceeb' } // skyblue
      GradientStop { position: 0.0; color: root_.hover ? '#87cefa' : '#cc87cefa' } // lightskyblue
      GradientStop { position: 1.0; color: root_.hover ? '#00bfff' : '#cc00bfff' } // deepskyblue, darker, clear transparency when hover
    }
  }

  Share.FadingRectangle { id: handle_
    anchors.verticalCenter: parent.verticalCenter
    x: 0
    y: 1
    height: 14
    width: height / 2
    radius: 3
    //radius: 7
    //radius: 0 // flat
    smooth: true
    gradient: Gradient {
      GradientStop { position: 0.0; color: mouse_.pressed ? 'black' : '#555555' }
      GradientStop { position: 1.0; color: 'black' }
    }
    //border.color: '#99ff0000' // red
    border.color: '#bbffffaa' // yellow
    border.width: toolTip_.containsMouse ? 2 : 0

    visible: root_.enabled

    onXChanged: updateValue()
    onWidthChanged: updateHandle()

    MouseArea { id: mouse_
      anchors.fill: parent
      anchors.margins: -16 // Increase mouse area a lot outside the slider
      drag.target: parent; drag.axis: Drag.XAxis
      drag.minimumX: 0
      drag.maximumX: root_.width - handle_.width
    }
  }

  Desktop.TooltipArea { id: toolTip_
    anchors.fill: parent
    text: value.toFixed(2)
  }
}

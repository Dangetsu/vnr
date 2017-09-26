// ratingindicator.qml
// 6/24/root_.mouseAreaPadding14 jichi
// See: http://developer.nokia.com/community/wiki/Custom_Rating_Indicator_using_Qt_Quick
import QtQuick 1.1

Row { id: root_
  property int value: 3

  property string imageSource: 'star.png'

  property real scale: 1

  property real activeScale: 1
  property real activeOpacity: 1

  property real inactiveScale: 0.5
  property real inactiveOpacity: 0.4

  property int transitionDuration: 1000 // msec

  property int easingType: Easing.OutBounce

  spacing: 5 * scale

  // - Private -

  property int mouseAreaPadding: 20

  Image { id: star1_
    property int value: 1

    source: root_.imageSource
    scale: root_.inactiveScale * root_.scale
    opacity: root_.inactiveOpacity

    MouseArea {
      anchors.fill: parent
      height: parent.height + root_.mouseAreaPadding * root_.scale
      width: parent.width + root_.mouseAreaPadding * root_.scale
      onClicked: root_.value = star1_.value
    }

    states: State {
      name: 'star'
      when: root_.value >= star1_.value
      PropertyChanges { target: star1_
        opacity: root_.activeOpacity
        scale: root_.activeScale * root_.scale
      }
    }

    transitions: Transition {
      NumberAnimation { properties: 'opacity,scale'
        easing.type: root_.easingType
        duration: root_.transitionDuration
      }
    }
  }

  Image { id: star2_
    property int value: 2

    source: root_.imageSource
    scale: root_.inactiveScale * root_.scale
    opacity: root_.inactiveOpacity

    MouseArea {
      anchors.fill: parent
      height: parent.height + root_.mouseAreaPadding * root_.scale
      width: parent.width + root_.mouseAreaPadding * root_.scale
      onClicked: root_.value = star2_.value
    }

    states: State {
      name: 'star'
      when: root_.value >= star2_.value
      PropertyChanges { target: star2_
        opacity: root_.activeOpacity
        scale: root_.activeScale * root_.scale
      }
    }

    transitions: Transition {
      NumberAnimation { properties: 'opacity,scale'
        easing.type: root_.easingType
        duration: root_.transitionDuration
      }
    }
  }

  Image { id: star3_
    property int value: 3

    source: root_.imageSource
    scale: root_.inactiveScale * root_.scale
    opacity: root_.inactiveOpacity

    MouseArea {
      anchors.fill: parent
      height: parent.height + root_.mouseAreaPadding * root_.scale
      width: parent.width + root_.mouseAreaPadding * root_.scale
      onClicked: root_.value = star3_.value
    }

    states: State {
      name: 'star'
      when: root_.value >= star3_.value
      PropertyChanges { target: star3_
        opacity: root_.activeOpacity
        scale: root_.activeScale * root_.scale
      }
    }

    transitions: Transition {
      NumberAnimation { properties: 'opacity,scale'
        easing.type: root_.easingType
        duration: root_.transitionDuration
      }
    }
  }

  Image { id: star4_
    property int value: 4

    source: root_.imageSource
    scale: root_.inactiveScale * root_.scale
    opacity: root_.inactiveOpacity

    MouseArea {
      anchors.fill: parent
      height: parent.height + root_.mouseAreaPadding * root_.scale
      width: parent.width + root_.mouseAreaPadding * root_.scale
      onClicked: root_.value = star4_.value
    }

    states: State {
      name: 'star'
      when: root_.value >= star4_.value
      PropertyChanges { target: star4_
        opacity: root_.activeOpacity
        scale: root_.activeScale * root_.scale
      }
    }

    transitions: Transition {
      NumberAnimation { properties: 'opacity,scale'
        easing.type: root_.easingType
        duration: root_.transitionDuration
      }
    }
  }

  Image { id: star5_
    property int value: 5

    source: root_.imageSource
    scale: root_.inactiveScale * root_.scale
    opacity: root_.inactiveOpacity

    MouseArea {
      anchors.fill: parent
      height: parent.height + root_.mouseAreaPadding * root_.scale
      width: parent.width + root_.mouseAreaPadding * root_.scale
      onClicked: root_.value = star5_.value
    }

    states: State {
      name: 'star'
      when: root_.value >= star5_.value
      PropertyChanges { target: star5_
        opacity: root_.activeOpacity
        scale: root_.activeScale * root_.scale
      }
    }

    transitions: Transition {
      NumberAnimation { properties: 'opacity,scale'
        easing.type: root_.easingType
        duration: root_.transitionDuration
      }
    }
  }
}

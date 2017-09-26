/** labeledgrayrangeslider.qml
 *  9/14/2014 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
//import '../../../js/util.min.js' as Util
import '.' as Share

Item { id: root_
  property int labelWidth: 20

  property alias maximumValue: slider_.maximumValue
  property alias minimumValue: slider_.minimumValue

  property alias startValue: slider_.startValue
  property alias stopValue: slider_.stopValue

  property alias startColor: slider_.startColor
  property alias stopColor: slider_.stopColor

  property bool enabled: true
  property bool hover:
      slider_.hover
      || startToolTip_.containsMouse
      || stopToolTip_.containsMouse

  property alias sliderToolTip: slider_.toolTip

  property alias startLabelText: startLabel_.text
  property alias startLabelToolTip: startToolTip_.text
  property alias startHandleToolTip: slider_.startHandleToolTip

  property alias stopLabelText: stopLabel_.text
  property alias stopLabelToolTip: stopToolTip_.text
  property alias stopHandleToolTip: slider_.stopHandleToolTip

  property alias handleWidth: slider_.handleWidth

  property int spacing: 9

  // - Private -

  height: Math.max(startLabel_.height, slider_.height)

  Text { id: startLabel_
    anchors {
      left: parent.left
      verticalCenter: parent.verticalCenter
    }
    width: root_.labelWidth
    verticalAlignment: Text.AlignVCenter
    horizontalAlignment: Text.AlignRight
    color: root_.enabled ? 'snow' : 'silver'
    effect: Share.TextEffect { highlight: root_.enabled && root_.hover }

    //font.bold: root_.enabled && root_.hover
    //font.family: root_.language ? Util.fontFamilyForLanguage(root_.language) : ""
    font.strikeout: !root_.enabled

    text: slider_.startValue.toFixed(2)

    property alias toolTip: startToolTip_.text
    Desktop.TooltipArea { id: startToolTip_
      anchors.fill: parent
    }
  }

  Text { id: stopLabel_
    anchors {
      right: parent.right
      verticalCenter: parent.verticalCenter
    }
    width: root_.labelWidth
    verticalAlignment: Text.AlignVCenter
    horizontalAlignment: Text.AlignLeft
    color: root_.enabled ? 'snow' : 'silver'
    effect: Share.TextEffect { highlight: root_.enabled && root_.hover }

    //font.bold: root_.enabled && root_.hover
    //font.family: root_.language ? Util.fontFamilyForLanguage(root_.language) : ""
    font.strikeout: !root_.enabled

    text: slider_.stopValue.toFixed(2)

    property alias toolTip: stopToolTip_.text
    Desktop.TooltipArea { id: stopToolTip_
      anchors.fill: parent
    }
  }

  Share.GrayRangeSlider { id: slider_
    anchors {
      top: parent.top; bottom: parent.bottom
      left: startLabel_.right
      right: stopLabel_.left
      leftMargin: root_.spacing
      rightMargin: root_.spacing
    }
    enabled: root_.enabled
  }
}

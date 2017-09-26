/** labeledslider.qml
 *  1/6/2013 jichi
 *  See: QML dial control example
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
//import '../../../js/util.min.js' as Util
import '.' as Share

Item { id: root_
  property alias text: label_.text
  property alias font: label_.font
  property alias color: label_.color
  //property alias horizontalAlignment: label_.horizontalAlignment
  //property alias verticalAlignment: label_.verticalAlignment
  property alias labelWidth: label_.width
  property alias toolTip: toolTip_.text
  property alias sliderToolTip: slider_.toolTip
  property bool hover: toolTip_.containsMouse || slider_.hover
  property alias handleWidth: slider_.handleWidth
  property alias value: slider_.value // real, default 0.0
  property alias maximumValue: slider_.maximumValue // real, default 0.0
  property alias minimumValue: slider_.minimumValue // real, default 100.0
  property alias enabled: slider_.enabled
  //property string language

  property int spacing: 9

  // - Private -

  height: Math.max(label_.height, slider_.height)

  Text { id: label_
    anchors {
      top: parent.top; bottom: parent.bottom
      left: parent.left
    }
    verticalAlignment: Text.AlignVCenter
    horizontalAlignment: Text.AlignRight
    color: root_.enabled ? 'snow' : 'silver'
    effect: Share.TextEffect { highlight: root_.enabled && root_.hover }

    font.bold: root_.enabled && root_.hover
    //font.family: root_.language ? Util.fontFamilyForLanguage(root_.language) : ""
    font.strikeout: !root_.enabled

    Desktop.TooltipArea { id: toolTip_
      anchors.fill: parent
    }
  }

  Share.Slider { id: slider_
    anchors {
      top: parent.top; bottom: parent.bottom
      right: parent.right
      left: label_.right
      leftMargin: root_.spacing
    }
  }
}

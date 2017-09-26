/** bootstrap/button.qml
 *  10/17/2012 jichi
 *  CSS: http://www.qtcentre.org/wiki/index.php?title=AeroButton
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import QtEffects 1.0 as Effects
import 'bootstrap.min.js' as Js

MouseArea { id: root_
  property alias text: text_.text
  property alias toolTip: toolTip_.text
  property alias font: text_.font
  //property alias color: text_.color

  property string styleClass: 'btn'
  property variant styleObject: Js.style(styleClass)
  //property alias effectColor: effect_.color

  //property alias pressed: mouse_.pressed
  property alias hover: toolTip_.containsMouse

  //signal clicked(variant mouse)

  function click()  { clicked(null) }

  width: text_.width + 24   // bootstrap: 12px * 2 = 24
  height: text_.height + 10  // bootstrap: 4px * 2 = 8

  acceptedButtons: Qt.LeftButton

  // - Private -

  Rectangle { id: background_
    z: -1
    anchors.fill: parent
    radius: 4 // bootstrap: 4px
    smooth: true

    // rgba(82, 168, 236, 0.8) = '#cc52a8ec'
    border.color: root_.activeFocus ? '#cc52a8ec' : '#bfbfbf'
    border.width: 1

    //effect: Effects.DropShadow {
    //  blurRadius: 1
    //  offset: '1,1'
    //  color: '#552d5f5f' // dark green
    //}

    gradient: Gradient {
      GradientStop {
        position: 0.0
        color: !root_.enabled ? '#e6e6e6' :
               root_.pressed ? styleObject.activeColor :
               root_.hover ? styleObject.hoverColor :
               styleObject.startColor
      }
      GradientStop {
        position: 1.0
        color: !root_.enabled ? '#e6e6e6' :
               root_.pressed ? styleObject.activeColor :
               root_.hover ? styleObject.hoverColor :
               styleObject.stopColor
      }
    }
  }

  Text { id: text_
    anchors.centerIn: parent
    horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
    font.pixelSize: 12 // bootstrap: 14px
    //font.bold: true
    //font.family: root_.language ? Util.fontFamilyForLanguage(root_.language) : ""
    //font.family: 'MS Gothic'
    //style: Text.Outline; styleColor: 'black'
    smooth: true
    color: root_.enabled ? styleObject.textColor : '#777777'

    effect: Effects.DropShadow { id: effect_
      blurRadius: 8
      offset: '1,1'
      color: styleClass === 'btn' ? 'transparent' : '#aa2d5f5f' // dark green. bootstrap default is rgba(0,0.0,0.75)
    }
  }

  Desktop.TooltipArea { id: toolTip_
    anchors.fill: parent
  }
}

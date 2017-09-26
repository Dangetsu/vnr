/** menubutton.qml
 *  9/29/2012 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
//import org.sakuradite.reader 1.0 as Plugin
//import '../../js/sakurakit.min.js' as Sk
//import '../../js/reader.min.js' as My
import '../share' as Share
import '.' as Kagami

Share.TextButton { id: root_ // blue button

  //property alias containsMouse: indicator_.containsMouse
  property bool fadingEnabled: false

  // - Private -

  //Plugin.SystemStatus { id: statusPlugin_ }
  Kagami.AppMenu { id: appMenu_ }

  toolTip: qsTr("Right click to show menu")
           //qsTr("Accessing the Internet") + " (" + qsTr("{0} thread").replace('{0}', threadPool_.threadCount) + ")"

  radius: 17
  //radius: 0 // flat

  width: 35; height: 35
  font.pixelSize: 14
  font.bold: true
  text: (!checked || !enabled) ? "◯" : "×" // まる、ばつ
  font.family: 'MS Gothic'

  property bool checked: false
  property bool enabled: statusPlugin_.online && statusPlugin_.login

  //visible: !root_.ignoresFocus

  backgroundColor: !enabled ? '#aaff0000' : // red
                   //checked ?  '#55bebebe' : // gray
                   checked ?  '#aa00bfff' : // blue
                              '#aa00bfff'   // blue

  property bool fading: fadingEnabled && !hover
  states: [
    State { when: !fading
      PropertyChanges { target: root_; opacity: 1 }
    }
    , State { when: fading
      PropertyChanges { target: root_; opacity: 0.01 }
    }
  ]

  transitions: Transition {
    NumberAnimation { property: 'opacity'; duration: 400 }
  }

  MouseArea {
    anchors.fill: parent
    anchors.margins: -2
    acceptedButtons: Qt.RightButton
    onPressed: {
      var gp = mapToItem(null, x + mouse.x, y + mouse.y)
      appMenu_.showPopup(gp.x, gp.y)
    }
  }

  Kagami.AjaxIndicator { id: indicator_
    anchors.centerIn: parent
    width: 60; height: 60

    visible: !fading && count > 0 && parent.visible

    //Behavior on x { SpringAnimation { spring: 3; damping: 0.3; mass: 1.0 } }
    //Behavior on y { SpringAnimation { spring: 3; damping: 0.3; mass: 1.0 } }
  }
}

/** checkdot.qml
 *  9/9/2014 jichi
 *  See: http://relog.xii.jp/archives/2011/09/qmlqt_4.html
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
//import '../../../js/util.min.js' as Util
import '.' as Share

MouseArea { id: root_

  property bool checked: false      // チェック状態
  property bool enabled: true
  property alias hover: toolTip_.containsMouse
  property int size: 13          // チェックのサイズ
  property alias toolTip: toolTip_.text
  //property string language

  //hoverEnabled: true

  acceptedButtons: Qt.LeftButton

  // - Private -

  width: size
  height: size

  // クリックイベント
  onClicked:
    if (enabled)
      checked = !checked;

  // チェックマーク
  Rectangle { id: box_
    anchors.fill: parent
    radius: root_.size/2 + 1
    //radius: 0 // flat

    // ベースのグラデ
    gradient: Gradient {
      GradientStop { position: 0; color: '#cc555555' }
      GradientStop { position: 1; color: '#cc333333' }
    }

    // On/Offするところ
    Rectangle {
      anchors.fill: parent
      anchors.margins: 2
      //width: size - 4; height: size - 4
      radius: parent.radius
      // グラデ（OFF時の色）
      gradient: Gradient {
        GradientStop { id: gradBegin_
          position: 0
          color: '#000000'
        }
        GradientStop { id: gradEnd_
          position: 1
          color: '#555555'
        }
      }
    }
  }

  // 状態管理
  states: State {
    when: root_.enabled && root_.checked   // こっちの方がスマートかも
    PropertyChanges {
      target: gradBegin_
      color: '#cc87cefa' // lightskyblue
      //color: '#aa87ceeb' // skyblue
    }
    PropertyChanges {
      target: gradEnd_
      color: root_.hover ? '#00bfff' : '#cc00bfff'// deepskyblue, darker, clear transparency when hover
    }
  }
  transitions: Transition { ColorAnimation {} }

  Desktop.TooltipArea { id: toolTip_
    anchors.fill: parent
  }
}

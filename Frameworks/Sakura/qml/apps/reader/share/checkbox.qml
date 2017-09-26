/** checkbox.qml
 *  11/26/2012 jichi
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
  property alias text: text_.text   // 表示するメッセージ
  property alias color: text_.color // 色
  property alias font: text_.font   // フォント
  property int boxSize: 13          // チェックのサイズ
  property alias toolTip: toolTip_.text
  //property string language

  //hoverEnabled: true

  acceptedButtons: Qt.LeftButton

  height: Math.max(box_.height, text_.height)
  width: box_.width + text_.width + text_.anchors.leftMargin

  // - Private -

  // チェック自体のサイズ変更
  //onBoxSizeChanged:
  //  if (boxSize < 10)
  //    boxSize = 10

  //width: box_.width + text_.width + text_.anchors.leftMargin * 2
  //height: box_.height > text_.height ? box_.height : text_.height

//これは使わずstate の whenを使う方がスマートかも
// 状態が変わった時のイベント
//  onCheckedChanged: {
//     if(checked){
//      state = 'ON'
//    }else{
//      state = ''
//    }
//  }

  // クリックイベント
  onClicked:
    if (enabled)
      checked = !checked;

  // チェックマーク
  Rectangle { id: box_
    anchors {
      left: parent.left
      verticalCenter: parent.verticalCenter
    }
    width: boxSize
    height: boxSize
    radius: boxSize/2 + 1
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
      //anchors.centerIn: parent
      //width: boxSize - 4; height: boxSize - 4
      radius: parent.radius
      // グラデ（OFF時の色）
      gradient: Gradient {
        GradientStop { id: boxGradBegin_
          position: 0
          color: '#000000'
        }
        GradientStop { id: boxGradEnd_
          position: 1
          color: '#555555'
        }
      }
    }
  }

  // テキスト
  Text { id: text_
    anchors {
      left: box_.right
      verticalCenter: parent.verticalCenter
      leftMargin: 8
    }
    font.strikeout: root_.enabled && !root_.checked
    //font.family: root_.language ? Util.fontFamilyForLanguage(root_.language) : ""
    //style: Text.Outline
    //styleColor: 'black'

    //font.bold: root_.hover
    color: root_.enabled ? 'snow' : 'silver'

    effect: Share.TextEffect { highlight: root_.hover && root_.enabled }
  }

  // 状態管理
  states: State {
    when: root_.enabled && root_.checked   // こっちの方がスマートかも
    PropertyChanges {
      target: boxGradBegin_
      color: '#cc87cefa' // lightskyblue
      //color: '#aa87ceeb' // skyblue
    }
    PropertyChanges {
      target: boxGradEnd_
      color: root_.hover ? '#00bfff' : '#cc00bfff'// deepskyblue, darker, clear transparency when hover
    }
  }
  transitions: Transition { ColorAnimation {} }

  Desktop.TooltipArea { id: toolTip_
    anchors.fill: parent
  }
}

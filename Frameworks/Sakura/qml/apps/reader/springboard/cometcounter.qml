/** cometcounter.qml
 *  3/3/2014 jichi
 */
import QtQuick 1.1
//import org.sakuradite.reader 1.0 as Plugin
import '../share' as Share

Share.TwinkleButton { //id: root_

  property int count
  text: String(count)

  //visible: globalComet_.active //&& count > 1

  // - Private -

  height: 22; width: 22

  //property int count: Math.max(1, globalComet_.connectionCount)

  //property bool highlight: count > 1

  font.pixelSize: 12
  font.bold: false
  radius: 2
  //visible: !root_.ignoresFocus
  //visible: !statusPlugin_.wine

  //property bool checked

  //pauseColor: checked ? parent.buttonCheckedColor : parent.buttonColor

  //pauseColor: '#aa555555' // black
  color: 'black'
  //pauseColor: 'snow'
  border.color: '#33555555'  // gray
  pauseColor: '#99ffffff'  // white

  runningColor: '#99ffff00' // yellow
  runningColor2: '#99ffffff' // white

  duration: 1000 // 1 second

  //language: root_.language
  //font.family: 'DFGirl'

  //toolTip: qsTr("Read current Japanese game text using TTS")
  toolTip: qsTr("{0} people are online now").replace('{0}', count)

  //onClicked: checked = !checked
}

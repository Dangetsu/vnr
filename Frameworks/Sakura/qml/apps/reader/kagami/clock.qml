/** clock.qml
 *  12/13/2013 jichi
 */
import QtQuick 1.1
//import QtDesktop 0.1 as Desktop
//import org.sakuradite.reader 1.0 as Plugin
//import '../../../js/sakurakit.min.js' as Sk
//import '../../../js/reader.min.js' as My
import '../../../js/util.min.js' as Util
import '../share' as Share

Share.FloatingRectangle { id: root_
  //implicitWidth: 200; implicitHeight: 100

  property real zoomFactor: 1
  visible: false

  // - Private -

  color: drag.active ? '#99000000' : '#55000000'
  //radius: 10 // flat

  width: text_.width + 9
  height: text_.height + 9

  onVisibleChanged:
    if (visible) {
      refresh()
      timer_.start()
    } else
      timer_.stop()

  Timer { id: timer_
    interval: 1000 * 30 // 30 second
    repeat: true
    onTriggered: root_.refresh()
  }

  Text { id: text_
    anchors.centerIn: parent
    textFormat: Text.PlainText
    font.pixelSize: 20 * root_.zoomFactor
    font.family: 'DFGirl'
    //font.family: 'YouYuan'
    //font.bold: true
    verticalAlignment: Qt.AlignVCenter
    horizontalAlignment: Qt.AlignHCenter
    wrapMode: Text.NoWrap
    color: 'snow'

    effect: Share.TextEffect { highlight: root_.drag.active }
  }

  function refresh() {
    var d = new Date()
    var h = Util.formatWeek(d.getDay()) + " " + Util.formatTime(d.getHours(), d.getMinutes())
    if (d.getTimezoneOffset() !== -540) // -540 is JCT
      h += " (日本 " + Util.formatTime((d.getUTCHours() + 9) % 24, d.getMinutes()) + ")"
    text_.text = h
    toolTip = Util.formatDate(d.getMonth()+1, d.getDate(), d.getFullYear(), d.getDay())
  }
}

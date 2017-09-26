/** counter.qml
 *  2/19/2014 jichi
 */
import QtQuick 1.1
import '../../../js/reader.min.js' as My

Text {

  // - Private -
  textFormat: Text.RichText
  font.pixelSize: 12

  wrapMode: Text.NoWrap
  horizontalAlignment: Text.AlignRight
  verticalAlignment: Text.AlignBottom

  visible: statusPlugin_.online && count > 1

  property int count: termComet_.connectionCount // cached

  text: {
    var t = '<span style="color:blue;font-weight:bold">' + count + '</span>'
    return My.tr("{0} people are viewing this page").replace('{0}', t)
  }
}

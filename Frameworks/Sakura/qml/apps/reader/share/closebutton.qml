/** closebutton.qml
 *  10/17/2012 jichi
 */
import '../../../js/sakurakit.min.js' as Sk
import '.' as Share

Share.CircleButton {

  // - Private -

  diameter: 15

  font.pixelSize: 14 // later
  font.bold: hover
  font.family: 'MS Gothic'

  //color: hover ? 'red' : 'snow'
  //backgroundColor: hover ? '#44ff33cc' : 'transparent' // magenta
  //backgroundColor: hover ? '#556a6d6a' : 'transparent' // black
  backgroundColor: hover ? '#556a6d6a' : '#01000000' // black, non-transp prevent disappear
  //backgroundColor: 'transparent' // black

  text: "×" // ばつ
  toolTip: Sk.tr("Close")
}

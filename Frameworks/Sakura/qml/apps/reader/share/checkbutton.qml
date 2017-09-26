/** checkbutton.qml
 *  9/7/2014 jichi
 */
import '.' as Share

Share.TextButton {

  //property bool enabled: true
  property bool checked

  // - Private -

  // - Private -
  width: 50
  height: 25
  backgroundColor: !enabled ? '#aabebebe' : checked ? '#aa00ff00' : '#aa434343'  // gray : green : black

  //radius: 5
  radius: 0 // flat
  onClicked: if (enabled) checked = !checked
}

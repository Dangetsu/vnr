/** pushbutton.qml
 *  9/7/2014 jichi
 *  A black color theme for text button
 */
import '.' as Share
import 'pushbutton.min.js' as Js

Share.TextButton {

  property color defaultColor
  property color disabledColor

  property string styleHint: 'inverse'
  property variant style: Js.style(styleHint)
  //property alias effectColor: effect_.color

  // - Private -

  width: 50
  height: 25

  //radius: 5
  radius: 0 // flat

  color: style.textColor
  backgroundColor: enabled ? style.activeColor : style.disabledColor
}

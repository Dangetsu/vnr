/** counter.qml
 *  2/18/2015 jichi
 */
import QtQuick 1.1
import '../share' as Share
import '../../../imports/qmleffects' as Effects

Share.CheckButton { //id: root_

  property int count
  property string prefix

  property real zoomFactor: 1.0

  property alias effectColor: effect_.color

  // - Private -

  text: count ? prefix + count : prefix

  width: 20 * zoomFactor
  height: 20 * zoomFactor

  font.pixelSize: 14 * zoomFactor
  font.family: 'YouYuan'

  //property color buttonCheckedColor: '#aa00ff00' // green
  //property color buttonUncheckedColor: '#aaff0000' // red
  //property color buttonDisabledColor:  // gray
  //backgroundColor: enabled ? '#aabebebe' : '#aa555555' // gray : black
  backgroundColor: 'transparent'

  effect: Effects.Glow { id: effect_
    offset: '1,1'
    //blurRadius: 8
    blurRadius: 30
    blurIntensity: 4
  }
}

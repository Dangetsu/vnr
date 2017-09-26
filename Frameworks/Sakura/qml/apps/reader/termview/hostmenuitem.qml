/** hostmenuitem.qml
 *  2/7/2015 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import '../../../js/util.min.js' as Util

Desktop.MenuItem {

  property string value

  // - Private -

  text: Util.translatorName(value)
  checkable: true
}

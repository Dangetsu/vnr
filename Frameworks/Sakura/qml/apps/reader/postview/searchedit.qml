/** searchedit.qml
 *  2/21/2014 jichi
 */
import QtQuick 1.1
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/util.min.js' as Util
import '../share' as Share

Share.SearchBox {

  property string searchText: getSearchText()

  // - Private -

  totalCount: 0 // no total count
  placeholderText: "ex. hello, @user, 201401"
  toolTip: Sk.tr("Search")

  function getSearchText() {
    var t = Util.trim(text)
    return !t ? '' : '%' + t.replace(/\s/g, '%') + '%'
  }
}

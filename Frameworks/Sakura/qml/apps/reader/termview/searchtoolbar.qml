/** searchtoolbar.qml
 *  2/20/2013 jichi
 */
import QtQuick 1.1
//import QtDesktop 0.1 as Desktop
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/util.min.js' as Util
import '../../../components/bootstrap3' as Bootstrap

Row { id: root_ // Theme refers to Bootstrap.label

  signal triggered(string text)
  property alias displaysDuplicateRows: duplicateButton_.checked // bool

  function clear() {
    for (var i = 0; i < children.length; ++i)
      if (children[i].checked)
        children[i].checked = false
  }

  // - Private -
  spacing: 2

  property int cellWidth: 45
  property int cellHeight: 18

  Bootstrap.Button {
    width: parent.cellWidth; height: parent.cellHeight
    styleClass: 'btn btn-inverse'

    text: '@' + Sk.tr("user")
    toolTip: qsTr("Search your editing")

    onClicked: {
      var name = statusPlugin_.userName
      if (name)
        root_.triggered('@' + name)
    }
  }

  Bootstrap.Button {
    width: parent.cellWidth; height: parent.cellHeight
    styleClass: 'btn btn-inverse'

    text: '#' + Sk.tr("game")
    toolTip: qsTr("Search current game")

    onClicked: {
      var name = datamanPlugin_.getCurrentGameSeries() || datamanPlugin_.getCurrentGameName()
      if (name)
        root_.triggered('#' + name)
    }
  }

  Bootstrap.Button {
    width: parent.cellWidth; height: parent.cellHeight
    styleClass: 'btn btn-inverse'

    text: Sk.tr("lang")
    toolTip: qsTr("Search your language")

    onClicked: {
      var lang2 = statusPlugin_.userLanguage
      if (lang2)
        root_.triggered(Sk.tr(Util.languageName(lang2)))
    }
  }

  Bootstrap.Button { id: duplicateButton_
    width: parent.cellWidth; height: parent.cellHeight
    styleClass: checked ? 'btn btn-success' : 'btn btn-default'
    checkable: true
    text: qsTr("dup")
    toolTip: qsTr("Display duplicate rows which should be avoided")
  }
}

// EOF
/*
Share.TextButton {
  //language: 'ja'
  width: parent.cellWidth; height: parent.cellHeight
  radius: parent.cellRadius
  //shadowWidth: width + 15; shadowHeight: height + 15
  font.pixelSize: parent.pixelSize
  //font.bold: true
  color: 'snow'
  backgroundColor: hover ? '#333' : '#666'
  //font.family: 'MS Gothic'

  text: '@' + Sk.tr("user")
  toolTip: qsTr("Search your terms")

  onClicked: {
    var name = statusPlugin_.userName
    if (name)
      root_.triggered('@' + name)
  }
}
*/

/** quick.qml
 *  5/25/2014 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import '../components/buttongroup' as ButtonGroup
import '../components/desktopex' as DesktopEx

Item {
  implicitWidth: 250; implicitHeight: 400

  // - Private -

  DesktopEx.MultiComboBox { id: combo_
    anchors.centerIn: parent
    width: 200
    height: 30

    //separatorText: "|"

    //property list<MenuItem> l: [
    Desktop.MenuItem { id: act1_
      text: "Naver"
      property string value: "naver"
      checkable: true
    }
    Desktop.MenuItem { id: act2_
      text: "Google"
      property string value: "google"
      checkable: true
    }
    Desktop.MenuItem { id: act3_
      text: "Bing"
      property string value: "bing"
      checkable: true
    }
    Desktop.MenuItem { id: act4_
      text: "Infoseek"
      property string value: "infoseek"
      checkable: true
    }

    menuItems: [act1_, act2_, act3_, act4_]

    property string selectedValues: 'google,bing'

    onSelectionChanged: updateSelectedValues()

    Component.onCompleted: {
      for (var i in menuItems) {
        var item = menuItems[i]
        if (~selectedValues.indexOf(item.value))
          item.checked = true
      }
    }

    function updateSelectedValues() {
      var l = []
      for (var i in menuItems) {
        var item = menuItems[i]
        if (item.checked)
          l.push(item.value)
      }
      selectedValues = l.join(',')
    }
  }

  //ButtonGroup.ButtonRow {
  //  anchors.centerIn: parent
  //  //spacing: 2
  //  Desktop.Button { text: "hello 1"; checkable: true }
  //  Desktop.Button { text: "hello 2"; checkable: true }
  //  Desktop.Button { text: "hello 3"; checkable: true }
  //  Desktop.Button { text: "hello 4"; checkable: true }

  //  exclusive: true
  //  //onCheckedButtonChanged:
  //  //  console.log(checkedButton)
  //}
}

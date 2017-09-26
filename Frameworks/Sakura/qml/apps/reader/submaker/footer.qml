/** footer.qml
 *  10/21/2012 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/util.min.js' as Util
import '../../../components/bootstrap3' as Bootstrap

Item { id: root_

  property alias returnChecked: returnAct_.checked
  property alias shiftReturnChecked: shiftReturnAct_.checked
  //property alias spellChecked: spellButton_.checked
  property alias lockChecked: lockButton_.checked
  //property alias popupChecked: popupButton_.checked
  signal submitClicked
  //signal tagTriggered(string tag)

  property string selectedType: typeCombo_.model.get(typeCombo_.selectedIndex).value

  // - Private -

  property bool canLock: status_.online && !!status_.userId && status_.userId !== 4

  height: 40

  //gradient: Gradient {
  //  //GradientStop { position: 0.0;  color: '#8c8f8c' }
  //  //GradientStop { position: 0.17; color: '#6a6d6a' }
  //  //GradientStop { position: 0.77; color: '#3f3f3f' }
  //  //GradientStop { position: 1.0;  color: '#6a6d6a' }
  //  GradientStop { position: 0.17; color: '#dfdfe3' }
  //  GradientStop { position: 0.77; color: '#f1f1f3' }
  //  GradientStop { position: 1.0;  color: '#f0f0f3' }
  //}
  //color: '#ced0d6'

  //Image {
  //  anchors.fill: parent
  //  fillMode: Image.Tile
  //  source: 'image://rc/texture-black'
  //  //z: -1
  //}

  Plugin.TextManagerProxy { id: textManager_
    contextSizeHint: contextCombo_.selectedIndex
  }

  Plugin.SystemStatus { id: status_ }

  Plugin.GameProxy { id: game_ }

  Plugin.MainObjectProxy { id: main_ }


  property int _MARGIN: 10
  property int _BUTTON_WIDTH: 60

  // - Left -

  Desktop.ComboBox { id: contextCombo_
    anchors {
      verticalCenter: parent.verticalCenter
      left: parent.left
      leftMargin: 10
    }
    width: 54
    model: ListModel {
      ListElement { text: "ctx=auto" }
      ListElement { text: "ctx=1" }
      ListElement { text: "ctx=2" }
      ListElement { text: "ctx=3" }
      ListElement { text: "ctx=4" }
    }
    tooltip: qsTr("Preferred context count")
  }

  Desktop.Label { id: contextLabel_
    anchors {
      verticalCenter: parent.verticalCenter
      left: contextCombo_.right
      leftMargin: 10
    }
    text: My.tr("Context count") + " = " + textManager_.contextSize

    Desktop.TooltipArea{
      anchors.fill: parent
      text: qsTr("Current context count")
    }
  }

  // - Right -

  //Desktop.CheckBox { id: spellButton_
  //  anchors {
  //    verticalCenter: parent.verticalCenter
  //    right: helpButton_.left
  //    rightMargin: 9
  //  }
  //  text: ' ' + Sk.tr("Spell check")
  //  width: 85
  //  //tooltip: qsTr("Mark mistyped words")  // tooltip does not exist for Desktop.ComboBox
  //}

  Desktop.CheckBox { id: lockButton_
    anchors {
      verticalCenter: parent.verticalCenter
      right: typeCombo_.left
      rightMargin: _MARGIN
    }
    width: 50
    enabled: root_.canLock
    //visible: status_.online && root_.canLock
    text: ' ' + Sk.tr("Lock")

    Desktop.TooltipArea{
      anchors {
        fill: parent
        leftMargin: 20
      }
      text: qsTr("Whether allow others to improve your subtitle")
    }
  }

  Desktop.ComboBox { id: typeCombo_
    anchors {
      verticalCenter: parent.verticalCenter
      right: enterButton_.left
      rightMargin: _MARGIN
    }
    width: 72
    model: ListModel {
      //ListElement { text: "Subtitle"; value: 'subtitle' }
      //ListElement { text: "Comment"; value: 'comment' }
      Component.onCompleted: {
        append({text:Sk.tr("Subtitle"), value:'subtitle'})
        append({text:Sk.tr("Danmaku"), value:'danmaku'})
        append({text:Sk.tr("Comment"), value:'comment'})
        append({text:My.tr("Note"), value:'popup'})
      }
    }
    tooltip: Sk.tr("Type")
    //onSelectedIndexChanged:
    //  console.log(model.get(selectedIndex).type)
  }

  Bootstrap.Button { id: enterButton_
    anchors {
      verticalCenter: parent.verticalCenter
      right: submitButton_.left
      rightMargin: _MARGIN
    }
    width: _BUTTON_WIDTH
    styleClass: 'btn btn-info'
    text: Sk.tr("Enter")
    toolTip: qsTr('Send "Enter" to the game process (no effect for some games)')
    onClicked: game_.postReturn()
  }

  Bootstrap.Button { id: submitButton_
    anchors {
      verticalCenter: parent.verticalCenter
      right: submitOptionButton_.left
      rightMargin: -_MARGIN/2
    }
    styleClass: 'btn btn-primary'
    width: _BUTTON_WIDTH

    text: Sk.tr("Submit")
    toolTip: qsTr("Shift+Enter to submit the subtitle")

    onClicked: submitClicked()
  }

  Bootstrap.Button { id: submitOptionButton_
    anchors {
      verticalCenter: parent.verticalCenter
      right: parent.right
      rightMargin: _MARGIN
    }
    styleClass: 'btn btn-primary'
    width: 20
    text: "＋"
    toolTip: Sk.tr("Keyboard shortcuts")

    onClicked: {
      //var gp = mapToItem(null, 0, 0)
      var gp = Util.itemGlobalPos(parent)
      submitMenu_.showPopup(gp.x + x, gp.y + y + height)
    }
  }

  Desktop.Menu { id: submitMenu_
    Desktop.MenuItem { id: returnAct_
      text: qsTr("Enter to Submit")
      checkable: true
      onTriggered: console.log("submitbar.qml:submitMenu: returnEnabled =", checked)
    }
    Desktop.MenuItem { id: shiftReturnAct_
      text: qsTr("Shift+Enter to Proceed Game")
      checkable: true
      onTriggered: console.log("submitbar.qml:submitMenu: shiftReturnEnabled =", checked)
    }
  }
}

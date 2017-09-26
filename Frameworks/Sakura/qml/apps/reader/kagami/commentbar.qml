/** commentbar.qml
 *  10/21/2012 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
//import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/util.min.js' as Util
import '../../../components/bootstrap3' as Bootstrap
import '../share' as Share

Share.InputBar { id: root_

  property bool fullScreen: false

  // - Private -

  function selectedType() {
    return typeEdit_.model.get(typeEdit_.selectedIndex).value
  }

  //radius: 12

  maximumLength: 255 // maximum number of characters allowed in comment
  //property color buttonColor: '#8b434343' // gray

  //textLeftMargin: visibleButton_.width + 20
  textRightMargin: enterButton_.width + submitButton_.width + helpButton_.width + typeEdit_.width + buttonMargin * 5
  property int buttonMargin: 4

  property bool opaque: active || !fullScreen //|| !!text
  states: [
    State { // active
      when: root_.visible && root_.opaque
      PropertyChanges { target: root_
        opacity: 1
      }
    }
    , State { // inactive
      when: root_.visible && !root_.opaque
      PropertyChanges { target: root_
        opacity: 0.6
      }
    }
    , State { // hidden
      when: !root_.visible
      PropertyChanges { target: root_
        opacity: 0
     }
    }
  ]
  transitions: Transition {
    NumberAnimation { property: 'opacity' }
  }

  placeholderText: qsTr("Enter to submit, or Shift+Enter to submit and forward the game")
  toolTip: qsTr("Type your comment here (BBCODE is supported)")

  //Plugin.TextManagerProxy { id: textmanPlugin_ }
  //Plugin.MainObjectProxy { id: mainPlugin_ }
  //Plugin.SystemStatus { id: statusPlugin_ }
  //Plugin.GameProxy { id: gamePlugin_ }

  Desktop.ComboBox { id: typeEdit_
    anchors {
      top: parent.top; bottom: parent.bottom
      topMargin: 2; bottomMargin: 2
      right: helpButton_.left
      rightMargin: buttonMargin
    }
    width: 72
    model: ListModel {
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

  Bootstrap.Button { id: helpButton_
    anchors {
      top: parent.top; bottom: parent.bottom
      topMargin: 2; bottomMargin: 2
      right: enterButton_.left
      rightMargin: buttonMargin
    }
    styleClass: 'btn btn-success'
    //width: 40
    //radius: 10
    //font.pixelSize: 12
    //font.bold: true
    //backgroundColor: '#aaffbf00' // yellow
    text: Sk.tr("Help")
    toolTip: Sk.tr("Help")
    onClicked: mainPlugin_.showCommentHelp()
  }


  Bootstrap.Button { id: enterButton_
    anchors {
      top: parent.top; bottom: parent.bottom
      topMargin: 2; bottomMargin: 2
      right: submitButton_.left
      rightMargin: buttonMargin
    }
    styleClass: 'btn btn-info'
    //width: 40
    //radius: 10
    //font.pixelSize: 12
    //font.bold: true
    //backgroundColor: '#aaffbf00' // yellow
    text: Sk.tr("Enter")
    toolTip: qsTr('Send "Enter" to the game process (no effect for some games)')
    onClicked: gamePlugin_.postReturn()
  }

  Bootstrap.Button { id: submitButton_
    anchors {
      top: parent.top; bottom: parent.bottom
      topMargin: 2; bottomMargin: 2
      right: parent.right
      rightMargin: buttonMargin
    }
    styleClass: 'btn btn-primary'
    //width: 40
    text: Sk.tr("Submit")
    onClicked: root_.submit()
    toolTip: qsTr("Submit the comment") + " (" + Sk.tr("Enter") + ")"
  }

  onAccepted: {
    var ok = submit()
    if (statusPlugin_.isKeyShiftPressed()) {
      if (ok)
        gamePlugin_.postReturnLater()
      else
        gamePlugin_.postReturn()
    }
  }

  ///  @return  bool  if ok
  function submit() {
    var t = Util.trim(root_.text)
    if (t) {
      var locked = false
      var type = selectedType()
      var ok = textmanPlugin_.submitComment(t, type, locked)
      if (ok)
        root_.text = ""
      return ok
    } else
      return false
    //console.log("commentbar.qml:submit: pass")
  }
}

// EOF

  //Share.TextButton { id: editButton_
  //  anchors {
  //    top: parent.top; bottom: parent.bottom
  //    topMargin: 2; bottomMargin: 2
  //    right: enterButton_.left
  //    rightMargin: 4
  //  }
  //  radius: 10
  //  width: 40
  //  font.pixelSize: 12
  //  font.bold: true
  //  text: Sk.tr("Edit")
  //  onClicked: mainPlugin_.showBacklog()
  //  backgroundColor: '#aa00bfff' // blue
  //  toolTip: qsTr("Open Backlog")
  //}


/** maintoolbar.qml
 *  2/21/2013 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My

Item { id: root_
  height: 40

  property QtObject model // gameman.CommentModel
  property QtObject currentItem // dataman.Comment
  property int userId
  property int userLevel

  // - Private -

  property bool notEmpty: !!model && model.count > 0

  property int _SUPER_USER_ID: 2
  property int _GUEST_USER_ID: 4
  //property string _SUPER_USER: ' '

  //gradient: Gradient {
  //  GradientStop { position: 0.0;  color: '#c8c9d0' }
  //  GradientStop { position: 0.17; color: '#dfdfe3' }
  //  GradientStop { position: 0.77; color: '#f1f1f3' }
  //  GradientStop { position: 1.0;  color: '#f0f0f3' }
  //}

  //Plugin.MainObjectProxy { id: mainPlugin_ }
  Plugin.DataManagerProxy { id: datamanPlugin_ }
  //Plugin.GameViewManagerProxy { id: gameview_ }
  //Plugin.SubtitleEditorManagerProxy { id: subedit_ }
  //Plugin.UserViewManagerProxy { id: userview_ }

  Desktop.ToolBar {
    anchors.fill: parent
    anchors.leftMargin: 5

    Row {
      spacing: 5
      anchors {
        verticalCenter: parent.verticalCenter
        left: parent.left; right: parent.right
      }

      //Desktop.ToolButton {
      //  text: Sk.tr("Add")
      //  tooltip: qsTr("Add a new entry")
      //  visible: root_.canSubmit
      //  onClicked: root_.createComment()
      //}
      Desktop.ToolButton {
        text: Sk.tr("Edit")
        tooltip: qsTr("Edit the selected entry")
        visible: root_.canEdit
        onClicked: root_.editCurrentItem()
      }
      Desktop.ToolButton {
        text: Sk.tr("Remove")
        tooltip: qsTr("Remove the selected entry")
        visible: root_.canEdit
        onClicked: root_.deleteCurrentItem()
      }
      Desktop.ToolButton {
        text: Sk.tr("Duplicate")
        tooltip: qsTr("Clone the selected entry")
        visible: root_.canSubmit
        onClicked: root_.cloneCurrentItem()
      }
      Desktop.ToolButton {
        text: Sk.tr("Improve")
        tooltip: qsTr("Override the selected entry")
        visible: root_.canImprove
        onClicked: root_.improveCurrentItem()
      }
      Desktop.ToolButton {
        text: Sk.tr("User")
        tooltip: Sk.tr("Show {0}").replace('{0}'), Sk.tr("user information")
        visible: !!root_.currentItem
        onClicked: {
          var item = root_.currentItem
          if (item)
            mainPlugin_.showUserWithHash(item.userId, item.userHash)
        }
      }
      Desktop.ToolButton {
        text: Sk.tr("Game")
        tooltip: Sk.tr("Show {0}").replace('{0}'), Sk.tr("game information")
        visible: !!root_.currentItem && root_.currentItem.gameId
        onClicked:
          if (root_.currentItem)
            mainPlugin_.showGameView(root_.currentItem.gameId)
      }
    }

    Row {
      anchors {
        verticalCenter: parent.verticalCenter
        left: parent.left; right: parent.right
        rightMargin: 10
      }
      spacing: 5
      layoutDirection: Qt.RightToLeft

      Desktop.ToolButton {
        text: Sk.tr("Help")
        tooltip: Sk.tr("Help")
        onClicked: mainPlugin_.showCommentHelp()
      }

      Desktop.ToolButton {
        text: Sk.tr("Wiki")
        tooltip: Sk.tr("Wiki")
        onClicked: mainPlugin_.openWiki('VNR/Sharing Subtitles')
      }

      Desktop.ToolButton {
        text: Sk.tr("Test")
        tooltip: My.tr("Test BBCode")
        onClicked: mainPlugin_.showBBCodeTester()
      }

      Desktop.ToolButton {
        text: Sk.tr("Statistics")
        visible: root_.notEmpty
        tooltip: qsTr("Plot statistics charts")
        onClicked: root_.model.showChart()
      }

      Desktop.ToolButton {
        text: Sk.tr("Export")
        visible: root_.notEmpty
        tooltip: qsTr("Save entries in Excel CSV format to the Desktop")
        onClicked: root_.model.export_()
      }

      Desktop.ToolButton {
        text: Sk.tr("Update")
        visible: !!root_.userId
        tooltip: qsTr("Update entries online")
        onClicked: root_.model.update()
      }
    }
  }

  property bool canSubmit: !!userId && !!currentItem
  property bool canImprove: canSubmit && (canEdit ||
      (userId !== _GUEST_USER_ID && !currentItem.locked))
  property bool canEdit: canEditable(currentItem)

      
      
  function canEditable(c) {
    var userAccess = [];
    if(statusPlugin_.userAccess){
        var userAccessMass = statusPlugin_.userAccess.split(',');
        for(var i = 0; i < userAccessMass.length; i++){
            userAccess[userAccess.length] = userAccessMass[i];
        }
    }

    return canSubmit && (userId === _SUPER_USER_ID
      || currentItem.userId === userId && !currentItem.protected
      || userAccess.length > 0 && (userAccess.indexOf(c.userId+':'+datamanPlugin_.gameItemId)>=0)
      || currentItem.userId === _GUEST_USER_ID && userLevel > 0);
  }
  //function createComment() {
  //  datamanPlugin_.createComment('target', My.tr("Matched text"), My.tr("Replaced text"))
  //}
  function editCurrentItem() {
    if (currentItem)
      mainPlugin_.showSubtitleEditor(currentItem)
      //subedit_.showComment(currentItem)
  }
  function deleteCurrentItem() {
    if (currentItem)
      datamanPlugin_.deleteComment(currentItem)
  }
  function cloneCurrentItem() {
    if (currentItem)
      datamanPlugin_.duplicateComment(currentItem)
  }
  function improveCurrentItem() {
    if (currentItem)
      datamanPlugin_.improveComment(currentItem)
  }
}

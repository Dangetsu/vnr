/** toolbar.qml
 *  2/21/2013 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My

Item { id: root_
  height: 40

  property QtObject model // gameman.ReferenceModel
  property QtObject currentItem // dataman.Reference
  property int userId
  property int gameId

  // - Private -

  property bool notEmpty: !!model && model.count > 0

  property int _SUPER_USER_ID: 2
  property int _GUEST_USER_ID: 4
  //property string _SUPER_USER: ' '

  property bool canSubmit: !!(userId && gameId &&
      !(userId === _GUEST_USER_ID && model.activeItem))
  //property bool canImprove: canSubmit && (canEdit || (userId !== _GUEST_USER_ID && !!currentItem && currentItem.userId !== userId && !currentItem.locked))
  property bool canEdit: canSubmit && !!currentItem && (userId === _SUPER_USER_ID
      || currentItem.userId === userId && !currentItem.protected)
  property bool canRemove: canEdit && userId !== _GUEST_USER_ID

  //gradient: Gradient {
  //  GradientStop { position: 0.0;  color: '#c8c9d0' }
  //  GradientStop { position: 0.17; color: '#dfdfe3' }
  //  GradientStop { position: 0.77; color: '#f1f1f3' }
  //  GradientStop { position: 1.0;  color: '#f0f0f3' }
  //}

  Plugin.MainObjectProxy { id: main_ }

  Plugin.ReferenceInput { id: refinput_ }
  Plugin.Growl { id: growlPlugin_ }

  function submitReference(ref) { model.submitItem(ref) } // as model is load delayed

  Component.onCompleted:
    refinput_.referenceSelected.connect(submitReference)
    //if (model.count <=0)
    //  refinput_.show()

  function addItem() { refinput_.showGame(gameId) }

  Desktop.ToolBar {
    anchors.fill: parent
    anchors.leftMargin: 5

    Row {
      spacing: 5
      anchors {
        verticalCenter: parent.verticalCenter
        left: parent.left; right: parent.right
      }

      Desktop.ToolButton {
        text: Sk.tr("Add")
        tooltip: qsTr("Add a new entry")
        visible: root_.canSubmit
        onClicked: addItem()
      }
      //Desktop.ToolButton {
      //  text: Sk.tr("Edit")
      //  tooltip: qsTr("Edit the selected entry")
      //  visible: root_.canEdit
      //  onClicked: root_.editCurrentItem()
      //}
      Desktop.ToolButton {
        text: Sk.tr("Remove")
        tooltip: qsTr("Remove the selected entry")
        visible: root_.canRemove
        onClicked: if (currentItem) model.removeItem(currentItem)
      }
      Desktop.ToolButton {
        text: Sk.tr("Browse")
        tooltip: qsTr("Open the selected entry")
        visible: !!root_.currentItem
        onClicked:
          if (currentItem && currentItem.url) {
            growlPlugin_.msg(My.tr("Open in external browser"))
            Qt.openUrlExternally(currentItem.url)
            //'http://amazon.co.jp/gp/product/black-curtain-redirect.html?ie=UTF8&redirect=true&redirectUrl=%2Fgp%2Fproduct%2F'
            //'http://amazon.co.jp/dp/' + currentItem.key
          }
      }
      //Desktop.ToolButton {
      //  text: Sk.tr("Duplicate")
      //  tooltip: qsTr("Clone the selected entry")
      //  visible: root_.canSubmit
      //  onClicked: root_.cloneCurrentItem()
      //}
      //Desktop.ToolButton {
      //  text: Sk.tr("Improve")
      //  tooltip: qsTr("Override the selected entry")
      //  visible: root_.canImprove
      //  onClicked: root_.improveCurrentItem()
      //}
      Desktop.ToolButton {
        text: Sk.tr("User")
        tooltip: Sk.tr("Show {0}").replace('{0}'), Sk.tr("user information")
        visible: !!root_.currentItem
        onClicked: {
          var item = root_.currentItem
          if (item)
            main_.showUserWithHash(item.userId, item.userHash)
        }
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
        onClicked: main_.showReferenceHelp()
      }

      //Desktop.ToolButton {
      //  text: Sk.tr("Statistics")
      //  visible: root_.notEmpty
      //  tooltip: qsTr("Plot statistics charts")
      //  onClicked: root_.model.showChart()
      //}

      //Desktop.ToolButton {
      //  text: Sk.tr("Export")
      //  visible: root_.notEmpty
      //  tooltip: qsTr("Save entries as XML to the Desktop")
      //  onClicked: root_.model.export_()
      //}

      Desktop.ToolButton {
        text: Sk.tr("Update")
        visible: !!root_.userId
        tooltip: qsTr("Update entries online")
        onClicked: root_.model.update()
      }
    }
  }
}

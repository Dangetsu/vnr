/** selecttoolbar.qml
 *  5/27/2014 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import '../../../js/sakurakit.min.js' as Sk

Item { id: root_
  height: 40

  property int selectionCount
  property QtObject model // dataman.TermModel

  // - Private -

  Desktop.ToolBar {
    anchors.fill: parent
    anchors.leftMargin: 5

    Row { id: firstRow_
      anchors {
        verticalCenter: parent.verticalCenter
        left: parent.left
        //rightMargin: 10
      }
      spacing: 5
      //layoutDirection: Qt.RightToLeft

      width: 100

      Desktop.ToolButton {
        text: Sk.tr("Cancel") + " (" + root_.selectionCount + ")"
        tooltip: qsTr("Cancel the selection")
        onClicked: root_.model.clearSelection()
      }
    }

    Row {
      spacing: 5
      anchors {
        verticalCenter: parent.verticalCenter
        left: firstRow_.right; right: parent.right
      }

      Desktop.ToolButton {
        text: Sk.tr("Remove")
        tooltip: qsTr("Remove the selected entries")
        //visible: root_.canEdit
        onClicked: root_.model.deleteSelection()
      }

      Desktop.ToolButton {
        text: Sk.tr("Disable")
        tooltip: qsTr("Disable the selected entries")
        //visible: root_.canEdit
        onClicked: root_.model.disableSelection()
      }

      Desktop.ToolButton {
        text: Sk.tr("Enable")
        tooltip: qsTr("Enable the selected entries")
        //visible: root_.canEdit
        onClicked: root_.model.enableSelection()
      }

      Desktop.ToolButton {
        text: Sk.tr("Comment")
        tooltip: qsTr("Edit comment for the selected entries")
        //visible: root_.canEdit
        onClicked: root_.model.commentSelection()
      }
    }
  }
}

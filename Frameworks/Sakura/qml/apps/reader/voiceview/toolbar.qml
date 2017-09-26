/** toolbar.qml
 *  6/22/2013 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
//import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My

Item { id: root_
  height: 40

  property bool enabled
  property QtObject model // gameman.CharacterModel
  property QtObject currentItem // dataman.Character

  // - Private -

  //Plugin.MainObjectProxy { id: main_ }

  function toggleEnabled() {
    //settingsPlugin_.voiceCharacterEnabled = !enabled
    if (enabled)
      settingsPlugin_.voiceCharacterEnabled = false
    else
      settingsPlugin_.speaksGameText = settingsPlugin_.voiceCharacterEnabled = true
  }

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
      //  enabled: root_.canSubmit
      //  visible: enabled
      //  onClicked: if (enabled) root_.createComment()
      //}
      Desktop.ToolButton {
        text: Sk.tr("Remove")
        tooltip: qsTr("Remove the selected entry")
        visible: root_.enabled && !!root_.currentItem && !!currentItem.name // prevent remove aside voice
        onClicked:
          if (currentItem)
            model.removeItem(currentItem)
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
        text: root_.enabled ? Sk.tr("Disable") : Sk.tr("Enable")
        tooltip: qsTr("Whether dub voices for game characters")
        onClicked: root_.toggleEnabled()
      }

      Desktop.ToolButton {
        text: Sk.tr("Help")
        tooltip: Sk.tr("Help")
        onClicked: mainPlugin_.showVoiceHelp()
      }

      Desktop.ToolButton {
        text: Sk.tr("Wiki")
        tooltip: Sk.tr("Wiki")
        onClicked: mainPlugin_.openWiki('VNR/Voice Settings')
      }

      Desktop.ToolButton {
        text: Sk.tr("Clear")
        tooltip: Sk.tr("Clear")
        visible: root_.enabled && model.count > 0
        onClicked: model.clearItems()
      }

      Desktop.ToolButton {
        text: Sk.tr("Refresh")
        tooltip: Sk.tr("Refresh")
        visible: root_.enabled && model.count > 0
        onClicked: model.purgeItems()
      }
    }
  }
}

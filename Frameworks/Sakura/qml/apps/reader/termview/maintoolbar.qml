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

  property QtObject currentItem // dataman.Term
  property int userId
  property int userLevel
  property bool enabled: false

  // - Private -

  property int _GUEST_USER_ID: 4
  property int _SUPER_USER_ID: 2

  //gradient: Gradient {
  //  GradientStop { position: 0.0;  color: '#c8c9d0' }
  //  GradientStop { position: 0.17; color: '#dfdfe3' }
  //  GradientStop { position: 0.77; color: '#f1f1f3' }
  //  GradientStop { position: 1.0;  color: '#f0f0f3' }
  //}

  //Plugin.MainObjectProxy { id: mainPlugin_ }
  //Plugin.DataManagerProxy { id: datamanPlugin_ }
  //Plugin.GameViewManagerProxy { id: gameview_ }
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

      Desktop.ToolButton {
        text: Sk.tr("Add")
        tooltip: qsTr("Add a new entry")
        visible: root_.canSubmit
        onClicked: root_.createTerm()
      }
      Desktop.ToolButton {
        text: Sk.tr("Remove")
        tooltip: qsTr("Remove the selected entry")
        visible: root_.canEdit
        onClicked: root_.deleteCurrentItem()
      }
      Desktop.ToolButton {
        text: Sk.tr("Replicate")
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
        visible: !!currentItem //&& root_.currentItem.userId
        onClicked:
          if (currentItem)
            mainPlugin_.showUserWithHash(currentItem.userId, currentItem.userHash)
      }
      Desktop.ToolButton {
        text: Sk.tr("Game")
        tooltip: Sk.tr("Show {0}").replace('{0}'), Sk.tr("game information")
        visible: !!(currentItem && currentItem.gameId)
        onClicked:
          if (currentItem)
            mainPlugin_.showGameView(currentItem.gameId)
      }
      Desktop.ToolButton {
        text: Sk.tr("Dictionary")
        tooltip: qsTr("Lookup pattern in the dictionary")
        visible: !!(currentItem && currentItem.pattern)
        onClicked:
          if (currentItem)
            mainPlugin_.lookupDictionaryTester(currentItem.pattern)
      }
      Desktop.ToolButton {
        text: My.tr("Speak")
        tooltip: qsTr("Speak pattern using TTS")
        visible: !!(currentItem && currentItem.pattern)
        onClicked:
          if (currentItem)
            ttsPlugin_.speak(currentItem.pattern, currentItem.sourceLanguage)
      }
      //Desktop.ToolButton { // TOO slow to compute
      //  text: Sk.tr("Name")
      //  tooltip: Sk.tr("Show {0}").replace('{0}'), My.tr("names")
      //  visible: !!(currentItem && currentItem.gameId && datamanPlugin_.queryGameItemId(currentItem.gameId))
      //  onClicked:
      //    if (currentItem) {
      //      var id = currentItem.gameId
      //      if (id) {
      //        id = datamanPlugin_.queryGameItemId(id)
      //        if (id)
      //          mainPlugin_.showGameNames(id)
      //      }
      //    }
      //}
      //Desktop.ToolButton {
      //  text: currentItem && currentItem.disabled ? Sk.tr("Enable") : Sk.tr("Disable")
      //  tooltip: qsTr("Enable or disable the selected entry")
      //  visible: root_.canImprove
      //  onClicked:
      //    if (currentItem.disabled)
      //      root_.enableCurrentItem()
      //    else
      //      root_.disableCurrentItem()
      //}
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
        tooltip: qsTr("Whether use user-defined terms to improve machine translation")
        onClicked: root_.enabled = !root_.enabled
      }

      Desktop.ToolButton {
        text: Sk.tr("Help")
        tooltip: Sk.tr("Help")
        onClicked: mainPlugin_.showTermHelp()
      }

      Desktop.ToolButton {
        text: Sk.tr("Wiki")
        tooltip: Sk.tr("Wiki")
        onClicked: mainPlugin_.openWiki('VNR/Shared Dictionary')
      }

      //Desktop.ToolButton {
      //  text: qsTr("Discuss")
      //  tooltip: qsTr("Visit the discussion page online")
      //  onClicked: Qt.openUrlExternally('http://sakuradite.com/subject/102')
      //}

      Desktop.ToolButton {
        text: Sk.tr("Test")
        visible: root_.enabled
        tooltip: My.tr("Test machine translation")
        onClicked: mainPlugin_.showMachineTranslationTester()
      }

      // Temporarily disabled for being too slow
      //Desktop.ToolButton {
      //  text: Sk.tr("Statistics")
      //  visible: root_.enabled
      //  tooltip: qsTr("Plot statistics charts")
      //  onClicked: mainPlugin_.showTermChart()
      //}

      Desktop.ToolButton {
        text: Sk.tr("Export")
        visible: root_.enabled
        tooltip: qsTr("Save entries in Excel CSV format to the Desktop")
        onClicked: datamanPlugin_.exportTerms()
      }

      Desktop.ToolButton {
        text: Sk.tr("Browse")
        visible: root_.enabled && !!root_.userId
        tooltip: qsTr("Browse current enabled rules")
        onClicked: mainPlugin_.showTermCache()
      }

      Desktop.ToolButton {
        text: Sk.tr("Update")
        visible: root_.enabled && !!root_.userId
        tooltip: qsTr("Update entries online")
        onClicked: datamanPlugin_.updateTerms()
      }
    }
  }

  property bool canSubmit: enabled && !!userId
  property bool canImprove: canSubmit && (canEdit || userId !== _GUEST_USER_ID)
  property bool canEdit: canSubmit && !!currentItem && (userId === _SUPER_USER_ID
      || currentItem.userId === userId && !currentItem.protected
      || currentItem.userId === _GUEST_USER_ID && userLevel > 0)

  function createTerm() {
    //datamanPlugin_.createTerm('output', My.tr("Matched text"), My.tr("Replaced text"))
    mainPlugin_.showTermInput()
  }
  function deleteCurrentItem() {
    if (currentItem)
      datamanPlugin_.deleteTerm(currentItem)
  }
  function cloneCurrentItem() {
    if (currentItem)
      datamanPlugin_.replicateTerm(currentItem)
  }
  function improveCurrentItem() {
    if (currentItem)
      datamanPlugin_.improveTerm(currentItem)
  }
  //function enableCurrentItem() {
  //  if (currentItem) {
  //    currentItem.disabled = false
  //    currentItem.updateUserId = userId
  //    currentItem.updateTimestamp = Util.currentUnixTime()
  //  }
  //}
  //function disableCurrentItem() {
  //  if (currentItem)
  //    datamanPlugin_.disableTerm(currentItem)
  //}
}

/** optionbar.qml
 *  6/30/2013 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin

Item { id: root_

  height: 40

  // - Private -

  Plugin.DataManagerProxy { id: dataman_
    onGameMd5Changed: loadSettings()
  }

  Component.onCompleted: loadSettings()

  function loadSettings() {
    defaultEnabled = dataman_.queryGameVoiceDefaultEnabled(dataman_.gameMd5)
  }
  function saveSettings() {
    dataman_.setGameVoiceDefaultEnabled(dataman_.gameMd5, defaultEnabled)
  }

  property alias defaultEnabled: defaultEnabledButton_.checked
  onDefaultEnabledChanged: saveSettings()

  property int _MARGIN: 10

  Desktop.CheckBox { id: defaultEnabledButton_
    anchors {
      verticalCenter: parent.verticalCenter
      left: parent.left
      leftMargin: _MARGIN
    }
    //width: 150
    //enabled: root_.canLock
    //visible: status_.online && root_.canLock
    //text: ' ' + qsTr("Enable voices for new characters")
    text: ' ' + qsTr("Dub voices for newly discovered characters (disabled by default)")

    //Desktop.TooltipArea{
    //  anchors {
    //    fill: parent
    //    leftMargin: 20
    //  }
    //  text: qsTr("Dub voices for newly discovered characters (disabled by default)")
    //}
  }
}

/** voiceview.qml
 *  6/22/2013 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../js/sakurakit.min.js' as Sk
import '../../js/reader.min.js' as My
import '../../js/util.min.js' as Util
import 'share' as Share
import 'voiceview' as VoiceView

Share.View { id: root_
  //implicitWidth: 480; implicitHeight: 360
  width: 500; height: 350

  // Window properties
  property string windowTitle: title() ///< window title
  function title() {
    var ret = My.tr("Voice Settings")
    if (model_.count > 0)
      ret += " (" + model_.count + ")"
    // Never empty
    //else
    //  ret += " (" + Sk.tr("Empty") + ")"
    //if (game)
    //  ret += " - " + game.name
    return ret
  }

  //property QtObject game // dataman.GameObject, to be set by constructor

  // - Private -

  Component.onCompleted: console.log("voiceview.qml: pass")
  Component.onDestruction: console.log("voiceview.qml:destroy: pass")

  property bool enabled: settingsPlugin_.speaksGameText && settingsPlugin_.voiceCharacterEnabled
  //property bool enabled: settingsPlugin_.voiceCharacterEnabled

  Plugin.VoiceModel { id: model_
    sortingColumn: table_.sortIndicatorColumn
    sortingReverse: table_.sortIndicatorDirection === 'up'

    filterText: Util.trim(searchBox_.text)
  }

  Plugin.Settings { id: settingsPlugin_ }

  Plugin.MainObjectProxy { id: mainPlugin_ }

  //Plugin.SystemStatus { id: status_ }
  //property int userId: status_.online ? status_.userId : 0

  //function loadSettings() {
  //  toolBar_.enabled = settings_.termEnabled
  //}
  //function saveSettings() {
  //  settings_.termEnabled = toolBar_.enabled
  //}

  // ToolBar at the top

  VoiceView.ToolBar { id: toolBar_
    anchors {
      left: parent.left; right: parent.right; top: parent.top
      topMargin: -1
    }
    enabled: root_.enabled

    model: model_
    //currentGame: root_.game
    currentItem: table_.currentItem
    //userId: root_.userId

    //Component.onCompleted: enabled = settings_.termEnabled
    //onEnabledChanged:
    //  if (enabled !== settings_.termEnabled)
    //    settings_.termEnabled = enabled
  }

  // Table
  VoiceView.Table { id: table_
    anchors {
      left: parent.left; right: parent.right
      top: toolBar_.bottom; bottom: searchBox_.top
    }
    model: model_
    //userId: root_.userId
    //currentGame: root_.game
    //filterText: Util.trim(searchBox_.text)

    property QtObject currentItem: model.get(currentIndex) // dataman.Comment

    Share.Blocker {
      anchors.fill: parent
      //visible: model_.currentCount <= 0 || !root_.enabled
      //text: (root_.enabled ? Sk.tr("Empty") : Sk.tr("Disabled")) + "! ><"
      visible: !root_.enabled
      text: Sk.tr("Disabled") + "! ><"

      Desktop.TooltipArea {
        anchors.fill: parent
        text: qsTr("Automatic TTS or dub voices is disabled by you")
      }
    }
  }

  Share.SearchBox { id: searchBox_
    anchors {
      left: parent.left; right: parent.right
      bottom: optionBar_.top
      //bottom: parent.bottom
      bottomMargin: 5
    }
    totalCount: model_.count
    currentCount: model_.currentCount
    //toolTip: qsTr("Type part of the text, and press Enter to search")
    //onAccepted: model_.filterText = Util.trim(text)
  }

  VoiceView.OptionBar { id: optionBar_
    anchors {
      left: parent.left; right: parent.right
      bottom: parent.bottom
    }
  }
  //VoiceView.Footer { id: footer_
  //  anchors {
  //    left: parent.left; right: parent.right
  //    bottom: parent.bottom
  //  }
  //}
}

/** refview.qml
 *  6/1/2013 jichi
 */
import QtQuick 1.1
//import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../js/sakurakit.min.js' as Sk
import '../../js/eval.min.js' as Eval
import '../../js/util.min.js' as Util
import 'share' as Share
import 'refview' as RefView

Share.View { id: root_
  //implicitWidth: 480; implicitHeight: 360
  width: 680; height: 400

  // Window properties
  property string windowTitle: title() ///< window title
  function title() {
    var ret = Sk.tr("Name")
    if (!gameId)
      return ret
    ret += ": " + datamanPlugin_.queryGameFileName(gameId) + " ="
    var item = model_.activeItem
    if (!item)
      ret += " (" + Sk.tr("not specified") + ")"
    else
      ret += "「" + item.title + "」"
    return ret

    //if (model_.count > 0)
    //  ret += " (" + model_.count + ")"
    //else
    //  ret += " (" + Sk.tr("Empty") + ")"
    //if (game)
    //  ret += " - " + game.name
    //return ret
  }

  // - Private -

  property int gameId

  Component.onCompleted: {
    initEvalContext()
    console.log("refview.qml: pass")
  }

  Component.onDestruction: console.log("refview.qml:destroy: pass")

  function initEvalContext() {
    var ctx = Eval.scriptContext
    ctx.main = mainPlugin_
    ctx.growl = growlPlugin_
    //ctx.clipboard = clipboardPlugin_
  }

  Plugin.MainObjectProxy { id: mainPlugin_ }
  Plugin.DataManagerProxy { id: datamanPlugin_ }

  Plugin.ReferenceModel { id: model_
    gameId: root_.gameId
    sortingColumn: table_.sortIndicatorColumn
    sortingReverse: table_.sortIndicatorDirection === 'up'

    filterText: Util.trim(searchBox_.text)
  }

  //Plugin.Settings { id: settings_ }

  Plugin.SystemStatus { id: status_ }
  Plugin.Growl { id: growlPlugin_ }
  property int userId: status_.online ? status_.userId : 0

  //function loadSettings() {
  //  toolBar_.enabled = settings_.termEnabled
  //}
  //function saveSettings() {
  //  settings_.termEnabled = toolBar_.enabled
  //}

  // ToolBar at the top

  RefView.ToolBar { id: toolBar_
    anchors {
      left: parent.left; right: parent.right; top: parent.top
      topMargin: -1
    }

    model: model_
    //currentGame: root_.game
    currentItem: table_.currentItem
    userId: root_.userId
    gameId: root_.gameId

    //Component.onCompleted: enabled = settings_.termEnabled
    //onEnabledChanged:
    //  if (enabled !== settings_.termEnabled)
    //    settings_.termEnabled = enabled
  }

  // Table
  RefView.Table { id: table_
    anchors {
      left: parent.left; right: parent.right
      top: toolBar_.bottom; bottom: searchBox_.top
    }
    model: model_
    userId: root_.userId
    gameId: root_.gameId
    //currentGame: root_.game
    //filterText: Util.trim(searchBox_.text)

    property QtObject currentItem: model.get(currentIndex) // dataman.Comment

    Share.Blocker {
      anchors.fill: parent
      visible: model_.currentCount <= 0
    }
  }

  Share.SearchBox { id: searchBox_
    anchors {
      left: parent.left; right: parent.right
      bottom: inspector_.top
      bottomMargin: 5
    }
    totalCount: model_.count
    currentCount: model_.currentCount
    toolTip: qsTr("Type part of the title, user, etc.")
           + " (" + Sk.tr("regular expression") + ", " + Sk.tr("case-insensitive") + ")"
    //onAccepted: model_.filterText = Util.trim(text)

    placeholderText: Sk.tr("Search") + " ... (" + holder() + ")"
    function holder() {
      return '@' + Sk.tr('user') + ", " + '#' + Sk.tr("game") + ", " + '#' + Sk.tr("game")
    }
  }

  // Inspector at the bottom
  RefView.Inspector { id: inspector_
    anchors {
      left: parent.left; right: parent.right
      bottom: parent.bottom
    }
    currentItem: table_.currentItem
    model: model_
  }
}

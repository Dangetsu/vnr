/** springboard.qml
 *  9/29/2012 jichi
 *  SpringBoard root_ element. Rendered within a window.
 *
 *  Hierarchy:
 *  - SpringBoard: root_ rectangle
 *    - Drawer: curtain container
 *      - Curtain: contain panel
 *    - Desktop: dashboard manager
 *      - Dock
 *      - Dashboard: app manager
 *        - Games: galgame
 *        - Applets: utilities
 */
import QtQuick 1.1
import org.sakuradite.reader 1.0 as Plugin
import '../../js/sakurakit.min.js' as Sk
import '../../js/reader.min.js' as My
import '../../js/eval.min.js' as Eval
import '../../js/util.min.js' as Util
import 'comet' as Comet
import 'share' as Share
import 'springboard' as SpringBoard

Item { id: root_
  width: 480; height: 600

  // Window properties
  property string windowTitle: title()
  property int windowFlags: Qt.Dialog | Qt.WindowMinMaxButtonsHint

  // - Private -

  function title() {
    var ret = My.tr("Spring Board") + " - " //+ " - " + My.tr("Visual Novel Reader") ///< window title
    var count = gameModel_.count
    var cur = gameModel_.currentCount
    if (count <= 0)
      ret += Sk.tr("Empty") + "><"
    else if (!root_.searchText)
      ret += My.tr("{0} games").replace('{0}', count)
    else if (cur > 0)
      ret += My.tr("{0} games").replace('{0}', cur + "/" + count)
    else
      ret += Sk.tr("Not found") + "><"
    return ret
  }

  //property int topMargin: drawer_.drawerHeight / 3
  property int topMargin: 0

  Component.onCompleted: {
    initEvalContext()
    console.log("springboard.qml: pass")
  }

  function initEvalContext() {
    var ctx = Eval.scriptContext
    ctx.main = mainPlugin_
    ctx.growl = growlPlugin_
    //ctx.clipboard = clipboardPlugin_
  }

  property string searchText: Util.trim(searchBar_.text) // cached

  // - Background -

  //gradient: Gradient {
  //  GradientStop { position: 0.0;  color: '#8c8f8c' }
  //  GradientStop { position: 0.17; color: '#6a6d6a' }
  //  GradientStop { position: 0.77; color: '#3f3f3f' }
  //  GradientStop { position: 1.0;  color: '#6a6d6a' }
  //}
  //color: '#343434'
  //Image { source: 'image://rc/stripes'; fillMode: Image.Tile; anchors.fill: parent; opacity: 0.3 }

  //Comet.GlobalComet { id: globalComet_ } // replaced by gComet

  Plugin.SystemStatus { id: statusPlugin_ }
  Plugin.MainObjectProxy { id: mainPlugin_ }
  Plugin.DataManagerProxy { id: datamanPlugin_ }
  Plugin.ClipboardProxy { id: clipboardPlugin_ }
  Plugin.Tts { id: ttsPlugin_ }
  Plugin.Settings { id: settingsPlugin_ }
  Plugin.Growl { id: growlPlugin_ }

  Plugin.Util { id: util_ }

  // - Context Menu -

  MouseArea {
    anchors.fill: parent
    acceptedButtons: Qt.RightButton
    onPressed: appMenu_.showPopup(mouseX, mouseY)
  }

  // - Dashboards -

  SpringBoard.Desktop {
    anchors {
      fill: parent
      topMargin: root_.topMargin
    }

    topMargin: root_.width / 4

    //backgroundSize.height: root_.height *2 // tracking width is enough, crash if track both
    backgroundSize.width: root_.width * 2

    //backgroundSource: "http://annot.me/images/yin.jpg"
    //backgroundSource: "http://annot.me/images/wallpaper/1.jpg"
    //backgroundSource: "http://annot.me/images/wallpaper/2.jpg"
    backgroundSource: util_.urlExists(settingsPlugin_.springBoardWallpaperUrl) ? settingsPlugin_.springBoardWallpaperUrl :
                      'image://rc/wallpaper'

    foregroundSize.width: root_.width
    foregroundSize.height: root_.height
    foregroundSource: {
      var game = gameDashboard_.currentObject
      if (game) {
         var url = game.image()
         if (url && url.indexOf('http')) // if not starts with http
           //return url
           return 'image://spring/' + url
      }
      return ''
    }

    model: VisualItemModel {
      // Dashboad #1: Games
      SpringBoard.Dashboard { id: gameDashboard_
        width: root_.width; height: root_.height
        model: Plugin.GameModel { id: gameModel_
          filterText: root_.searchText
          filterGameType: inspector_.selectedGameType
        }

        property QtObject currentObject: model ? model.get(currentIndex) : undefined
        //searchText: root_.searchText
        highlight: !!root_.searchText

        //Component.onCompleted:
        //  contextMenuAt.connect(appMenu_.showPopup)
      }

      // Dashboard #2: Applets
      SpringBoard.Dashboard { id: appletDashboard_
        width: root_.width; height: root_.height
        model: SpringBoard.AppModel {}

        //Component.onCompleted:
        //  contextMenuAt.connect(appMenu_.showPopup)
      }
    }
  }

  Share.Blocker {
    anchors.fill: parent
    visible: gameModel_.currentCount <= 0
    textColor: '#333'
    text: (gameModel_.count > 0 ? Sk.tr("Not found") : Sk.tr("Empty")) + "! ><"
  }

  // Dock view
  SpringBoard.Dock { id: dock_
    anchors {
      horizontalCenter: parent.horizontalCenter
      bottom: inspector_.visible ? inspector_.top : parent.bottom
    }
    height: 50; width: Math.min(count * 50, parent.width - 20)
    //interactive: width === parent.width - 20
    orientation: Qt.Horizontal

    model: SpringBoard.DockModel {}
    Component.onCompleted: contentX = -50 // Why I have to manually do this?
  }

  SpringBoard.Inspector { id: inspector_
    anchors {
      left: parent.left; right: parent.right
      bottom: parent.bottom
    }

    visible: !!game

    game: gameDashboard_.currentObject

    SpringBoard.CometCounter { //id: counter_
      anchors {
        right: parent.right
        bottom: parent.bottom
        bottomMargin: 3
        rightMargin: 108 // larger than bottom buttons
      }
      count: gComet.connectionCount
      //visible: gComet.active && count > 1 //&& settingsPlugin_.cometCounterVisible
      visible: statusPlugin_.online

      text: count > 1 ? My.tr("Message") + " " + count : My.tr("Message")
      width: 80

      onClicked: {
        running = false
        mainPlugin_.showGlobalChatView()
      }

      Component.onCompleted: {
        gComet.postReceived.connect(start)
        gComet.postUpdated.connect(start)
      }

      function start() {
        if (!mainPlugin_.isGlobalChatViewVisible())
          running = true
      }
    }

    Share.InputBar { id: searchBar_
      anchors {
        left: parent.left
        //bottom: inspector_.visible ? inspector_.top : parent.bottom
        bottom: parent.bottom

        //right: activeFocus ? parent.right : dock_.left
        //leftMargin: 8; bottomMargin: 12
        leftMargin: 4; bottomMargin: 4
      }
      //radius: 10

      property int _ACTIVE_WIDTH: root_.width * 0.4
      property int _INACTIVE_WIDTH: root_.width * 0.2
      width: _INACTIVE_WIDTH
      states: [
        State { // default
          when: !searchBar_.activeFocus
          PropertyChanges { target: searchBar_
            width: _INACTIVE_WIDTH
            placeholderText: Sk.tr("Search") + " ..."
          }
        }
        , State { // active
          when: searchBar_.activeFocus
          PropertyChanges { target: searchBar_
            width: _ACTIVE_WIDTH
            placeholderText: Sk.tr("Search") + " ... (" + Sk.tr("regex") + ")"
         }
        }
      ]
      transitions: Transition {
        SmoothedAnimation { property: 'width' }
        //NumberAnimation { property: 'width' }
        //SpringAnimation {
        //  property: 'width'
        //  spring: 1.5; damping: 0.1 // spring: strength; damping: speed
        //}
      }

      toolTip: qsTr("You can type part of the game name or path here")
      visible: gameModel_.count > 0
      Share.ClearButton {
        anchors {
          right: parent.right
          verticalCenter: parent.verticalCenter
          rightMargin: 2
        }
        onClicked: parent.text = ""
      }
    }
  }

  //SpringBoard.Drawer { id: drawer_
  //  anchors.fill: parent
  //}

  SpringBoard.AppMenu { id: appMenu_ }
}

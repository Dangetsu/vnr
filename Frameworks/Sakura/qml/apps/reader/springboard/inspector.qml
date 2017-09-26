/** inspector.qml
 *  1/6/2013 jichi
 *  Game inspector
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/util.min.js' as Util
import '../../../components/bootstrap3' as Bootstrap
import '../../../components/buttongroup' as ButtonGroup
import '../share' as Share

Rectangle { id: root_

  property QtObject game // dataman.GameObject

  property string selectedGameType:
      junaiButton_.checked ? 'junai' :
      nukiButton_.checked ? 'nuki' :
      otomeButton_.checked ? 'otome' :
      ''

  // - Private -

  //height: 30
  //height: 50
  height: topRegion_.height + bottomRegion_.height
  color: '#ddced0d6' // opacity: 0xdd/0xff = 87%

  //property bool containsMouse:
  //  toolTip_.containsMouse ||
  //  openButton_.hover || editButton_.hover || subButton_.hover ||
  //  infoButton_.hover || browseButton_.hover || removeButton_.hover ||
  //  allButton_.hover || junaiButton_.hover || nukiButton_.hover || otomeButton_.hover

  //Plugin.MainObjectProxy { id: mainPlugin_ }
  Plugin.GameManagerProxy { id: gameman_ }
  Plugin.GameEditorManagerProxy { id: gameedit_ }
  //Plugin.GameViewManagerProxy { id: gameview_ }

  //Desktop.TooltipArea { id: toolTip_
  //  anchors.fill: parent
  //  //text: game ? (game.launchPath ? game.launchPath : game.path) : ""
  //  //text: qsTr("Click to copy the game information to the clipboard and read the text using TTS")
  //  text: qsTr("Click to copy the game information to the clipboard")
  //}

  // - Label -

  //MouseArea {
  //  anchors.fill: parent
  //  acceptedButtons: Qt.LeftButton
  //  onPressed:
  //    if (game) {
  //      var t = game.name
  //      if (t) {
  //        var l = [t]
  //        t = game.brand
  //        if (t) l.push(t)
  //        //t = game.tags
  //        //if (t) l.push(t)
  //        t = l.join("、")
  //        clipboardPlugin_.text = t
  //        //ttsPlugin_.speak(t, 'ja')
  //      }
  //    }
  //}

  // Top region
  Item { id: topRegion_
    anchors {
      left: parent.left; right: parent.right
      top: parent.top
      //bottom: parent.bottom
    }
    height: 50

    Image { id: gameIcon_
      anchors {
        verticalCenter: parent.verticalCenter
        left: parent.left
        leftMargin: 9
      }
      //smooth: true
      //property int size: containsMouse ? 48 : 24
      //sourceSize.width: 24; sourceSize.height: 24
      sourceSize.width: 48; sourceSize.height: 48

      source: game ? 'image://file/' + game.path : '' //'image://rc/game'
    }

    TextEdit { id: nameLabel_
      anchors {
        verticalCenter: parent.verticalCenter
        left: gameIcon_.right
        right: toolbar_.left
        leftMargin: 9; rightMargin: 4
      }
      font.pixelSize: 12
      //font.family: 'MS HGothic'
      //font.family: 'Meiryo'
      //font.bold: root_.containsMouse
      //color: root_.containsMouse ? 'snow' : 'black'
      effect: Share.TextEffect {} // highlight: root_.containsMouse }
      wrapMode: TextEdit.WordWrap
      textFormat: TextEdit.RichText
      text: !game ? '' : renderGame(game)

      selectByMouse: true
      //readOnly: true

      function renderGame(g) { // game -> string
        var ret = g.name
        if (!g.known)
          ret += " <span style='color:red'>(" + Sk.tr('Unknown') + ")</span>"
        else {
          var sz = g.fileSizeString
          if (sz)
            ret += " <span style='color:darkgreen'>" + sz.replace(' ', '') + "</span>"
          var brand = g.brand
          if (g.language && g.language !== 'ja')
            ret += " <span style='color:crimson'>(" + Sk.tr(Util.languageShortName(g.language)) + ")</span>"
          if (brand)
            ret += " <span style='color:purple'>@" + brand.replace(/,/g, " @") + "</span>"
          var tags = g.tags
          if (tags)
            ret += " <span style='color:darkblue'>" + tags + "</span>"
          //  ret += " <span style='color:darkblue'>*" + tags.replace(/,/g, " *") + "</span>"
          var ts = g.date
          if (ts > 0) {
            ts = Util.datestampToString(ts)
            ret += " <span style='color:brown'>" + ts + "</span>"
          }
        }
        return ret
      }
    }

    // - Buttons -

    Grid { id: toolbar_
      anchors {
        verticalCenter: parent.verticalCenter
        right: parent.right
        rightMargin: 2
        //right: parent.right; top: parent.top
        //topMargin: 4
      }
      //height: 30
      rows: 2 //columns: 3
      //spacing: 5
      spacing: 1

      property int cellWidth: 50

      Bootstrap.Button { id: openButton_
        styleClass: 'btn btn-primary'
        width: parent.cellWidth
        //text: Sk.tr("Launch")
        text: qsTr("Launch")
        toolTip: qsTr("Launch the game, or attach to the running game") + " (" + Sk.tr("Double-click") + ")"
        onClicked: if (game) gameman_.open(game)
      }

      Bootstrap.Button { id: editButton_
        styleClass: 'btn btn-success'
        width: parent.cellWidth
        //text: Sk.tr("Edit")
        text: qsTr("Edit")
        toolTip: qsTr("Edit game properties")
        onClicked: if (game) gameedit_.showGame(game.md5)
      }

      //Bootstrap.Button { id: discussButton_
      //  //styleClass: 'btn btn-default'
      //  styleClass: 'btn btn-info'
      //  width: parent.cellWidth
      //  //text: Sk.tr("Browse")
      //  text: qsTr("Discuss")
      //  toolTip: qsTr("Visit the discussion page online")
      //  onClicked:
      //    if (game) {
      //      var id = game.itemId
      //      if (id)
      //        Qt.openUrlExternally('http://sakuradite.com/game/' + id)
      //      else
      //        growlPlugin_.warn(My.tr("Unknown game"))
      //    }
      //}

      Bootstrap.Button { id: subButton_
        styleClass: 'btn btn-inverse'
        width: parent.cellWidth
        text: My.tr("Sub")
        toolTip: qsTr("Edit shared subtitles")
        onClicked: if (game) mainPlugin_.showGameObjectSubtitles(game)
      }

      Bootstrap.Button { id: infoButton_
        styleClass: 'btn btn-info'
        width: parent.cellWidth
        text: My.tr("Info")
        toolTip: qsTr("Show game information")
        onClicked: if (game) mainPlugin_.showGameView(game.id)
      }

      Bootstrap.Button { id: browseButton_
        styleClass: 'btn btn-default'
        width: parent.cellWidth
        //text: Sk.tr("Browse")
        text: qsTr("Browse")
        toolTip: qsTr("Show the game folder")
        onClicked: if (game) gameman_.openDirectory(game)
      }

      Bootstrap.Button { id: removeButton_
        styleClass: 'btn btn-danger'
        width: parent.cellWidth
        //text: Sk.tr("Remove")
        text: qsTr("Remove")
        toolTip: qsTr("Remove this game from the dashboard")
        onClicked: if (game) gameman_.remove(game)
      }
    }
  }

  // Bottom region
  Item { id: bottomRegion_
    anchors {
      left: parent.left; right: parent.right
      //top: parent.top
      bottom: parent.bottom
    }
    height: 27

    Item { //id: scoreRow_
      anchors {
        top: parent.top; bottom: parent.bottom
        right: typeRow_.left
        rightMargin: 90 // large enough to skip
      }

      //visible: false // temporarily disabled

      width: scoreText_.width

      Desktop.TooltipArea { id: scoreTip_
        anchors.fill: parent
        text: Sk.tr("Review")
      }

      MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton
        onPressed:
          if (statusPlugin_.online && root_.game && root_.game.itemId)
            mainPlugin_.showGameTopics(root_.game.itemId)
      }

      Text { id: scoreText_
        //anchors.fill: parent
        anchors {
          top: parent.top; bottom: parent.bottom
          right: parent.right
        }
        visible: !!root_.game && root_.game.itemId > 0
        wrapMode: Text.NoWrap
        textFormat: Text.RichText

        horizontalAlignment: Text.AlignRight
        verticalAlignment: Text.AlignVCenter

        font.pixelSize: 12
        effect: Share.TextEffect {
          highlight: scoreTip_.containsMouse && statusPlugin_.online
          highlightColor: 'yellow'
        }
        text: !visible ? "" : renderGame(game)

        function renderGame(g) { // game -> string
          var ret = "<span style='color:darkblue'>%1 %3&times;%2</span>"
            .replace('%1', Sk.tr("Score"))
            .replace('%2', g.overallScoreCount)
            .replace('%3', g.overallScoreCount == 0 ? 0 : (g.overallScoreSum/g.overallScoreCount).toFixed(1))
          if (g.ecchiScoreCount)
            ret += " <span style='color:purple'>%1 %3&times;%2</span>"
              .replace('%1', My.tr("Ecchi"))
              .replace('%2', g.ecchiScoreCount)
              .replace('%3', (g.ecchiScoreSum/g.ecchiScoreCount).toFixed(1))
          if (g.topicCount)
            ret += " <span style='color:green'>%1 %2</span>"
              .replace('%1', Sk.tr("Topic"))
              .replace('%2', g.topicCount)
          return ret
        }
      }
    }

    ButtonGroup.ButtonRow { id: typeRow_
      //spacing: 5
      anchors {
        verticalCenter: parent.verticalCenter
        right: parent.right
        rightMargin: 2
        verticalCenterOffset: -1
        //right: parent.right; top: parent.top
        //topMargin: 4
      }
      spacing: 1

      property int cellWidth: 25
      property int cellHeight: 25
      //property real scale: 0.9

      Bootstrap.Button { id: allButton_
        styleClass: checked ? 'btn btn-inverse' : 'btn btn-default'
        checkable: true
        checked: true // select all button by default
        //scale: parent.scale
        width: parent.cellWidth
        height: parent.cellHeight
        text: "全"
        toolTip: "全て"
      }

      Bootstrap.Button { id: junaiButton_
        styleClass: checked ? 'btn btn-primary' : 'btn btn-default'
        checkable: true
        //scale: parent.scale
        width: parent.cellWidth
        height: parent.cellHeight
        text: "愛"
        toolTip: "純愛作"
      }

      Bootstrap.Button { id: nukiButton_
        styleClass: checked ? 'btn btn-info' : 'btn btn-default'
        checkable: true
        //scale: parent.scale
        width: parent.cellWidth
        height: parent.cellHeight
        text: "抜"
        toolTip: "抜き作"
      }

      Bootstrap.Button { id: otomeButton_
        styleClass: checked ? 'btn btn-success' : 'btn btn-default'
        checkable: true
        //scale: parent.scale
        width: parent.cellWidth
        height: parent.cellHeight
        text: "乙"
        toolTip: "乙女向き"
      }
    }
  }
}

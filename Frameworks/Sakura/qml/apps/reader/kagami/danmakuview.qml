/** danmaku.qml
 *  9/29/2012 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/util.min.js' as Util
import '../../../js/sakurakit.min.js' as Sk
import '../../../imports/qmleffects' as Effects
import '../../../js/local.js' as Local // Local.comet
import '.' as Kagami
//import '../share' as Share

Item { id: root_
  implicitWidth: 500; implicitHeight: 400
  property color effectColor: '#2d5f5f'
  //property real velocity: 0.08
  property real zoomFactor: 1.0

  property bool convertsChinese
  property bool ignoresFocus

  property int userId
  property bool readOnly

  // - Private -

  Component.onCompleted: Local.lanes = [] // [bool free]

  property bool canVote: !readOnly && !!userId && userId != 4

  //clip: true

  //property variant freeway: [] // [bool free] Deficiency in QML
  //property QtObject lanes: ListModel {} // [int:bool free]
  property int _LANE_HEIGHT: 30

  function likeComment(c, t) { // Comment, bool ->
    if (canVote && userId != c.userId) {
      if (t) {
        c.likeCount += 1
        datamanPlugin_.likeComment(c, 1)
      } else {
        c.likeCount -= 1
        datamanPlugin_.likeComment(c, 0)
      }
    }
  }

  function dislikeComment(c, t) { // Comment, bool ->
    if (canVote && userId != c.userId) {
      if (t) {
        c.dislikeCount += 1
        datamanPlugin_.likeComment(c, -1)
      } else {
        c.dislikeCount -= 1
        datamanPlugin_.likeComment(c, 0)
      }
    }
  }

  //Plugin.SubtitleEditorManagerProxy { id: subeditPlugin_ }

  //Plugin.BBCodeParser { id: bbcodePlugin_ }
  function renderComment(c) {
    var t = c.text
    if (convertsChinese && c.language === 'zhs')
      t = bean_.convertChinese(t)
    return ~t.indexOf('[') ? bbcodePlugin_.parse(t) :
           ~t.indexOf("\n") ? t.replace(/\n/g, '<br/>') :
           t
    //return bbcodePlugin_.parse(t)
  }

  //Component.onCompleted: console.log("danmakuview.qml: pass")
  Repeater { id: repeater_
    anchors.fill: parent
    model: ListModel { id: model_ }

    delegate: Item { id: danmaku_
      width: text_.width + voteCol_.width + 5 // 5 = text_.rightMargin
      height: text_.height

      //x: 0
      x: root_.width - width // align right
      y: _LANE_HEIGHT * model.lane
      property real currentX

      property alias likeChecked: likeCounter_.checked
      property alias likeEnabled: likeCounter_.enabled
      property alias dislikeChecked: dislikeCounter_.checked
      property alias dislikeEnabled: dislikeCounter_.enabled

      function toggleLike() { likeCounter_.click() }
      function toggleDislike() { dislikeCounter_.click() }

      Component.onCompleted: {
        model.comment.deletedChanged.connect(remove)
        start()
      }

      Component.onDestruction:
        model.comment.deletedChanged.disconnect(remove)

      //states: State { name: '*'
      //  PropertyChanges { target: danmaku_; x: root_.width }
      //}

      function remove() {
        //root_.lanes.get(model.lane).free = true
        Local.lanes[model.lane] = true
        model_.remove(model.index)
      }

      SequentialAnimation { id: runningAni_
        NumberAnimation {
          target: danmaku_; property: 'opacity'
          from: 0; to: 1; duration: 800
        }
        PauseAnimation {
          duration: 10000 // 10 seconds
        }
        NumberAnimation {
          target: danmaku_; property: 'opacity'
          from: 1; to: 0; duration: 600
        }
        ScriptAction { script: danmaku_.remove() }
      }

      function pause() {
        if (runningAni_.running && !runningAni_.paused)
          runningAni_.pause()
      }
      function resume() {
        if (runningAni_.paused)
          runningAni_.resume()
      }
      function stop() {
        if (runningAni_.running)
          runningAni_.stop()
      }
      function start() {
        if (!runningAni_.running) {
          currentX = x
          runningAni_.start()
        }
      }


      Text { id: text_
        anchors {
          right: voteCol_.left
          rightMargin: 5
        }
        text: root_.renderComment(model.comment)
        font.pixelSize: 20 * root_.zoomFactor
        color: 'snow'

        effect: Effects.Glow {
          color: highlight ? 'red' : (model.comment.color || root_.effectColor)
          property bool highlight: toolTip_.containsMouse || runningAni_.paused

          //enabled2: root_.outlineEnabled
          //blurRadius2: 4
          //blurIntensity2: 2
          //offset2: '0,0'   // default
          //color2: 'black'  // default

          offset: '1,1'
          //blurRadius: 8
          blurRadius: 30
          blurIntensity: highlight ? 2 : 4
          //enabled: !!text_.text
        }

        wrapMode: Text.NoWrap
        textFormat: Text.RichText
        font.family: Util.fontFamilyForLanguage(model.comment.language)
        font.bold: true
        //font.italic: Util.isLatinLanguage(model.comment.language)

        //function renderText(t) {
        //  return '<span style="background-color:rgba(0,0,0,10)">' + t + '</span>'
        //}
      }

      Column { id: voteCol_
        anchors {
          verticalCenter: text_.verticalCenter
          right: parent.right
        }

        Kagami.Counter { id: likeCounter_
          enabled: root_.canVote && !!model.comment && root_.userId != model.comment.userId
          count: (model.comment ? model.comment.likeCount : 0)
          prefix: "+"
          zoomFactor: root_.zoomFactor //* 0.8 // smaller
          toolTip: Sk.tr("Like")
          hoverEnabled: true
          effectColor: containsMouse ? 'red' : 'green' //checked ? 'green' : (model.comment.color || root_.effectColor)
          onClicked: if (enabled) {
            if (dislikeCounter_.checked) {
              dislikeCounter_.checked = false
              model.comment.dislikeCount -= 1
            }
            root_.likeComment(model.comment, checked)
          }
        }

        Kagami.Counter { id: dislikeCounter_
          enabled: root_.canVote && !!model.comment && root_.userId != model.comment.userId
          count: (model.comment ? model.comment.dislikeCount : 0)
          prefix: "-"
          zoomFactor: root_.zoomFactor //* 0.8 // smaller
          toolTip: Sk.tr("Dislike")
          hoverEnabled: true
          effectColor: containsMouse ? 'red' : 'magenta' //checked ? 'purple' : (model.comment.color || root_.effectColor)
          onClicked: if (enabled) {
            if (likeCounter_.checked) {
              likeCounter_.checked = false
              model.comment.likeCount -= 1
            }
            root_.dislikeComment(model.comment, checked)
          }
        }
      }

      MouseArea { //id: mouse_
        anchors.fill: text_
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        drag.target: danmaku_; drag.axis: Drag.XandYAxis
        onDoubleClicked: danmaku_.resume()
        onClicked: {
          danmaku_.pause()
          if (mouse.button === Qt.RightButton && !root_.ignoresFocus) {
            var gp = mapToItem(null, x + mouse.x, y + mouse.y)
            menu_.popup(model, gp.x, gp.y)
          }
        }
      }

      Desktop.TooltipArea { id: toolTip_
        anchors.fill: text_
        text: commentSummary(model.comment)
      }
    }
  }

  function commentSummary(c) {
    var us = '@' + c.userName
    var lang = c.language
    lang = "(" + lang + ")"
    var sec = c.updateTimestamp > 0 ? c.updateTimestamp : c.timestamp
    var ts = Util.timestampToString(sec)
    return us + lang + ' ' + ts
  }

  Plugin.OmajinaiBean { id: bean_
    Component.onCompleted: {
      bean_.showComment.connect(root_.show)
      bean_.clear.connect(root_.clear)
    }
  }

  Desktop.Menu { id: menu_
    //Desktop.MenuItem {
    //  text: Sk.tr("Pause") + " (" + Sk.tr("Click") + ")"
    //  onTriggered: menu_.getItem().pause()
    //}
    Desktop.MenuItem {
      text: Sk.tr("Resume") + " (" + Sk.tr("Double-click") + ")"
      onTriggered: menu_.getItem().resume()
    }
    Desktop.MenuItem {
      text: Sk.tr("Edit")
      onTriggered: mainPlugin_.showSubtitleEditor(menu_.getComment())
    }
    Desktop.Separator {}
    Desktop.MenuItem {
      text: Sk.tr("Remove")
      onTriggered: menu_.getItem().remove()
    }
    Desktop.Separator {}
    Desktop.MenuItem { id: likeAct_
      checkable: true
      text: Sk.tr("Like")
      onTriggered: {
        var item = menu_.getItem()
        if (item)
          item.toggleLike()
      }
    }
    Desktop.MenuItem { id: dislikeAct_
      checkable: true
      text: Sk.tr("Dislike")
      onTriggered: {
        var item = menu_.getItem()
        if (item)
          item.toggleDislike()
      }
    }

    property variant modelData
    function getItem() { return repeater_.itemAt(modelData.index) }
    function getComment() { return modelData.comment }

    function popup(data, x, y) {
      modelData = data

      var item = getItem()
      likeAct_.checked = !!item && item.likeChecked
      dislikeAct_.checked = !!item && item.dislikeChecked
      likeAct_.enabled = !!item && item.likeEnabled
      dislikeAct_.enabled = !!item && item.dislikeEnabled

      showPopup(x, y)
    }
  }


  // - Actions -

  function getLane() { // return int lane
    var lanes = Local.lanes
    for (var i in lanes)
      if (lanes[i]) {
        lanes[i] = false
        return i
      }
    lanes.push(false)
    return lanes.length - 1
  }

  function show(comment) {
    if (visible)
      model_.append({comment:comment, lane:getLane()})
  }

  function clear() {
    //listModel_.clear()
    console.log("danmakuview.qml:clear: pass")
  }
}

/** commentview.qml
 *  12/2/2012 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/eval.min.js' as Eval
import '../../../js/util.min.js' as Util
import '../../../imports/texscript' as TexScript
import '../../../components' as Components
import '../share' as Share
import '.' as Kagami

Item { id: root_
  property bool ignoresFocus: false
  //property bool subtitleVisible: true
  property bool commentVisible: true

  property color effectColor
  //property bool avatarVisible

  property bool convertsChinese

  property real zoomFactor: 1.0

  property int userId
  property bool readOnly

  // - Private -

  property bool canVote: !readOnly && !!userId && userId != 4

  property int _BBCODE_TIMESTAMP: 1363922891

  visible: commentVisible && listModel_.count > 0

  property int _VISIBLE_DURATION: 12000
  property int _FADE_DURATION: 800

  TexScript.TexHtmlParser { id: tex_
    settings: TexScript.TexHtmlSettings {
      tinySize: "10px"
      smallSize: "14px"
      normalSize: "16px" // the same as textEdit_.font.pixelSize
      largeSize: "28px"
      hugeSize: "40px"

      hrefStyle: "color:snow"
      urlStyle: hrefStyle
    }
  }

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

  //Plugin.DataManagerProxy { id: datamanPlugin_ }
  //Plugin.ClipboardProxy { id: clipboardPlugin_ }
  //Plugin.SubtitleEditorManagerProxy { id: subeditPlugin_ }
  //Plugin.UserViewManagerProxy { id: userViewPlugin_ }

  //Plugin.BBCodeParser { id: bbcode_ }
  function renderComment(c) {
    var t = c.text
    if (convertsChinese && c.language === 'zhs')
      t = bean_.convertChinese(t)

    if (c.timestamp > _BBCODE_TIMESTAMP)
      return ~t.indexOf('[') ? bbcodePlugin_.parse(t) :
             ~t.indexOf("\n") ? t.replace(/\n/g, '<br/>') :
             t
      //return bbcodePlugin_.parse(t)
    else
      return ~t.indexOf("\\") ? tex_.toHtml(t) : t
  }

  //visible: !!listModel_.count

  ListView { id: listView_
    anchors.fill: parent
    //width: root_.width; height: root_.height
    clip: true
    boundsBehavior: Flickable.DragOverBounds // no overshoot bounds
    snapMode: ListView.SnapToItem   // move to bounds

    //contentWidth: width
    //contentHeight: 2000

    //effect: Effects.TextShadow {
    //  blurRadius: 1
    //  offset: Qt.point(1, 1)
    //  color: '#2d5f5f' // dark green
    //}

    model: ListModel { id: listModel_ }

    //highlight: Rectangle { color: 'black'; radius: 5; opacity: 0.2 }
    //highlightFollowsCurrentItem: true

    // See: http://doc.qt.digia.com/4.7-snapshot/qml-textedit.html#selectWord-method
    //function ensureVisible(r) {
    //  if (contentX >= r.x)
    //    contentX = r.x
    //  else if (contentX+width <= r.x+r.width)
    //    contentX = r.x+r.width-width
    //  if (contentY >= r.y)
    //    contentY = r.y
    //  else if (contentY+height <= r.y+r.height)
    //    contentY = r.y+r.height-height
    //}

    // Behavior on x { SpringAnimation { spring: 3; damping: 0.3; mass: 1.0 } }
    // Behavior on y { SpringAnimation { spring: 3; damping: 0.3; mass: 1.0 } }

    //MouseArea {
    //  acceptedButtons: Qt.LeftButton
    //  anchors.fill: parent
    //  drag.target: parent; drag.axis: Drag.XandYAxis
    //  onPressed: { /*parent.color = 'red';*/ /*parent.styleColor = 'orange';*/ }
    //  onReleased: { /*parent.color = 'snow';*/ /*parent.styleColor = 'red';*/ }
    //}

    states: State {
      when: listView_.movingVertically || listView_.movingHorizontally
      PropertyChanges { target: verticalScrollBar_; opacity: 1 }
      //PropertyChanges { target: horizontalScrollBar_; opacity: 1 }
    }

    transitions: Transition {
      NumberAnimation { property: 'opacity'; duration: 400 }
    }

    header: Item {
      width: listView_.width; height: listView_.height/4

      Rectangle { id: header_
        anchors {
          left: parent.left; right: parent.right
          top: parent.bottom
        }
        height: listView_.childrenRect.height
        color: '#55000000'
        z: -1
        //radius: 15
        radius: 0 // flat

      }
      Share.CloseButton {
        anchors { left: header_.left; top: header_.top; margins: -4 }
        onClicked: root_.hide()
        z: 999
      }
    }

    delegate: textComponent_
    //delegate: Loader {
    //  sourceComponent: model.component
    //  property QtObject modelData: model
    //}
  }

  Components.ScrollBar { id: verticalScrollBar_
    width: 12
    height: Math.max(0, listView_.height - 12)
    anchors.left: listView_.left
    anchors.verticalCenter: listView_.verticalCenter
    opacity: 0
    orientation: Qt.Vertical
    position: listView_.visibleArea.yPosition
    pageSize: listView_.visibleArea.heightRatio
  }

  //Components.ScrollBar { id: horizontalScrollBar_
  //  width: Math.max(0, listView_.width - 12)
  //  height: 12
  //  anchors.bottom: listView_.bottom
  //  anchors.horizontalCenter: listView_.horizontalCenter
  //  opacity: 0
  //  orientation: Qt.Horizontal
  //  position: listView_.visibleArea.xPosition
  //  pageSize: listView_.visibleArea.widthRatio
  //}

  Component { id: textComponent_ // list delegate
    Item { id: textItem_
      height: !visible ? 0 : 30 + textEdit_.height
      //width: !visible ? 0 : 20 + textEdit_.width + (avatar_.visible ? avatar_.width : 0)
      width: visible ? listView_.width : 0

      property color color: toolTip_.containsMouse ? 'red' : (model.comment.color || root_.effectColor)

      Component.onCompleted: {
        hideAct_.triggered.connect(textItem_.hide)
        autoHideAct_.triggered.connect(textItem_.autoHide)
        //autoHide()
        if (autoHideAct_.checked)
          visibleTimer_.start()
      }

      Component.onDestruction: {
        hideAct_.triggered.disconnect(textItem_.hide)
        autoHideAct_.triggered.disconnect(textItem_.autoHide)
      }

      Timer { id: visibleTimer_
        interval: _VISIBLE_DURATION
        onTriggered: textItem_.removeMe()
      }

      property alias likeChecked: likeCounter_.checked
      property alias likeEnabled: likeCounter_.enabled
      property alias dislikeChecked: dislikeCounter_.checked
      property alias dislikeEnabled: dislikeCounter_.enabled
      function toggleLike() { likeCounter_.click() }
      function toggleDislike() { dislikeCounter_.click() }

      function autoHide() {
        if (hideAct_.checked)
          visibleTimer_.restart()
        else
          visibleTimer_.stop()
      }

      function hide() {
        visibleTimer_.stop()
        removeMe()
      }

      function removeMe() {
        listModel_.remove(model.index)
      }

      visible: root_.commentVisible && !model.comment.disabled && !model.comment.deleted

      //opacity: 0
      NumberAnimation on opacity { // fade in
        from: 0; to: 1; duration: _FADE_DURATION
      }
      //states: State {
      //  when: textItem_.visible
      //  PropertyChanges { target: textItem_; opacity: 1 }
      //}
      //transitions: Transition {
      //  NumberAnimation { property: 'opacity'; duration: _FADE_DURATION }
      //}

      // See: http://doc.qt.digia.com/qt/qml-listview.html
      ListView.onRemove: SequentialAnimation { // fade out
        PropertyAction { target: textItem_; property: 'ListView.delayRemove'; value: true }
        NumberAnimation { target: textItem_; property: 'opacity'; to: 0; duration: _FADE_DURATION }
        PropertyAction { target: textItem_; property: 'ListView.delayRemove'; value: false }
      }

      // Shadow
      //Rectangle {
      //  color: model.color
      //  anchors.centerIn: parent
      //  z: -1
      //  width: textEdit_.paintedWidth + 20
      //  height: textEdit_.paintedHeight + 20
      //  radius: 15
      //}

      // http://qt-project.org/forums/viewthread/7037
      Rectangle { id: avatarRect_
        anchors {
          verticalCenter: parent.verticalCenter
          left: parent.left
          leftMargin: 9
        }
        //radius: 20
        width: 40 * root_.zoomFactor
        height: 40 * root_.zoomFactor
        color: 'transparent'
        border.width: 2
        border.color: textItem_.color
        //opacity: 0.9
        visible: !!avatar_.source && avatar_.status === Image.Ready

        Image { id: avatar_
          //clip: true
          anchors.fill: parent
          fillMode: Image.PreserveAspectCrop
          //fillMode: Image.Stretch
          sourceSize: Qt.size(50, 50) // small: 50x50
          //visible: status == Image.Ready

          asynchronous: !!url && url.indexOf('http://') === 0
          //asynchronous: true
          source: url
          property string url: datamanPlugin_.queryUserAvatarUrlWithHash(model.comment.userId, model.comment.userHash)
        }
      }

      Column { id: voteCol_
        anchors {
          left: avatar_.visible ? avatarRect_.right : parent.left
          verticalCenter: parent.verticalCenter
          leftMargin: 5
        }

        Kagami.Counter { id: likeCounter_
          enabled: root_.canVote && !!model.comment && root_.userId != model.comment.userId
          count: (model.comment ? model.comment.likeCount : 0)
          prefix: "+"
          zoomFactor: root_.zoomFactor
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
          zoomFactor: root_.zoomFactor
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

      TextEdit { id: textEdit_
        anchors {
          verticalCenter: parent.verticalCenter
          left: voteCol_.right
          right: parent.right
          leftMargin: 5
          rightMargin: 9
        }
        // height is the same as painted height
        //width: Math.max(0, listView_.width - 20)

        focus: true
        //smooth: true  // not used
        textFormat: TextEdit.RichText
        //readOnly: true

        onLinkActivated: Eval.evalLink(link)

        wrapMode: TextEdit.Wrap
        verticalAlignment: TextEdit.AlignVCenter
        horizontalAlignment: TextEdit.AlignLeft

        selectByMouse: true

        //effect: Effects.TextShadow {
        //  blurRadius: 1
        //  offset: Qt.point(1, 1)
        //  color: '#2d5f5f' // dark green
        //}
        effect: Share.TextEffect {
          color: textItem_.color
        }

        //onCursorRectangleChanged: listView_.ensureVisible(cursorRectangle)

        font.pixelSize: 18 * root_.zoomFactor
        font.bold: true
        color: 'snow'
        //style: Text.Raised
        //styleColor: '#aa98fb98' // pale green

        text: renderComment(model.comment)

        font.family: Util.fontFamilyForLanguage(model.comment.language)

        //onActiveFocusChanged: {
        //  console.log(activeFocus)
        //  listModel_.setProperty(model.index, 'focused', activeFocus)
        //  //visibleTimer_.restart()
        //}

        function renderComment(c) {
          var ret = root_.renderComment(c)
          var u = '@' + c.userName
          var ts = '<span style="font-size:10px"> ― ' + Util.timestampToString(c.updateTimestamp > 0 ? c.updateTimestamp : c.timestamp) + '</span>'
          ret = u + ': ' + ret + ts
          return ret
        }
      }

      //MouseArea { id: mouse_
      //  anchors.fill: parent
      //  acceptedButtons: Qt.RightButton
      //  drag.target: danmaku_; drag.axis: Drag.XandYAxis
      //  onDoubleClicked: danmaku_.resume()
      //  onClicked: {
      //    danmaku_.pause()
      //    if (mouse.button === Qt.RightButton) {
      //      var gp = mapToItem(null, x + mouse.x, y + mouse.y)
      //      menu_.popup(model, gp.x, gp.y)
      //    }
      //  }
      //}

      Desktop.TooltipArea { id: toolTip_
        anchors.fill: parent
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

  Plugin.GossipBean { id: bean_
    Component.onCompleted: {
      bean_.clear.connect(root_.clear)
      //bean_.showMessage.connect(root_.showMessage)
      bean_.showComment.connect(root_.showComment)
    }
  }

  //PropertyAnimation on opacity { id: fadeOutAni_
  //  from: 1; to: 0; duration: 1000
  //}

  //function isFocused() {
  //  for (var i = 0; i < listModel_.count; ++i)
  //    if (listModel_.get(i).focused)
  //      return true
  //  return false
  //}

  //Component.onCompleted: console.log("gossip.qml: pass")

  function addItem(comment) {
    listModel_.append({comment:comment})
    listView_.positionViewAtIndex(listModel_.count -1, ListView.Contain)
    //listView_.currentIndex = _pageIndex + 1
    //cls()
  }

  //function showMessage(text, lang) {
  //  addText(text, 'message', lang, '#55000000') // black
  //}

  function showComment(comment) {
    if (!commentVisible)
      return
    addItem(comment)
  }

  function clear() { listModel_.clear() }

  // - Context Menu -

  function hide() { hideAct_.triggered() }

  Desktop.Menu { id: menu_

    Desktop.MenuItem { //id: editAct_
      text: Sk.tr("Edit")
      onTriggered: {
        var c = getPopupComment()
        if (c)
          mainPlugin_.showSubtitleEditor(c)
      }
    }

    Desktop.MenuItem {
      text: Sk.tr("Copy")
      //shortcut: "Ctrl+A"
      onTriggered: {
        var c = getPopupComment()
        if (c)
          clipboardPlugin_.text = c.text
      }
    }

    Desktop.MenuItem {
      text: Sk.tr("User information")
      onTriggered: {
        var c = getPopupComment()
        if (c)
          mainPlugin_.showUser(c.userId)
      }
    }

    Desktop.Separator {}

    Desktop.MenuItem { id: autoHideAct_
      text: My.tr("Auto Hide")
      checkable: true
      //shortcut: "Esc"
      checked: true
    }
    Desktop.MenuItem { id: hideAct_
      text: Sk.tr("Hide")
      //shortcut: "Esc"
    }

    Desktop.Separator {}
    Desktop.MenuItem { id: likeAct_
      checkable: true
      text: Sk.tr("Like")
      onTriggered: {
        var item = getPopupItem()
        if (item)
          item.toggleLike()
      }
    }
    Desktop.MenuItem { id: dislikeAct_
      checkable: true
      text: Sk.tr("Dislike")
      onTriggered: {
        var item = getPopupItem()
        if (item)
          item.toggleDislike()
      }
    }

    function popup(x, y) {
      popupX = x; popupY = y
      //var item = listModel_.get(popupIndex())
      //editAct_.enabled = !!(item && item.comment)

      var item = getPopupItem()
      likeAct_.checked = !!item && item.likeChecked
      dislikeAct_.checked = !!item && item.dislikeChecked
      likeAct_.enabled = !!item && item.likeEnabled
      dislikeAct_.enabled = !!item && item.dislikeEnabled

      showPopup(x, y)
    }
  }

  MouseArea {
    anchors.fill: parent
    acceptedButtons: Qt.RightButton
    enabled: !root_.ignoresFocus
    onPressed: if (!root_.ignoresFocus) {
      var gp = mapToItem(null, x + mouse.x, y + mouse.y)
      //menu_.showPopup(gp.x, gp.y)
      menu_.popup(gp.x, gp.y)
    }
  }

  property int popupX
  property int popupY

  function popupIndex() {
    var pos = listView_.mapFromItem(null, popupX, popupY)
    return listView_.indexAt(listView_.contentX + pos.x, listView_.contentY + pos.y)
  }

  function getPopupItem() { return listModel_.get(popupIndex()) }
  function getPopupComment() {
    var item = getPopupItem()
    return item ? item.comment : null
  }

  function textEditAt(index) {
    if (index >= 0 && index < listModel_.count) {
      var item = listModel_.get(index)
      if (item)
        return item.textEdit
    }
    return undefined
  }
}

/** graffiti.qml
 *  10/17/2012 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
//import '../../../imports/qmlhelper' as Helper
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/util.min.js' as Util
import '../../../components' as Components
import '../../../components/bootstrap3' as Bootstrap
import '../../../components/qt5' as Qt5

Item { id: root_
  property string searchText: ""
  property variant searchRe: new RegExp(searchText, 'i')
  property bool enabled: true

  property bool copyEnabled: true
  property bool headerVisible: true
  property bool spellCheckEnabled: true

  //property bool allCommentsVisible: false

  property bool textVisible: true
  //onTextVisibleChanged: console.log("graffiti.qml: text visible =", textVisible)

  property bool translationVisible: true
  //onTranslationVisibleChanged: console.log("graffiti.qml: translation visible =", translationVisible)

  property bool subtitleVisible: true
  //onSubtitleVisibleChanged: console.log("graffiti.qml: subtitle visible =", subtitleVisible)

  property bool danmakuVisible: true

  property bool commentVisible: true
  //onCommentVisibleChanged: console.log("graffiti.qml: comment visible =", commentVisible)

  //signal lookupRequested(string text, int x, int y) // popup honyaku of text at (x, y)

  // FIXME: This is supposed to be the count of matched items
  property alias count: listModel_.count

  //property bool groupEnabled: true

  function visibleCount() {
    var ret = 0
    // http://stackoverflow.com/questions/9039497/how-to-get-an-instantiated-delegate-component-from-a-gridview-or-listview-in-qml
    for (var i = 0; i < listView_.contentItem.children.length; ++i) {
      var item = listView_.contentItem.children[i]
      if (item.objectName === 'textItem' && item.visible)
        ++ret
    }
    return ret
  }

  function scrollBeginning() {
    listView_.positionViewAtBeginning()
    //showScrollBar()
  }

  function scrollEnd() {
    listView_.positionViewAtEnd()
    //if (listView_.count)
    //  listView_.positionViewAtIndex(listView_.count-1, ListView.End)
    //showScrollBar()
  }

  //function matchedCount() {
  //  var ret = 0
  //  if (listView_.model)
  //    for (var i = listModel_.count -1; i >= 0; i -= 1)
  //      if (isMatchedModelData(listModel_.get(i)))
  //        ret += 1
  //  return ret
  //}

  // - Actions -

  //clear
  //showAllComments

  // - Private -

  clip: true

  //property int _BUTTON_WIDTH: 45
  //property int _BUTTON_HEIGHT: 20
  property int _BUTTON_PIXEL_SIZE: 10

  Plugin.SystemStatus { id: status_ }
  property int userId: status_.online ? status_.userId : 0
  property int userLevel: status_.userCommentLevel // use int instead of alias to cache the result

  property int _SUPER_USER_ID: 2
  property int _GUEST_USER_ID: 4

  function typeName(type) {
    switch (type) {
    case 'danmaku': return Sk.tr("danmaku")
    case 'comment': return Sk.tr("comment")
    case 'subtitle': return Sk.tr("subtitle")
    case 'popup': return My.tr("note")

    case 'tr': return Sk.tr("translation")
    case 'text': return Sk.tr("text")
    default: return type
    }
  }

  //radius: 10

  //Image {
  //  anchors.fill: parent
  //  fillMode: Image.Tile
  //  source: 'image://rc/texture-black'
  //  //z: -1
  //}

  //gradient: Gradient {
  //  //GradientStop { position: 0.0;  color: '#8c8f8c' }
  //  //GradientStop { position: 0.17; color: '#6a6d6a' }
  //  //GradientStop { position: 0.77; color: '#3f3f3f' }
  //  //GradientStop { position: 1.0;  color: '#6a6d6a' }
  //  GradientStop { position: 0.0;  color: '#c8c9d0' }
  //  GradientStop { position: 0.17; color: '#dfdfe3' }
  //  GradientStop { position: 0.77; color: '#f1f1f3' }
  //  GradientStop { position: 1.0;  color: '#f0f0f3' }
  //}

  ListView { id: listView_
    anchors.fill: parent
    anchors.margins: 10
    width: root_.width; height: root_.height
    //clip: true // in order to enable zebra
    boundsBehavior: Flickable.DragOverBounds // no overshoot bounds

    // Do not snap to the first item
    //snapMode: ListView.SnapToItem

    spacing: 0

    //contentWidth: width
    //contentHeight: 2000

    //effect: Effects.DropShadow {
    //  blurRadius: 1
    //  offset: Qt.point(1, 1)
    //  color: 'magenta'
    //}

    //highlight: Rectangle {
    //  width: listView_.width
    //  color: 'black'; radius: 5; opacity: 0.2
    //}
    highlightFollowsCurrentItem: true

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

    //Behavior on x { SpringAnimation { spring: 3; damping: 0.3; mass: 1.0 } }
    //Behavior on y { SpringAnimation { spring: 3; damping: 0.3; mass: 1.0 } }

    //MouseArea {
    //  anchors.fill: parent
    //  drag.target: parent; drag.axis: Drag.XandYAxis
    //  onPressed: { /*parent.color = 'red';*/ /*parent.styleColor = 'orange';*/ }
    //  onReleased: { /*parent.color = 'snow';*/ /*parent.styleColor = 'red';*/ }
    //}

    states: State {
      when: listView_.movingVertically //|| listView_.movingHorizontally
      PropertyChanges { target: verticalScrollBar_; opacity: 1 }
      //PropertyChanges { target: horizontalScrollBar_; opacity: 1 }
    }

    transitions: Transition {
      NumberAnimation { property: 'opacity'; duration: 400 }
    }

    delegate: textComponent_

    footer: Item {
      width: listView_.width
      height: Math.max(0, listView_.height - 10 - 50) // margin: 10, last text item: 40
    }

    model: ListModel { id: listModel_ }
    //Component.onCompleted: root_.connectModel()
  }

  // FIXME: switch to native scrollbar
  //Desktop.ScrollBar {
  //  //width: 12
  //  height: Math.max(0, listView_.height - 12)
  //  anchors.right: listView_.right
  //  anchors.verticalCenter: listView_.verticalCenter
  //  //opacity: 0
  //  opacity: 1
  //  orientation: Qt.Vertical
  //  value: listView_.visibleArea.yPosition
  //  maximumValue: listView_.contentHeight
  //  //pageStep: listView_.visibleArea.heightRatio
  //}

  Components.ScrollBar { id: verticalScrollBar_
    width: 12
    height: Math.max(0, listView_.height - 12)
    anchors.right: listView_.right
    anchors.verticalCenter: listView_.verticalCenter
    opacity: 0
    //opacity: 1
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

  //function showScrollBar() {
  //  verticalScrollBar_.opacity = 1
  //}

  //WorkerScript { id: script_
  //  source: 'graffiti.min.js'
  //  onMessage: {
  //    toggleListModel()
  //    console.log("graffiti.qml:onMessage: pass")
  //  }
  //}

  Component { id: textComponent_
    Item { id: textItem_
      objectName: 'textItem' // See: http://stackoverflow.com/questions/9039497/how-to-get-an-instantiated-delegate-component-from-a-gridview-or-listview-in-qml

      //width: visible ? textEdit_.width + 40 : 0
      height: visible ? textEdit_.height + headerText_.height + 15 : 0

      property bool hasComment: !!model.comment && !model.comment.deleted

      property bool ownComment: hasComment && (
          root_.userId === comment.userId && !comment.protected
          || comment.userId === _GUEST_USER_ID && root_.userLevel > 0)
      property bool canEdit: !!root_.userId && ownComment
      property bool canDisable: canEdit ||
          hasComment && !!root_.userId && !model.comment.locked && root_.userId !== 'guest'

      visible: {
        if (!root_.enabled)
          return false
        if (!root_.visible)
          return false
        if (model.comment && model.comment.deleted)
          return false
        var ret
        switch (model.type) {
          case 'text': ret = root_.textVisible; break
          case 'tr': ret = root_.translationVisible; break
          case 'subtitle': ret = root_.subtitleVisible; break
          case 'danmaku': ret = root_.danmakuVisible; break
          case 'comment': ret = hasComment && root_.commentVisible; break
          //case 'prompt': return !root_.searchText // hide when search text is not empty
          default: ret = true   // should be unreachable
        }
        if (ret && root_.searchText && model.text) { // search text is not empty
          ret = root_.searchRe.test(model.text)
          //ret = containsRe(model.text, root_.searchText)
          if (!ret && headerText_.text)
            ret = root_.searchRe.test(headerText_.text)
            //ret = containsRe(headerText_.text, root_.searchText)
        }
        return ret
      }

      //function containsRe(src, pattern) {
      //  return (new RegExp(pattern, 'i')).test(src)
      //}

      property bool highlight: hover || root_.headerVisible || !!root_.searchText
      property bool hover: toolTip_.containsMouse ||
                           headerToolTip_.containsMouse ||
                           noteToolTip_.containsMouse ||
                           lockButton_.hover ||
                           editButton_.hover ||
                           improveButton_.hover ||
                           disableButton_.hover ||
                           deleteButton_.hover ||
                           createSubtitleButton_.hover ||
                           createCommentButton_.hover

      //Component.onCompleted: fadeInAni_.start()

      //NumberAnimation on opacity { id: fadeInAni_
      //  from: 0; to: 1; duration: 800
      //}

      // Shadow
      //Rectangle {
      //  color: model.color
      //  anchors {
      //    verticalCenter: textEdit_.verticalCenter
      //    left: textEdit_.left
      //    //left: model.align === Qt.AlignLeft ? textEdit_.left : undefined
      //    //right: model.align === Qt.AlignRight ? textEdit_.right : undefined
      //    //horizontalCenter: model.align === Qt.AlignHCenter ? textEdit_.horizontalCenter : undefined
      //    margins: -10
      //  }
      //  z: -1
      //  width: textEdit_.paintedWidth + 20
      //  height: textEdit_.paintedHeight + 10
      //  radius: 15
      //}

      // Shadow
      Rectangle {
        anchors {
          top: parent.top
          left: parent.left
          leftMargin: -10 // listView_ left margin
          topMargin: 6
          //topMargin: -listView_.spacing
        }
        radius: 9
        width: listView_.width
        height: parent.height + listView_.spacing
        z: -1
        visible: !!(model.group % 2)
        color: '#77fefefe'
      }

      //MouseArea { id: hover_
      //  anchors {
      //    left: parent.left
      //    right: parent.right
      //    top: parent.top
      //    bottom: parent.bottom
      //    topMargin: -20
      //    //bottomMargin: -5
      //  }
      //  hoverEnabled: true
      //  acceptedButtons: Qt.NoButton
      //}

      Qt5.TextEdit5 { id: textEdit_
        anchors.bottom: parent.bottom
        // height is the same as painted height
        width: Math.max(0, listView_.width - 20)

        selectByMouse: true

        onLinkActivated: Qt.openUrlExternally(link)

        onSelectedTextChanged:
          if (root_.copyEnabled && selectedText)
            copy()

        //Component.onCompleted:
        //  listModel_.setProperty(model.index, 'textEdit', textEdit_)

        MouseArea { // context menu
          anchors.fill: parent
          //hoverEnabled: true
          acceptedButtons: Qt.RightButton
          onPressed: {
            var gp = mapToItem(null, x + mouse.x, y + mouse.y)
            menu_.popup(gp.x, gp.y, model, textEdit_)
          }
        }

        // 4/10/2015: Temporarily disabled
        //Plugin.MeCabHighlighter {
        //  document: textEdit_.getTextDocument()
        //  enabled: textItem_.visible
        //        && textItem_.hover
        //        && model.type === 'text' && model.language === 'ja'
        //}

        Plugin.SpellChecker {
          document: textEdit_.getTextDocument()
          language: model.language
          enabled: textItem_.visible
                && textItem_.hasComment
                && root_.spellCheckEnabled
                && Util.spellSupportsLanguage(model.language)
        }

        Desktop.TooltipArea { id: toolTip_
          anchors.fill: parent
          text: (textItem_.canEdit ? Sk.tr("Editable") : Sk.tr("Read-only"))
                + " " + root_.typeName(model.type)
        }

        //MouseArea { id: textCursor_
        //  anchors.fill: parent
        //  acceptedButtons: Qt.NoButton
        //  hoverEnabled: true
        //  property string lastSelectedText
        //  onPositionChanged: {
        //     // Current EDICT dictionary support only ja and en
        //    if (model.language === 'ja') {
        //      textEdit_.cursorPosition = textEdit_.positionAt(mouse.x, mouse.y)
        //      textEdit_.selectWord()
        //      var t = textEdit_.selectedText
        //      if (t && t !== lastSelectedText) {
        //        lastSelectedText = t
        //        var gp = Util.itemGlobalPos(parent)
        //        root_.lookupRequested(t, mouse.x + gp.x, mouse.y + gp.y)
        //      }
        //    }
        //  }

        //  onClicked: {
        //    var gp = Util.itemGlobalPos(parent)
        //    menu_.showPopup(mouse.x + gp.x, mouse.y + gp.y)
        //  }
        //}

        focus: true
        //smooth: true  // not used
        //textFormat: needsRichText() ? TextEdit.RichText : TextEdit.PlainText
        textFormat: TextEdit.PlainText
        //text: model.text ? renderText(model.text) : ""
        onTextChanged:
          if (text && textItem_.hasComment)
            root_.updateCommentText(model.comment, Util.trim(text))

        readOnly: !textItem_.canEdit

        wrapMode: TextEdit.Wrap
        font.strikeout: textItem_.hasComment && model.comment.disabled

        verticalAlignment: TextEdit.AlignVCenter
        horizontalAlignment: TextEdit.AlignLeft

        //selectByMouse: true

        font.family: Util.fontFamilyForLanguage(model.language)

        //onCursorRectangleChanged: listView_.ensureVisible(cursorRectangle)

        font.pixelSize: 14
        //font.bold: true
        //font.italic: Util.isLatinLanguage(model.language)
        font.italic: textItem_.hasComment && model.comment.type === 'comment'
        color: 'black'

        //function isEmpty() { return !model.text }

        //function needsTranslate() { // always disabled
        //  return model.type === 'text' && model.language === 'ja' && textCursor_.containsMouse
        //}

        //function needsRichText() { return false }

        Component.onCompleted: // decouple property binding
          if (model.comment && !model.comment.deleted)
            text = model.comment.text
          else if (model.text)
            text = model.text
      }

      Text { id: headerText_
        anchors {
          left: parent.left; top: parent.top
          leftMargin: 5; topMargin: 10
        }
        textFormat: Text.RichText
        color: textItem_.highlight ? 'blue' : 'silver'
        font.pixelSize: 12
        text: textItem_.hasComment ? commentSummary() :
              model.type === 'text' ? textSummary() :
              model.type === 'tr' ? translationSummary() :
              ''
        //font.italic: !model.comment
        //font.bold: true
        //font: textEdit_.font
        //visible: !!model.comment

        Desktop.TooltipArea { id: headerToolTip_
          anchors.fill: parent
          text: model.type === 'text' ? My.tr("Game text") :
                model.type === 'tr' ? My.tr("Machine translation") :
                model.type === 'subtitle' ? qsTr("Creation user and time") :
                model.type === 'danmaku' ? qsTr("Creation user and time") :
                model.type === 'comment' ? qsTr("Creation user and time") :
                My.tr("Text") // unreachable
        }

        function translationSummary() {
          var tr = My.tr(Util.translatorName(model.provider))
          var lang = Sk.tr(Util.languageShortName(model.language))
          return tr + " (" + lang + ")"
        }

        function textSummary() {
          var ctx = "ctx=" + model.contextSize
          return My.tr("Game text") + "(" + ctx + ")"
        }

        function commentSummary() {
          var us = '@' + model.comment.userName
          if (textItem_.highlight && textItem_.ownComment)
            us = '<span style="color:darkblue;font-weight:bold">' + us + "</span>"
          else
            us = '<span style="font-weight:bold">' + us + "</span>"
          var lang = model.comment.language
          var type = typeName(model.comment.type)
          var ctx = "ctx=" + model.comment.contextSize
          var ts = Util.timestampToString(model.comment.timestamp)
          return us + "(" + lang + "," + type + "," + ctx + ") " + ts
        }
      }

      // For game text
      Row {
        anchors {
          left: headerText_.right; verticalCenter: headerText_.verticalCenter
          leftMargin: 9
        }
        spacing: 3
        visible: model.type === 'text'

        //property color hoverColor: '#99ff33cc' // magenta
        //property color hoverColor: '#996a6d6a' // black

        Bootstrap.Button { id: createSubtitleButton_
          styleClass: 'btn btn-default'
          //width: _BUTTON_WIDTH; height: _BUTTON_HEIGHT
          font.pixelSize: _BUTTON_PIXEL_SIZE
          //font.bold: true
          //color: textItem_.highlight ? 'blue' : 'silver'
          enabled: !!root_.userId
          //backgroundColor: hover && enabled ? parent.hoverColor : 'transparent'
          visible: enabled

          text: Sk.tr("subtitle")
          onClicked: root_.createComment('subtitle', model.contextHash, model.contextSize, model.index)
          toolTip: qsTr("Create a new {0}").replace('{0}', Sk.tr("subtitle"))
        }

        Bootstrap.Button { id: createCommentButton_
          styleClass: 'btn btn-default'
          //width: _BUTTON_WIDTH; height: _BUTTON_HEIGHT
          font.pixelSize: _BUTTON_PIXEL_SIZE
          //font.bold: true
          //color: textItem_.highlight ? 'blue' : 'silver'
          enabled: !!root_.userId
          //backgroundColor: hover && enabled ? parent.hoverColor : 'transparent'
          visible: enabled

          text: Sk.tr("comment")
          onClicked: root_.createComment('comment', model.contextHash, model.contextSize, model.index)
          toolTip: qsTr("Create a new {0}").replace('{0}', Sk.tr("comment"))
        }
      }

      // For user comment
      Row {
        anchors {
          left: headerText_.right; verticalCenter: headerText_.verticalCenter
          leftMargin: 9
        }
        spacing: 3
        visible: textItem_.hasComment

        //property color hoverColor: '#99ff33cc' // magenta
        //property color hoverColor: '#996a6d6a' // black

        Bootstrap.Button { id: editButton_
          styleClass: 'btn btn-default'
          //width: _BUTTON_WIDTH; height: _BUTTON_HEIGHT
          font.pixelSize: _BUTTON_PIXEL_SIZE
          //font.bold: true
          //color: textItem_.highlight ? 'blue' : 'silver'
          //property bool enabled: textItem_.canDisable
          //backgroundColor: hover ? parent.hoverColor : 'transparent'
          visible: textItem_.hasComment

          text: Sk.tr("edit")
          onClicked: mainPlugin_.showSubtitleEditor(model.comment)
          toolTip: qsTr("Edit properties of the subtitle")
        }

        Bootstrap.Button { id: improveButton_
          styleClass: 'btn btn-default'
          //width: _BUTTON_WIDTH; height: _BUTTON_HEIGHT
          font.pixelSize: _BUTTON_PIXEL_SIZE
          //font.bold: true
          //color: textItem_.highlight ? 'blue' : 'silver'
          enabled: textItem_.canDisable
          //backgroundColor: hover && enabled ? parent.hoverColor : 'transparent'
          visible: enabled

          text: Sk.tr("improve")
          onClicked: root_.improveComment(model.comment, model.index)
          toolTip: qsTr("Improve the subtitle")
        }

        Bootstrap.Button { id: disableButton_
          styleClass: (textItem_.hasComment && model.comment.disabled) ? 'btn btn-info' : 'btn btn-default'
          //width: _BUTTON_WIDTH; height: _BUTTON_HEIGHT
          font.pixelSize: _BUTTON_PIXEL_SIZE
          //font.bold: true
          //color: textItem_.highlight ? 'blue' : 'silver'
          enabled: textItem_.canDisable || root_.userId === _SUPER_USER_ID
          //backgroundColor: hover && enabled ? parent.hoverColor : 'transparent'
          visible: enabled

          text: !textItem_.hasComment ? "" :
                enabled ? (
                  model.comment.disabled ? Sk.tr("enable") : Sk.tr("disable")
                ) : (
                  model.comment.disabled ? Sk.tr("disabled") : Sk.tr("enabled")
                )
          onClicked: root_.toggleCommentDisabled(model.comment)
          toolTip: qsTr("Enable or disable the subtitle")
        }

        Bootstrap.Button { id: deleteButton_
          styleClass: 'btn btn-danger'
          //width: _BUTTON_WIDTH; height: _BUTTON_HEIGHT
          font.pixelSize: _BUTTON_PIXEL_SIZE
          //font.bold: true
          //color: textItem_.highlight ? 'red' : 'silver'
          enabled: textItem_.canEdit
          //backgroundColor: hover && enabled ? parent.hoverColor : 'transparent'
          visible: enabled && model.comment.disabled

          text: Sk.tr("del")
          onClicked: root_.deleteComment(model.comment)
          toolTip: qsTr("Delete the subtitle")
        }

        Bootstrap.Button { id: lockButton_
          styleClass: (textItem_.hasComment && model.comment.locked) ? 'btn btn-success' : 'btn btn-default'
          //width: _BUTTON_WIDTH; height: _BUTTON_HEIGHT
          font.pixelSize: _BUTTON_PIXEL_SIZE
          //font.bold: true
          //color: !textItem_.highlight ? 'silver' :
          //       (textItem_.hasComment && model.comment.locked) ? 'green' :
          //       'blue'
          enabled: textItem_.canEdit && root_.userId !== _GUEST_USER_ID
          //backgroundColor: hover && enabled ? parent.hoverColor : 'transparent'

          text: !textItem_.hasComment ? "" :
                enabled ? (
                  model.comment.locked ? Sk.tr("unlock") : Sk.tr("lock")
                ) : (
                  model.comment.locked ? Sk.tr("locked") : Sk.tr("unlocked")
                )

          visible: enabled ||
              textItem_.hasComment && model.comment.locked

          onClicked: root_.toggleCommentLocked(model.comment)
          toolTip: qsTr("Lock the subtitle to prevent others from overriding it")
        }
      }

      Text { id: noteText_
        anchors {
          right: textEdit_.right; top: parent.top
          rightMargin: 5; topMargin: 10
        }
        textFormat: Text.RichText
        color: textItem_.highlight ? 'green' : 'silver'
        font.pixelSize: 12

        visible: textItem_.hasComment && model.comment.updateTimestamp > 0
        text: visible ? updateSummary() : ""

        function updateSummary() {
          var user = model.comment.updateUserName
          var us = '@' + user
          if (textItem_.highlight && model.comment.updateUserId === root_.userId)
            us = "<span style='color:darkgreen;font-weight:bold'>" + us + "</span>"
          else
            us = "<span style='font-weight:bold'>" + us + "</span>"
          var ts = Util.timestampToString(model.comment.updateTimestamp)
          return  "M " + us + " " + ts
        }

        Desktop.TooltipArea { id: noteToolTip_
          anchors.fill: parent
          text: qsTr("Modification user and time")
        }
      }

    }
  }

  //function isModelConnected() {
  //  return !!listView_.model
  //}

  //function connectModel() {
  //  listView_.model = listModel_
  //}
  //function disconnectModel() {
  //  listView_.model = undefined
  //}

  Plugin.Growl { id: growl_ }

  Plugin.DataManagerProxy { id: dataman_ }

  Plugin.GraffitiBean { id: bean_
    Component.onCompleted: {
      bean_.clear.connect(root_.clear)
      bean_.pageBreak.connect(root_.pageBreak)
      bean_.showText.connect(root_.showText)
      bean_.showTranslation.connect(root_.showTranslation)
      bean_.showComment.connect(root_.showComment)
      //bean_.connectModel.connect(root_.connectModel)
      //bean_.disconnectModel.connect(root_.disconnectModel)
    }
  }

  Plugin.Tts { id: tts_ }

  Plugin.ShioriProxy { id: shiori_ }

  //Plugin.SubtitleEditorManagerProxy { id: subedit_ }

  //Helper.QmlHelper { id: qmlhelper_ }

  // Index of the first item on the last page
  // Assume page index is always less then list view count
  property int _pageIndex: 0

  //Component.onCompleted: connectModel()

  property int group: 0 // text group

  function createTextItem(text, lang, type, provider, ctxhash, ctxsize, comment) {
    if (type === 'text')
      group += 1
    return {
      comment: comment,
      contextHash: ctxhash,
      contextSize: ctxsize,
      group: group,
      language: lang,
      provider: provider,
      text: text,
      type: type, // text, translation, subtitle, comment
      //textEdit: undefined, // callback
    }
  }

  function addText(text, lang, type, provider, ctxhash, ctxsize, comment, index) {
    var item = createTextItem.apply(this, arguments)
    var hasIndex = index
    if (index && index <= listModel_.count)
      listModel_.insert(index, item)
    else {
      index = listModel_.count
      listModel_.append(item)
    }

    // The inserted item is always visible
    if (index === listView_.count -1)
      listView_.positionViewAtIndex(index, ListView.Contain)
    else
      listView_.positionViewAtIndex(index +1, ListView.Visible)
    if (!hasIndex)
      listView_.currentIndex = _pageIndex
  }

  function showText(text, language, ctxhash, ctxsize) {
    addText(text, language, 'text', undefined, ctxhash, ctxsize)
  }

  function showTranslation(text, lang, provider) {
    addText(text, lang, 'tr', provider)
  }

  function showComment(c, index) {
    // FIXME: Due to int64 issue, comment hash and context sizes are ignored
    //addText(c.text, c.language, c.type, c.hashObject, c.contextSize, c, index)
    addText(c.text, c.language, c.type, undefined, 0, 0, c, index)
  }
  //c.type === 'comment' ? '#c3ffc3' : '#f0ffe4', // pale green : light blue

  //function showPrompt() {
  //  addText("...", 'en', 'prompt', '#ffa07a') // light salmon
  //}

  // Insert a page break
  function pageBreak() {
    slimList()
    //showPrompt()
    _pageIndex = listModel_.count
    //listView_.currentIndex = _pageIndex
  }

  // Limit total number of items in the list by removing extra items in the beginning
  function slimList() {
    if (listModel_.count > 100) {   // if the list size is greater than 100
      //console.log("grimoire.qml:slimList: enter: count =", listModel_.count)
      while (listModel_.count > 70) // remove the first 30 items
        listModel_.remove(0)
      if (listView_.currentIndex >= 30) // 30 = 100 - 70
        listView_.currentIndex -= 30
      //console.log("grimoire.qml:slimList: leave: count =", listModel_.count)
      console.log("graffiti.qml:slimList: pass")
    }
  }

  function clear() {
    _pageIndex = 0
    listModel_.clear()
    //allCommentsVisible = false
    console.log("graffiti.qml:clear: pass")
  }

  // - Submit Changes -

  function updateCommentText(comment, text) {
    if (!visible || !text || text === comment.text)
      return
    if (!root_.userId || comment.userId !== root_.userId) {
      console.log("graffiti.qml:updateCommentText: warning: cannot edit other's comment")
      return
    }
    //console.log("graffiti.qml:updateCommentText: text = " + text)
    comment.text = text
    comment.updateUserId = root_.userId
    comment.updateTimestamp = Util.currentUnixTime()
  }

  function toggleCommentLocked(comment) {
    if (root_.userId !== comment.userId) {
      console.log("graffiti.qml:lockComment: warning: needs ownership")
      return
    }
    comment.locked = !comment.locked
    comment.updateUserId = root_.userId
    comment.updateTimestamp = Util.currentUnixTime()
  }

  function toggleCommentDisabled(comment) {
    if (!root_.userId) {
      console.log("graffiti.qml:disableComment: warning: needs login")
      return
    }
    comment.disabled = !comment.disabled
    comment.updateUserId = root_.userId
    comment.updateTimestamp = Util.currentUnixTime()
  }

  function deleteComment(comment) {
    if (!root_.userId || comment.userId !== root_.userId) {
      console.log("graffiti.qml:updateComment: warning: cannot delete other's comment")
      return
    }
    comment.deleted = true
    comment.updateUserId = root_.userId
    comment.updateTimestamp = Util.currentUnixTime()
  }

  function createComment(type, ctxhash, ctxsize, index) {
    if (!root_.userId) {
      growl_.warn(qsTr("Please login to add comment"))
      return
    }
    if (type && ctxhash && ctxsize) {
      var text = qsTr("New {0}").replace('{0}', My.tr(type))
      var newComment = dataman_.createComment(text, type, ctxhash, ctxsize)
      if (newComment) {
        showComment(newComment, index +1)
        return
      }
    }
    growl_.warn(qsTr("Cannot create new comment here"))
  }

  function improveComment(comment, index) {
    if (!root_.userId) {
      growl_.warn(qsTr("Please login to add comment"))
      return
    }
    var newComment = dataman_.improveComment(comment)
    if (newComment)
      showComment(newComment, index +1)
    else
      growl_.warn(qsTr("Cannot improve the comment"))
  }

  //function showAllComments() {
  //  if (!allCommentsVisible) {
  //    console.log("graffiti.qml:showAllComments: enter")
  //    allCommentsVisible = bean_.showAllComments()
  //    //script_.sendMessage({'model': idleListModel()})
  //    console.log("graffiti.qml:showAllComments: leave, visible =", allCommentsVisible)
  //  }
  //}

  // - Context Menu -

  // Popup globalPos

  property int popupX
  property int popupY
  property QtObject selectedModel
  property QtObject selectedTextEdit

  function hoverText() {
    var e = selectedTextEdit
    if (!e.selectedText) {
      var pos = e.mapFromItem(null, popupX, popupY)
      e.cursorPosition = e.positionAt(pos.x, pos.y)
      e.selectWord()
    }
    return e.selectedText
  }

  Desktop.Menu { id: menu_

    //Desktop.MenuItem { id: editAct_
    //  text: qsTr("Edit Subtitle in New Window")
    //  onTriggered: {
    //    if (selectedModel && selectedModel.comment)
    //      subedit_.showComment(selectedModel.comment)
    //  }
    //}

    //Desktop.Separator {}

    Desktop.MenuItem { id: copyAct_
      text: Sk.tr("Copy")
      shortcut: "Ctrl+C"
      onTriggered: {
        if (hoverText())
          selectedTextEdit.copy()
        else if (selectedTextEdit) {
          selectedTextEdit.selectAll()
          selectedTextEdit.copy()
        }
      }
    }

    //Desktop.MenuItem {
    //  text: Sk.tr("Paste")
    //  shortcut: "Ctrl+V"
    //  onTriggered:
    //    selectedTextEdit.paste()
    //}

    //Desktop.MenuItem {
    //  text: Sk.tr("Cut")
    //  shortcut: "Ctrl+X"
    //  onTriggered: {
    //    if (selectedTextEdit.selectedText)
    //      selectedTextEdit.cut()
    //  }
    //}

    //Desktop.MenuItem {
    //  text: qsTr("Select Word")
    //  //shortcut: "Ctrl+A"
    //  onTriggered: {
    //    var e = selectedTextEdit
    //    var pos = e.mapFromItem(null, popupX, popupY)
    //    e.cursorPosition = e.positionAt(pos.x, pos.y)
    //    e.selectWord()
    //  }
    //}

    //Desktop.MenuItem {
    //  text: qsTr("Select Sentence")
    //  shortcut: "Ctrl+A"
    //  onTriggered:
    //    selectedTextEdit.selectAll()
    //}

    Desktop.MenuItem {
      text: qsTr("Read Sentence")
      //shortcut: "Ctrl+A"
      onTriggered: {
        selectedTextEdit.selectAll()
        if (selectedTextEdit.selectedText && selectedModel.language)
          tts_.speak(selectedTextEdit.selectedText, selectedModel.language)
      }
    }

    Desktop.MenuItem {
      text: qsTr("Read Selection")
      //shortcut: "Ctrl+A"
      onTriggered: {
        if (selectedModel.language) {
          var t = hoverText()
          if (t)
            tts_.speak(t, selectedModel.language)
        }
      }
    }

    Desktop.MenuItem {
      text: qsTr("Lookup Selection")
      //shortcut: "Ctrl+A"
      onTriggered: {
        var t = hoverText()
        if (t)
          shiori_.popup(t, 'ja',
            bean_.x() + popupX, bean_.y() + popupY)
      }
    }

    function popup(x, y, model, textEdit) {
      popupX = x; popupY = y
      selectedModel = model; selectedTextEdit = textEdit
      //editAct_.enabled = !!model.comment
      showPopup(x, y)
    }
  }

  //MouseArea {
  //  anchors.fill: parent
  //  acceptedButtons: Qt.RightButton
  //  onPressed: {
  //    var gp = mapToItem(null, mouse.x, mouse.y)
  //    menu_.popup(gp.x, gp.y)
  //  }
  //}
}

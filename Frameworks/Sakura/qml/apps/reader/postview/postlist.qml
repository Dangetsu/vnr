/** postlist.qml
 *  2/19/2014 jichi
 */
import QtQuick 1.1
import '../../../js/npm/bbcode.min.js' as BBCode
import '../../../js/ajax.min.js' as Ajax
import '../../../js/linkify.min.js' as Linkify
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/underscore.string.min.js' as S_
import '../../../js/util.min.js' as Util
import '../../../components' as Components
import '../share' as Share

Item { id: root_
  implicitWidth: 200; implicitHeight: 300 // default

  property alias count: listModel_.count
  property string postUrl //: Define.DOMAIN_COM + '/api/json/post/list'
  property variant postData // json object

  signal editPostRequested(string post) // passing post as json

  function refresh() {
    Ajax.postJSON(postUrl, postData, function (obj) {
      if (obj.status === 0) {
        listModel_.clear()
        if (obj.data.length)
          for (var i in obj.data)
            listModel_.append(marshal(obj.data[i]))
      }
    })
  }

  function prepend(post) { // obj
    listModel_.insert(0, marshal(post))
    listView_.positionViewAtBeginning()
  }

  function append(post) { // obj
    listModel_.append(marshal(post))
    listView_.positionViewAtEnd()
  }

  function remove(post) { // obj -> bool  if exists
    var id = post.id
    for (var i = 0; i < listModel_.count; ++i)
      if (listModel_.get(i).id === id) {
        listModel_.remove(i)
        return true
      }
    return false
  }

  // - Private -

  clip: true

  function parse(str) {
    return BBCode.parse(Linkify.parse(S_.escapeHTML(str))).replace(/<li><\/li>/g, '<li>')
  }

  function marshal(post) { // obj -> obj
    return {
      id: post.id
      , userName: post.userName
      , userAvatar: post.userAvatar
      , color: post.userColor
      , createTime: Util.timestampToString(post.createTime)
      , content: post.content
      , language: post.lang
    }
  }

  // List

  ListView { id: listView_
    anchors.fill: parent
    boundsBehavior: Flickable.DragOverBounds // no overshoot bounds

    delegate: postComponent_
    model: ListModel { id: listModel_ }

    states: State {
      when: listView_.movingVertically //|| listView_.movingHorizontally
      PropertyChanges { target: verticalScrollBar_; opacity: 1 }
      //PropertyChanges { target: horizontalScrollBar_; opacity: 1 }
    }

    transitions: Transition {
      NumberAnimation { property: 'opacity'; duration: 400 }
    }
  }

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

  // Post item

  Component { id: postComponent_
    Item { id: postItem_
      anchors {
        left: parent.left; right: parent.right
        //margins: 10
      }
      height: Math.max(avatar_.height, postHeader_.height + postText_.height) + 10

      property bool owner: statusPlugin_.userName === model.userName

      //Item { id: avatar_
      //  anchors {
      //    top: parent.top
      //    left: parent.left
      //  }
      //  width: 50; height: 50
      //}

      Share.AvatarImage { id: avatar_
        anchors { left: parent.left; top: parent.top }
        width: 40
        height: 40
        url: model.userAvatar ? 'http://media.getchute.com/media/' + model.userAvatar + '/64x64' : ''
        sourceSize: Qt.size(64, 64)
        //url: model.userAvatar ? 'http://avatars.io/' + model.userAvatar + '?size=large' : ''
      }

      Rectangle { id: postHeader_
        anchors {
          left: avatar_.right
          right: parent.right
          top: parent.top
          leftMargin: 5
        }
        height: postUser_.height + 10
        color: Qt.rgba(0,255,127,.1)

        Text { id: postUser_
          anchors {
            left: parent.left
            verticalCenter: parent.verticalCenter
          }
          // The color is the same as bootstrap 3 link hover color
          font.pixelSize: 12
          text: '<a style="color:#2a6496;text-decoration:none" href="http://sakuradite.com/user/' + model.userName + '">@' + model.userName + '</a>'
          textFormat: Text.RichText

          onLinkActivated: {
            growlPlugin_.msg(My.tr("Open in external browser"))
            Qt.openUrlExternally(link)
          }
        }

        Text { //id: editButton_
          visible: postItem_.owner
          anchors { // the same as postUser_
            verticalCenter: parent.verticalCenter
            right: postDate_.left
            rightMargin: 9
          }
          font.pixelSize: 12
          text: '<a href="#" style="color:darkgreen;text-decoration:none">' + Sk.tr("Edit") + '</a>'
          textFormat: Text.RichText

          onLinkActivated: root_.editPostRequested(JSON.stringify(model))
        }

        //Share.TextButton { id: editButton_
        //  visible: postItem_.owner
        //  anchors { // the same as postUser_
        //    left: parent.left
        //    verticalCenter: parent.verticalCenter
        //  }
        //  font.pixelSize: 10
        //  height: 20; width: 40
        //  text: Sk.tr("Edit")
        //  toolTip: Sk.tr("Edit")
        //  color: '#2a6496' // bootstrap link color
        //  radius: 4
        //  font.bold: false
        //  //radius: parent.cellRadius
        //  //backgroundColor: parent.buttonColor
        //  //visible: !root_.ignoresFocus && !slimChecked
        //  onClicked: editDialog_.showPost(model)
        //}

        Text { id: postDate_
          anchors {
            right: parent.right
            verticalCenter: parent.verticalCenter
          }
          font.pixelSize: 10
          textFormat: Text.PlainText
          text: model.createTime
          color: '#555' // text-minor:hover
        }
      }

      TextEdit { id: postText_
        anchors {
          top: postHeader_.bottom
          left: avatar_.right
          right: parent.right
          leftMargin: 5
        }
        font.pixelSize: 12
        wrapMode: TextEdit.WordWrap
        textFormat: TextEdit.RichText
        color: model.color || 'black'
        text: root_.parse(model.content)
        readOnly: true
        selectByMouse: true // Use TextEdit instead of Text because of this
        onLinkActivated: Qt.openUrlExternally(link)
      }
    }
  }
}

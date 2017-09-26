/** editdialog.qml
 *  2/23/2014 jichi
 *
 *  See:
 *  https://qt.gitorious.org/qt-components/desktop/source/c1949cead4f25f3b224f980aa507910d908e0ecf:components/Dialog.qml
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import '../../../js/ajax.min.js' as Ajax
import '../../../js/define.min.js' as Define
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/util.min.js' as Util

Desktop.Dialog { id: root_

  width: 320; height: 240

  property variant post

  property string postUrl: Define.DOMAIN_COM + '/api/json/post/update'
  //property string postUrl: 'http://192.168.1.105:8080/api/json/post/update'

  title: Sk.tr('Edit')

  function showPost(model) { // marshaled post
    post = model
    visible = true
  }

  // - Private -

  //Image {
  //  anchors.fill: parent
  //  fillMode: Image.Tile
  //  source: 'image://rc/background'
  //  z: -1
  //}

  Desktop.TextArea { id: textEdit_
    anchors.fill: parent
    //anchors.margins: 9
    //wrapMode: TextEdit.WordWrap
    //textFormat: TextEdit.PlainText
    //color: (!post ? '' : post.userColor) || 'black'
    text: !post ? '' : post.content
    //selectByMouse: true // Use TextEdit instead of Text because of this
  }

  onAccepted:
    if (textEdit_.text !== post.content) {
      var t = Util.trim(textEdit_.text)
      if (t && t !== post.content) {
        var user = statusPlugin_.userName
        var pass = statusPlugin_.userPassword
        if (user && pass && user === post.userName) // double check
          send(t, user, pass)
      }
    }

  function send(content, userName, password) { // string, string, string
    Ajax.postJSON(root_.postUrl, {
      login: userName
      , password: password
      , id: post.id
      , content: content
    }, function (obj) {
      if (obj.status)
        sendError()
    }, sendError)
  }

  function sendError() {
    growlPlugin_.warn(qsTr("I am sorry that I am failed to save the changes")
        + '<br/>' +
        qsTr("Something might be wrong with the Internet connection"))
    //if (!Util.trim(textEdit_.text) && root_.lastText)
    //  textEdit_.text = root_.lastText
  }
}

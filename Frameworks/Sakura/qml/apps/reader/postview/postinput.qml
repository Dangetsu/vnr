/** postinput.qml
 *  2/23/2014 jichi
 *
 *  See:
 *  https://qt.gitorious.org/qt-components/desktop/source/c1949cead4f25f3b224f980aa507910d908e0ecf:components/Dialog.qml
 */
import QtQuick 1.1
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/ajax.min.js' as Ajax

Item { id: root_

  property string topicKey // topicId
  property string postUrl //: Define.DOMAIN_COM + '/api/json/post/create'
  //property string postUrl: 'http://192.168.1.105:8080/api/json/post/create'

  // string json ->
  function newPost() { editor_.newPost(0, 'post') }

  // - Private -

  Plugin.PostInputManager { id: editor_
    imageEnabled: false
    Component.onCompleted: postReceived.connect(root_.submit)
  }

  function submit(postString, imageString) { // image string is ignored
    var post = JSON.parse(postString)
    var user = statusPlugin_.userName
    var pass = statusPlugin_.userPassword
    if (user && pass && post.content) {
      var req = {
        login: user
        , password: pass
        , content: post.content
        , topic: root_.topicKey
        //, type: 'post'
        //, replyId:
      }
      if (post.lang)
        req.lang = post.lang
      send(req)
    }
  }

  function send(request) { // object
    Ajax.postJSON(root_.postUrl, request, function (obj) { // on success
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

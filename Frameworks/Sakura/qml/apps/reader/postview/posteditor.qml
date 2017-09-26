/** posteditor.qml
 *  2/23/2014 jichi
 *
 *  See:
 *  https://qt.gitorious.org/qt-components/desktop/source/c1949cead4f25f3b224f980aa507910d908e0ecf:components/Dialog.qml
 */
import QtQuick 1.1
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/ajax.min.js' as Ajax

Item { id: root_

  property string postUrl //: Define.DOMAIN_COM + '/api/json/post/update'
  //property string postUrl: 'http://192.168.1.105:8080/api/json/post/update'

  // string json ->
  function editPost(post) { editor_.editPost(post) }

  // - Private -

  Plugin.PostEditorManager { id: editor_
    imageEnabled: false
    Component.onCompleted: postChanged.connect(root_.submit)
  }

  function submit(postString, imageString) { // image is temporarily ignored
    var post = JSON.parse(postString)
    var user = statusPlugin_.userName
    var pass = statusPlugin_.userPassword
    if (user && pass && user === post.userName) { // double check user
      var req = {
        login: user
        , password: pass
        , id: post.id
      }
      if (post.content)
        req.content = post.content
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

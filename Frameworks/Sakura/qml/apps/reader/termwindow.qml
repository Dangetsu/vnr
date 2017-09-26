/** termwindow.qml
 *  2/19/2014 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../js/eval.min.js' as Eval
import 'comet' as Comet
import 'share' as Share
import '.' as Main

Share.View { id: root_
  //implicitWidth: 480; implicitHeight: 360

  width: 1300; height: 500

  property string windowTitle: termView_.windowTitle
  //property int windowFlags: termView_.windowFlags
  property bool windowVisible // receive window visible

  // - Private -

  Component.onCompleted: initEvalContext()

  function initEvalContext() {
    var ctx = Eval.scriptContext
    ctx.main = mainPlugin_
    ctx.growl = growlPlugin_
    //ctx.clipboard = clipboardPlugin_
  }

  Plugin.SystemStatus { id: statusPlugin_ }
  Plugin.Growl { id: growlPlugin_ }
  Plugin.MainObjectProxy { id: mainPlugin_ }
  Plugin.DataManagerProxy { id: datamanPlugin_ }

  Comet.TermComet { id: termComet_
    active: windowVisible && statusPlugin_.online
  }

  Desktop.SplitterRow {
    anchors.fill: parent

    Main.TermView { id: termView_
      anchors {
        top: parent.top; bottom: parent.bottom
        left: parent.left
      }
      Desktop.Splitter.expanding: true
    }

    Main.PostView { id: postView_
      anchors {
        top: parent.top; bottom: parent.bottom
        right: parent.right
      }
      visible: root_.windowVisible && statusPlugin_.online
      topicKey: 'term'
      Desktop.Splitter.expanding: false
    }
  }
}

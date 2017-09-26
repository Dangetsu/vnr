/** inspector.qml
 *  2/21/2013 jichi
 */
import QtQuick 1.1
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/util.min.js' as Util
import '../share' as Share

Item { id: root_

  property QtObject currentItem // dataman.Comment

  // - Private -

  property string _CONTEXT_SEP: "||"

  height: Math.max(70, text_.height + 10)
  //height: 80
  //color: '#ced0d6'

  //gradient: Gradient {
  //  GradientStop { position: 0.0;  color: '#c8c9d0' }
  //  GradientStop { position: 0.17; color: '#dfdfe3' }
  //  GradientStop { position: 0.77; color: '#f1f1f3' }
  //  GradientStop { position: 1.0;  color: '#f0f0f3' }
  //}

  Share.CachedAvatarImage { id: avatar_
    anchors {
      left: parent.left; top: parent.top
      leftMargin: 9
      topMargin: 3
    }
    width: 40; height: 40
    userId: currentItem ? currentItem.userId : 0
    userHash: currentItem ? currentItem.userHash : 0
  }

  TextEdit { id: text_
    anchors {
      top: parent.top //; bottom: parent.bottom
      right: parent.right
      left: avatar_.visible ? avatar_.right : parent.left
      leftMargin: 9; rightMargin: 9
      topMargin: 3
    }
    textFormat: TextEdit.RichText
    font.pixelSize: 12

    wrapMode: TextEdit.Wrap
    selectByMouse: true

    text: summary()
  }

  function summary() {
    if (!currentItem)
      return ""

    var ret = ""
    var ts = Util.timestampToString(currentItem.timestamp)
    ret += Sk.tr("Creation") + ": @" + currentItem.userName + " (" + ts + ")"
    if (currentItem.comment)
      ret += ": " + currentItem.comment

    if (currentItem.updateUserId) {
      ret += "\n"
      ts = Util.timestampToString(currentItem.updateTimestamp)
      ret += Sk.tr("Update") + ": @" + currentItem.updateUserName + " (" + ts + ")"
      if (currentItem.updateComment)
        ret += ": " + currentItem.updateComment
    }

    ret += "\n"
    ret += Sk.tr("Content") + ": " + currentItem.text

    if (currentItem.context) {
      ret += "\n"
      ret += Sk.tr("Context") + ": "
      var l = currentItem.context.split(_CONTEXT_SEP)
      ret += l[l.length -1]
      if (l.length > 1) {
        ret += "\n"
        ret += My.tr("Previous context") + ": "
        l.pop()
        ret += l.join("\n")
      }
    }
    return ret
  }
}

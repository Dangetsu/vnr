/** inspector.qml
 *  2/21/2013 jichi
 */
import QtQuick 1.1
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/eval.min.js' as Eval
import '../../../js/underscore.min.js' as Underscore
import '../../../js/util.min.js' as Util
import '../share' as Share

Item { id: root_

  property QtObject currentItem // dataman.Reference
  property QtObject model // dataman.ReferenceModel

  // - Private -

  //height: 70 // should be large enough to cover all texts
  height: Math.max(70, text_.height + footer_.height + 10)
  //color: '#ced0d6'

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
      top: parent.top //; bottom: footer_.bottom
      right: parent.right
      left: avatar_.visible ? avatar_.right : parent.left
      leftMargin: 9; rightMargin: 9
      topMargin: 3
    }
    textFormat: TextEdit.RichText
    font.pixelSize: 12

    wrapMode: TextEdit.WordWrap
    selectByMouse: true
    onLinkActivated: Eval.evalLink(link)

    text: summary()
  }

  function summary() {
    var ret = ""
    if (currentItem) {
      var ts = Util.timestampToString(currentItem.timestamp)
      ret += Sk.tr("Creation") + ": " + renderUser(currentItem.userName) + " (" + ts + ")"
      if (currentItem.comment)
        ret += ": " + Underscore.escape(currentItem.comment)

      if (currentItem.updateUserId) {
        ret += "<br/>"
        ts = Util.timestampToString(currentItem.updateTimestamp)
        ret += Sk.tr("Update") + ": " + renderUser(currentItem.updateUserName) + " (" + ts + ")"
        if (currentItem.updateComment)
          ret += ": " + Underscore.escape(currentItem.updateComment)
      }
    }
    return ret
  }

  function openUrl(link) {
    growlPlugin_.msg(My.tr("Open in external browser") + "<br/>" + link)
    Qt.openUrlExternally(link)
  }

  Row { id: footer_
    anchors {
      left: parent.left; right: parent.right
      bottom: parent.bottom
      leftMargin: 9; rightMargin: 9
      bottomMargin: 5
    }

    spacing: 10

    //property int cellWidth: 80
    property int pixelSize: 12

    Text {
      //width: parent.cellWidth
      font.pixelSize: parent.pixelSize
      textFormat: Text.RichText
      wrapMode: Text.NoWrap
      onLinkActivated: root_.openUrl(link)
      text: root_.formatText('ErogeTrailers', 'erogetrailers.com', model.trailersItem)
    }

    Text {
      //width: parent.cellWidth
      font.pixelSize: parent.pixelSize
      textFormat: Text.RichText
      wrapMode: Text.NoWrap
      onLinkActivated: root_.openUrl(link)
      text: root_.formatText('ErogameScape', 'erogamescape.dyndns.org/~ap2/ero/toukei_kaiseki', model.scapeItem)
    }

    Text {
      //width: parent.cellWidth
      font.pixelSize: parent.pixelSize
      textFormat: Text.RichText
      wrapMode: Text.NoWrap
      onLinkActivated: root_.openUrl(link)
      text: root_.formatText('Holyseal', 'holyseal.net', model.holysealItem)
    }

    Text {
      //width: parent.cellWidth
      font.pixelSize: parent.pixelSize
      textFormat: Text.RichText
      wrapMode: Text.NoWrap
      onLinkActivated: root_.openUrl(link)
      text: root_.formatText('Getchu', 'getchu.com', model.getchuItem)
    }

    Text {
      //width: parent.cellWidth
      font.pixelSize: parent.pixelSize
      textFormat: Text.RichText
      wrapMode: Text.NoWrap
      onLinkActivated: root_.openUrl(link)
      text: root_.formatText('Melon', 'melonbooks.co.jp', model.melonItem)
    }

    Text {
      //width: parent.cellWidth
      font.pixelSize: parent.pixelSize
      textFormat: Text.RichText
      wrapMode: Text.NoWrap
      onLinkActivated: root_.openUrl(link)
      text: root_.formatText('Amazon', 'amazon.co.jp', model.amazonItem)
    }

    Text {
      //width: parent.cellWidth
      font.pixelSize: parent.pixelSize
      textFormat: Text.RichText
      wrapMode: Text.NoWrap
      onLinkActivated: root_.openUrl(link)
      text: root_.formatText('DMM', 'dmm.co.jp', model.dmmItem)
    }

    Text {
      //width: parent.cellWidth
      font.pixelSize: parent.pixelSize
      textFormat: Text.RichText
      wrapMode: Text.NoWrap
      onLinkActivated: root_.openUrl(link)
      text: root_.formatText('DLsite', 'dlsite.co.jp', model.dlsiteItem)
    }

    Text {
      //width: parent.cellWidth
      font.pixelSize: parent.pixelSize
      textFormat: Text.RichText
      wrapMode: Text.NoWrap
      onLinkActivated: root_.openUrl(link)
      text: root_.formatText('DiGiket', 'www.digiket.com', model.digiketItem)
    }

    Text {
      //width: parent.cellWidth
      font.pixelSize: parent.pixelSize
      textFormat: Text.RichText
      wrapMode: Text.NoWrap
      onLinkActivated: root_.openUrl(link)
      text: root_.formatText('Gyutto', 'gyutto.com', model.gyuttoItem)
    }

    Text {
      //width: parent.cellWidth
      font.pixelSize: parent.pixelSize
      textFormat: Text.RichText
      wrapMode: Text.NoWrap
      onLinkActivated: root_.openUrl(link)
      text: root_.formatText('FreeM', 'freem.ne.jp', model.freemItem)
    }

    Text {
      //width: parent.cellWidth
      font.pixelSize: parent.pixelSize
      textFormat: Text.RichText
      wrapMode: Text.NoWrap
      onLinkActivated: root_.openUrl(link)
      text: root_.formatText('Steam', 'steampowered.com', model.steamItem)
    }
  }

  function formatText(name, url, item) { // string, string, Reference -> string
    return '<a style="color:' + (item ? 'green' : 'brown') + '" href="' + (item ? item.url : url) + '">' + name + '</a>'
  }

  function renderUser(name) {
    name = Underscore.escape(name)
    return "<a href=\"javascript://main.showUser('" + name + "')\">@" + name + "</a>"
  }
}

/** bbcode.qml
 *  5/27/2014 jichi
 */
import QtQuick 1.1
import '../js/npm/bbcode.min.js' as BBCode
import '../js/linkify.min.js' as Linkify
import '../js/underscore.string.min.js' as S_

Item {
  implicitWidth: 250; implicitHeight: 400

  // - Private -

  Text {
    anchors.centerIn: parent
    text: BBCode.parse(Linkify.parse(S_.escapeHTML("><http://www.google.com"))).replace(/<li><\/li>/g, '<li>')
    textFormat: Text.RichText
  }
}

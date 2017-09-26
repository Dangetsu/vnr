/** textcolumn.qml
 *  7/20/2013 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/util.min.js' as Util

Desktop.TableColumn {
  role: 'object'; title: My.tr("Character name")
  width: 120

  property alias color: text_.color

  delegate: Item { id: delegate_
    height: 25
    Text { id: text_
      anchors { fill: parent; leftMargin: 5 }
      textFormat: Text.PlainText
      clip: true
      verticalAlignment: Text.AlignVCenter
      text: itemValue.name ? itemValue.name : "(" + Sk.tr("Aside") + ")"
      color: itemSelected ? 'white' : entryColor(itemValue)
      //font.strikeout: !itemSelected && !itemValue.ttsEnabled
      font.bold: itemValue.ttsEnabled
    }
  }
}

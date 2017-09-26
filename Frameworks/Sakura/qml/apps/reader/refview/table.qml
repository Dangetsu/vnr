/** table.qml
 *  2/20/2013 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
//import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/util.min.js' as Util

Item { id: root_

  property int userId
  property int gameId
  property alias model: table_.model
  property alias currentIndex: table_.currentIndex
  //property QtObject currentGame // gameman.GameObject
  //property alias filterText: model_.filterText
  //property alias filterCount: model_.filterCount
  //property alias count: model_.count

  property alias sortIndicatorDirection: table_.sortIndicatorDirection
  property alias sortIndicatorColumn: table_.sortColumn

  // - Private -

  property int _SUPER_USER_ID: 2
  property int _GUEST_USER_ID: 4

  //property color _DISABLED_COLOR: 'silver'
  property color _EDITABLE_COLOR: 'green'
  property color _READONLY_COLOR: 'steelblue'
  property color _HIGHLIGHT_COLOR: 'purple'

  //Plugin.DataManagerProxy { id: datamanPlugin_ }

  function canEdit(r) {
    return !!r && !!userId && (userId === _SUPER_USER_ID
        || r.userId === userId && !r.protected)
  }

  function canImprove(r) {
    return !!r && !!userId && (r.userId === userId && ! r.protected
        || !!userId && userId !== _GUEST_USER_ID)
  }

  function shouldHighlight(r) { return gameId === Number(r.gameId) }

  function itemColor(r) {
    return datamanPlugin_.queryUserColor(r.userId) || (
        canEdit(r) ? _EDITABLE_COLOR : 'black')
  }

  function itemUpdateColor(r) {
    return datamanPlugin_.queryUserColor(r.updateUserId) || (
        canEdit(r) ? _EDITABLE_COLOR : 'black')
  }

  function gameSummary(id) {
    if (!id)
      return ""
    var n = datamanPlugin_.queryGameFileName(id)
    if (!n)
      return ""
    return n + " (" + id + ")"
  }

  function itemSummary(id) {
    if (!id)
      return ""
    var n = datamanPlugin_.queryItemName(id)
    if (!n)
      return ""
    return n + " (" + id + ")"
  }

  //property int _MIN_TEXT_LENGTH: 1
  property int _MAX_TEXT_LENGTH: 255

  Desktop.TableView { id: table_
    anchors.fill: parent

    sortIndicatorVisible: true

    property int cellHeight: 25
    property int cellSpacing: 5
    contentWidth: width // Prevent recursive binding bug in QtDesktop

    // Column: Row
    Desktop.TableColumn {
      role: 'number'; title: "#"
      width: 30
      //delegate: Item {
      //  height: table_.cellHeight
      //  Text {
      //    anchors { fill: parent; leftMargin: table_.cellSpacing }
      //  textFormat: Text.PlainText
      //    clip: true
      //    verticalAlignment: Text.AlignVCenter
      //    text: itemValue
      //    color: itemSelected ? 'white' : editable ? 'green' : 'black'
      //    font.strikeout: itemValue.disabled
      //  }
      //}
    }

    // Column: Disabled

    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Enable")
      width: 40
      delegate: Item {
        height: table_.cellHeight
        Desktop.CheckBox {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          enabled: canImprove(itemValue)
          checked: !itemValue.disabled
          onCheckedChanged:
            if (enabled && checked === itemValue.disabled) {
              //if (checked)
              //  model.enableItem(itemValue)
              //else
              //  model.disableItem(itemValue)
              model.toggleItemEnabled(itemValue)
              checked = !itemValue.disabled
            }
        }
      }
    }

    // Column: Game
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("File")
      width: 100
      delegate: Item {
        height: table_.cellHeight
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          //horizontalAlignment: Text.AlignHCenter
          text: gameSummary(itemValue.gameId)
          color: itemSelected ? 'white' : shouldHighlight(itemValue) ? _HIGHLIGHT_COLOR : _READONLY_COLOR
          font.strikeout: itemValue.disabled
          //font.bold: !itemValue.disabled
        }
      }
    }

    // Column: Item
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Cluster")
      width: 100
      delegate: Item {
        height: table_.cellHeight
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          //horizontalAlignment: Text.AlignHCenter
          text: itemSummary(itemValue.itemId)
          color: itemSelected ? 'white' : shouldHighlight(itemValue) ? _HIGHLIGHT_COLOR : _READONLY_COLOR
          font.strikeout: itemValue.disabled
          //font.bold: !itemValue.disabled
        }
      }
    }

    // Column: Type
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Site")
      width: 50
      delegate: Item {
        height: table_.cellHeight
        property bool editable: canEdit(itemValue)
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          //visible: !itemSelected || !editable
          text: {
              switch (itemValue.type) {
              case 'trailers': return "Trailers"
              case 'scape': return "ErogameScape"
              case 'melon': return "Melon"
              case 'getchu': return "Getchu"
              case 'gyutto': return "Gyutto"
              case 'digiket': return "DiGiket"
              case 'holyseal': return "Holyseal"
              case 'dlsite': return "DLsite"
              case 'dmm': return "DMM"
              case 'amazon': return "Amazon"
              case 'freem': return "FreeM"
              case 'steam': return "Steam"
              default: return Sk.tr("Unknown")
            }
          }
          color: itemSelected ? 'white' : itemColor(itemValue)
          //color: itemSelected ? 'white' : shouldHighlight(itemValue) ? _HIGHLIGHT_COLOR : _READONLY_COLOR
          font.strikeout: !itemSelected && itemValue.disabled
          //font.bold: !itemValue.disabled
        }
      }
    }

    // Column: Title
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Title")
      width: 150
      delegate: Item {
        height: table_.cellHeight
        property bool editable: canEdit(itemValue)
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          //visible: !itemSelected || !editable
          text: itemValue.title
          //color: itemSelected ? 'white' : shouldHighlight(itemValue) ? _HIGHLIGHT_COLOR : _READONLY_COLOR
          color: itemSelected ? 'white' : itemColor(itemValue)
          font.strikeout: !itemSelected && itemValue.disabled
          //font.bold: !itemValue.disabled
        }
      }
    }

    // Column: Brand
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Brand")
      width: 80
      delegate: Item {
        height: table_.cellHeight
        property bool editable: canEdit(itemValue)
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          //visible: !itemSelected || !editable
          text: itemValue.brand
          //color: itemSelected ? 'white' : shouldHighlight(itemValue) ? _HIGHLIGHT_COLOR : _READONLY_COLOR
          color: itemSelected ? 'white' : itemColor(itemValue)
          font.strikeout: !itemSelected && itemValue.disabled
          //font.bold: !itemValue.disabled
        }
      }
    }

    // Column: Release date
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Release date")
      width: 120
      delegate: Item {
        height: table_.cellHeight
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          text: itemValue.date > 0 ? Util.dateToString(new Date(itemValue.date * 1000))  : '(' + Sk.tr("unknown") + ')'
          //color: itemSelected ? 'white' : shouldHighlight(itemValue) ? _HIGHLIGHT_COLOR : _READONLY_COLOR
          color: itemSelected ? 'white' : itemColor(itemValue)
          font.strikeout: !itemSelected && itemValue.disabled
        }
      }
    }

    // Column: Comment
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Comment")
      width: 160
      delegate: Item {
        height: table_.cellHeight
        property bool editable: canEdit(itemValue)
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          visible: !itemSelected || !editable
          text: itemValue.comment
          color: itemSelected ? 'white' : itemColor(itemValue)
          //font.strikeout: !itemSelected && itemValue.disabled
          //font.bold: !itemValue.disabled
        }
        TextInput {
          anchors { fill: parent; leftMargin: table_.cellSpacing; topMargin: 6 }
          color: 'white'
          selectByMouse: true
          selectionColor: 'white'
          selectedTextColor: 'black'
          visible: itemSelected && editable
          maximumLength: _MAX_TEXT_LENGTH

          Component.onCompleted: text = itemValue.comment

          onTextChanged: save()
          onAccepted: save()
          function save() {
            if (editable) {
              var t = Util.trim(text)
              if (t !== itemValue.comment) {
                itemValue.comment = t
                itemValue.updateUserId = root_.userId
                itemValue.updateTimestamp = Util.currentUnixTime()
              }
            }
          }
        }
      }
    }

    // Column: User Name
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Creator")
      width: 80
      delegate: Item {
        height: table_.cellHeight
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          text: '@' + itemValue.userName
          color: itemSelected ? 'white' : _READONLY_COLOR
        }
      } }

    // Column: Timestamp
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Creation time")
      width: 120
      delegate: Item {
        height: table_.cellHeight
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          text: Util.timestampToString(itemValue.timestamp)
          color: itemSelected ? 'white' : _READONLY_COLOR
        }
      }
    }

    // Column: Update User Name
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Update")
      width: 80
      delegate: Item {
        height: table_.cellHeight
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          text: itemValue.updateUserId ? '@' + itemValue.updateUserName : ""
          color: itemSelected ? 'white' : _READONLY_COLOR
        }
      }
    }

    // Column: Timestamp
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Update time")
      width: 120
      delegate: Item {
        height: table_.cellHeight
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          text: itemValue.updateTimestamp > 0 ? Util.timestampToString(itemValue.updateTimestamp)  : ''
          color: itemSelected ? 'white' : _READONLY_COLOR
        }
      }
    }

    // Column: Update Comment

    Desktop.TableColumn {
      role: 'object'; title: My.tr("Update reason")
      width: 160
      delegate: Item {
        height: table_.cellHeight
        property bool editable: itemValue.updateUserId === root_.userId
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          visible: !itemSelected || !editable
          text: itemValue.updateComment
          color: itemSelected ? 'white' : itemUpdateColor(itemValue)
          //font.strikeout: itemValue.disabled
          //font.bold: !itemValue.disabled
        }
        TextInput {
          anchors { fill: parent; leftMargin: table_.cellSpacing; topMargin: 6 }
          color: 'white'
          selectByMouse: true
          selectionColor: 'white'
          selectedTextColor: 'black'
          visible: itemSelected && editable
          maximumLength: _MAX_TEXT_LENGTH

          // The updateComment could be modified by dataman
          //Component.onCompleted: text = itemValue.updateComment
          text: itemValue.updateComment

          onTextChanged: save()
          onAccepted: save()
          function save() {
            if (editable) {
              var t = Util.trim(text)
              if (t !== itemValue.updateComment) {
                itemValue.updateComment = t
                itemValue.updateUserId = root_.userId
                itemValue.updateTimestamp = Util.currentUnixTime()
              }
            }
          }
        }
      }
    }

    // New Column
  }

  //function enableReference(r) {
  //  r.disabled = false
  //  r.updateUserId = userId
  //  r.updateTimestamp = Util.currentUnixTime()
  //  return true
  //}
  //function disableReference(r) {
  //  return datamanPlugin_.disableComment(c)
  //}
}

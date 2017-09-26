/** table.qml
 *  2/20/2013 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/util.min.js' as Util

Item { id: root_

  property int userId
  property int userLevel
  property alias model: table_.model
  property alias currentIndex: table_.currentIndex
  //property QtObject currentGame // gameman.GameObject
  //property alias filterText: model_.filterText
  //property alias filterCount: model_.filterCount
  //property alias count: model_.count

  property alias sortIndicatorDirection: table_.sortIndicatorDirection
  property alias sortIndicatorColumn: table_.sortColumn
  
  Plugin.SystemStatus { id: statusPlugin_ }
  
  function positionViewAtBeginning() { table_.positionViewAtBeginning() }
  function positionViewAtEnd() { table_.positionViewAtEnd() }

  // - Private -

  property int _SUPER_USER_ID: 2
  property int _GUEST_USER_ID: 4

  //property color _DISABLED_COLOR: 'silver'
  property color _EDITABLE_COLOR: 'green'
  property color _READONLY_COLOR: 'steelblue'
  property color _HIGHLIGHT_COLOR: 'red'

  Plugin.DataManagerProxy { id: datamanPlugin_ }
  //Plugin.Growl { id: growl_ }

  function canEdit(c) {
	
    var userAccess = [];
    if(statusPlugin_.userAccess){
        var userAccessMass = statusPlugin_.userAccess.split(',');
        for(var i = 0; i < userAccessMass.length; i++){
            userAccess[userAccess.length] = userAccessMass[i];
        }
    }

    return !!c && !!userId && (userId === _SUPER_USER_ID
        || c.userId === userId && !c.protected
        || userAccess.length > 0 && (userAccess.indexOf(c.userId+':'+datamanPlugin_.gameItemId)>=0)
        || c.userId === _GUEST_USER_ID && userLevel > 0);
  }

  function canImprove(c) {
    var userAccess = [];
    if(statusPlugin_.userAccess){
        var userAccessMass = statusPlugin_.userAccess.split(',');
        for(var i = 0; i < userAccessMass.length; i++){
            userAccess[userAccess.length] = userAccessMass[i];
        }
    }
    return !!c && !!userId && (c.userId === userId && !c.protected
        || userAccess.length > 0 && (userAccess.indexOf(c.userId+':'+datamanPlugin_.gameItemId)>=0)
        || userId !== _GUEST_USER_ID && !c.locked)
  }

  function canSelect(c) {
    return canImprove(c)
  }

  function shouldHighlight(c) {
    return c.type === 'popup'
  }

  function itemColor(c) {
    return shouldHighlight(c) ? _HIGHLIGHT_COLOR :
      datamanPlugin_.queryUserColor(c.userId) || (
        canEdit(c) ? _EDITABLE_COLOR : 'black')
  }

  function commentColor(c) {
    return datamanPlugin_.queryUserColor(c.updateUserId) || (
        canEdit(c) ? _EDITABLE_COLOR : 'black')
  }

  function updateCommentColor(c) {
    return datamanPlugin_.queryUserColor(c.updateUserId) || (
        canEdit(c) ? _EDITABLE_COLOR : 'black')
  }

  function gameSummary(id) {
    if (!id)
      return ""
    var n = datamanPlugin_.queryGameFileName(id)
    if (!n)
      return ""
    return n + " (" + id + ")"
  }

  property int _MIN_TEXT_LENGTH: 1
  property int _MAX_TEXT_LENGTH: 255

  Desktop.TableView { id: table_
    anchors.fill: parent

    sortIndicatorVisible: true

    property int cellHeight: 25
    property int cellSpacing: 5
    contentWidth: width // Prevent recursive binding bug in QtDesktop

    sortColumn: 1 // the initial sorting column is the second one

    // Column: Selected
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Select")
      width: 30
      delegate: Item {
        height: table_.cellHeight
        Desktop.CheckBox {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          enabled: canSelect(itemValue)
          checked: itemValue.selected
          onCheckedChanged:
            if (enabled && checked !== itemValue.selected) {
              itemValue.selected = checked
              table_.model.refreshSelection()
            }

          function setChecked(t) { checked = t }
          Component.onCompleted: itemValue.selectedChanged.connect(setChecked)
          Component.onDestruction: itemValue.selectedChanged.disconnect(setChecked)
        }
      }
    }

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
            if (enabled && checked === itemValue.disabled)
              datamanPlugin_.enableComment(itemValue, checked)
              //checked = !itemValue.disabled

          function setNotChecked(t) { checked = !t }
          Component.onCompleted: itemValue.disabledChanged.connect(setNotChecked)
          Component.onDestruction: itemValue.disabledChanged.disconnect(setNotChecked)
        }
      }
    }

    // Column: Type
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Type")
      width: 60
      delegate: Item {
        height: table_.cellHeight
        property bool editable: canEdit(itemValue)
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          text: {
            switch (itemValue.type) {
            case 'danmaku': return Sk.tr("Danmaku")
            case 'comment': return Sk.tr("Comment")
            case 'subtitle': return Sk.tr("Subtitle")
            case 'popup': return My.tr("Note")
            default: return Sk.tr("Danmaku")
            }
          }
          visible: !itemSelected || !editable
          color: itemSelected ? 'white' : itemColor(itemValue)
          font.strikeout: itemValue.disabled
          font.bold: itemValue.locked
        }
        Desktop.ComboBox {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          model: ListModel { //id: typeModel_
            Component.onCompleted: {
              append({value:'danmaku', text:Sk.tr("Danmaku")})
              append({value:'comment', text:Sk.tr("Comment")})
              append({value:'subtitle', text:Sk.tr("Subtitle")})
              append({value:'popup', text:My.tr("Note")})
            }
          }

          tooltip: Sk.tr("Type")
          visible: itemSelected && editable

          onSelectedIndexChanged:
            if (editable) {
              var t = model.get(selectedIndex).value
              if (t !== itemValue.type) {
                itemValue.type = t
                itemValue.updateUserId = root_.userId
                itemValue.updateTimestamp = Util.currentUnixTime()
              }
            }

          selectedText: model.get(selectedIndex).text
          Component.onCompleted: {
            switch (itemValue.type) { // Must be consistent with the model
            case 'danmaku': selectedIndex = 0; break
            case 'comment': selectedIndex = 1; break
            case 'subtitle': selectedIndex = 2; break
            case 'popup': selectedIndex = 3; break
            default: selectedIndex = 0
            }
          }
        }
      }
    }

    // Column: Language
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Language")
      width: 40
      delegate: Item {
        height: table_.cellHeight
        property bool editable: canEdit(itemValue)
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          text: Sk.tr(Util.languageShortName(itemValue.language || 'en'))
          visible: !itemSelected || !editable
          color: itemSelected ? 'white' : itemColor(itemValue)
          font.strikeout: itemValue.disabled
          font.bold: itemValue.locked
        }
        Desktop.ComboBox {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          model: ListModel { //id: languageModel_
            Component.onCompleted: {
              for (var i in Util.LANGUAGES) {
                var lang = Util.LANGUAGES[i]
                append({
                  value: lang
                  , text: Sk.tr(Util.languageShortName(lang))
                })
              }
            }
          }

          tooltip: My.tr("Language")
          visible: itemSelected && editable

          onSelectedIndexChanged:
            if (editable) {
              var t = model.get(selectedIndex).value
              if (t !== itemValue.language) {
                itemValue.language = t
                itemValue.updateUserId = root_.userId
                itemValue.updateTimestamp = Util.currentUnixTime()
              }
            }

          selectedText: model.get(selectedIndex).text

          Component.onCompleted: {
            for (var i = 0; i < model.count; ++i)
              if (model.get(i).value === itemValue.language)
                selectedIndex = i
          }
        }
      }
    }

    // Column: Locked
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Lock")
      width: 40
      delegate: Item {
        height: table_.cellHeight
        Desktop.CheckBox {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          enabled: canEdit(itemValue) && root_.userId !== _GUEST_USER_ID
          checked: itemValue.locked
          onCheckedChanged:
            if (enabled && checked !== itemValue.locked)
              itemValue.locked = checked
        }
      }
    }

    // Column: Like
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Like")
      width: 30
      delegate: Item {
        height: table_.cellHeight
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          visible: !!itemValue.likeCount
          text: itemValue.likeCount ? '+' + itemValue.likeCount : ''
          color: itemSelected ? 'white' : itemColor(itemValue)
          font.strikeout: !itemSelected && itemValue.disabled
          font.bold: itemValue.locked
        }
      }
    }
    // Column: Like
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Dislike")
      width: 30
      delegate: Item {
        height: table_.cellHeight
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          visible: !!itemValue.dislikeCount
          text: itemValue.dislikeCount ? '-' + itemValue.dislikeCount : ''
          color: itemSelected ? 'white' : itemColor(itemValue)
          font.strikeout: !itemSelected && itemValue.disabled
          font.bold: itemValue.locked
        }
      }
    }

    // Column: Text
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Text")
      width: 150
      delegate: Item {
        height: table_.cellHeight
        property bool editable: canEdit(itemValue)
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          visible: !itemSelected //|| !editable
          text: itemValue.text
          color: itemSelected ? 'white' : itemColor(itemValue)
          font.strikeout: !itemSelected && itemValue.disabled
          font.bold: itemValue.locked
        }
        TextInput {
          anchors { fill: parent; leftMargin: table_.cellSpacing; topMargin: 6 }
          color: valid ? 'white' : 'red'
          selectByMouse: true
          selectionColor: 'white'
          selectedTextColor: 'black'
          visible: itemSelected //&& editable
          readOnly: !editable
          maximumLength: _MAX_TEXT_LENGTH
          //font.bold: itemValue.locked

          property bool valid: Util.trim(text).length >= _MIN_TEXT_LENGTH

          Component.onCompleted: text = itemValue.text

          onTextChanged: save()
          onAccepted: save()
          function save() {
            if (editable) {
              var t = Util.trim(text)
              if (t && t !== itemValue.text && valid) {
                itemValue.text = t
                itemValue.updateUserId = root_.userId
                itemValue.updateTimestamp = Util.currentUnixTime()
              }
            }
          }
        }
      }
    }

    // Column: Context
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Context")
      width: 150
      delegate: Item {
        height: table_.cellHeight
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          text: itemValue.context.replace(/\n/g, " ")
          color: itemSelected ? 'white' : _READONLY_COLOR
          //color: itemSelected ? 'white' : itemColor(itemValue)
          font.strikeout: !itemSelected && itemValue.disabled
          font.bold: itemValue.locked
        }
      }
    }

    // Column: Context Size
    Desktop.TableColumn {
      role: 'object'; title: My.tr("ctx")
      width: 30
      delegate: Item {
        height: table_.cellHeight
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          //horizontalAlignment: Text.AlignHCenter
          text: String(itemValue.contextSize)
          color: itemSelected ? 'white' : _READONLY_COLOR
          font.strikeout: itemValue.disabled
          font.bold: itemValue.locked
        }
      }
    }

    // Column: Game
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Game")
      width: 40
      delegate: Item {
        height: table_.cellHeight
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          //horizontalAlignment: Text.AlignHCenter
          text: gameSummary(itemValue.gameId)
          //text: String(itemValue.gameId)
          color: itemSelected ? 'white' : _READONLY_COLOR
          font.strikeout: itemValue.disabled
          font.bold: itemValue.locked
        }
      }
    }

    // Column: Comment
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Comment")
      width: 120
      delegate: Item {
        height: table_.cellHeight
        property bool editable: canEdit(itemValue)
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          visible: !itemSelected //|| !editable
          text: itemValue.comment
          color: itemSelected ? 'white' : commentColor(itemValue)
          //font.strikeout: !itemSelected && itemValue.disabled
          //font.bold: itemValue.locked
        }
        TextInput {
          anchors { fill: parent; leftMargin: table_.cellSpacing; topMargin: 6 }
          color: 'white'
          selectByMouse: true
          selectionColor: 'white'
          selectedTextColor: 'black'
          visible: itemSelected //&& editable
          readOnly: !editable
          maximumLength: _MAX_TEXT_LENGTH

          text: itemValue.comment

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
      }
    }

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
          text: itemValue.updateTimestamp > 0 ? Util.timestampToString(itemValue.updateTimestamp) : ''
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
          visible: !itemSelected //|| !editable
          text: itemValue.updateComment
          color: itemSelected ? 'white' : updateCommentColor(itemValue)
          //font.strikeout: itemValue.disabled
          //font.bold: itemValue.locked
        }
        TextInput {
          anchors { fill: parent; leftMargin: table_.cellSpacing; topMargin: 6 }
          color: 'white'
          selectByMouse: true
          selectionColor: 'white'
          selectedTextColor: 'black'
          visible: itemSelected //&& editable
          readOnly: !editable
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

  //function enableComment(c) {
  //  c.disabled = false
  //  c.updateUserId = userId
  //  c.updateTimestamp = Util.currentUnixTime()
  //  return true
  //}
  //function disableComment(c) {
  //  return datamanPlugin_.disableComment(c)
  //}
}

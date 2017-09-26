/** table.qml
 *  6/22/2013 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/util.min.js' as Util

Item { id: root_

  property alias model: table_.model
  property alias currentIndex: table_.currentIndex
  property QtObject currentEntry // gameman.GameObject
  //property alias filterText: model_.filterText
  //property alias filterCount: model_.filterCount
  //property alias count: model_.count

  property alias sortIndicatorDirection: table_.sortIndicatorDirection
  property alias sortIndicatorColumn: table_.sortColumn

  // - Private -

  Plugin.Tts { id: tts_ }
  property variant ttsEngines: tts_.availableEngines() ? tts_.availableEngines().split(',') : []

  //Component.onCompleted: {
  //  console.log(ttsEngines)
  //  console.log(ttsEngines.length)
  //}

  function entryColor(entry) { // object -> string
    switch (entry.gender) {
    case 'f': return 'purple'
    case 'm': return 'steelblue'
    default: return 'black'
    }
  }

  function characterName(name) { // string -> string
    switch (name) {
    case '': return "(" + Sk.tr("Aside") + ")"
    case '?': return "(" + Sk.tr("Unknown") + ")"
    default: return name
    }
  }

  function ttsEngineName(key) { // string -> string
    switch (key) {
    case '': return Sk.tr('Default')
    case 'google': return "Google.com"
    case 'bing': return "Bing.com"
    case 'naver': return "Naver.com"
    case 'baidu': return My.tr("Baidu") + ".com"

    case 'yukarioffline': return "結月ゆかり(♀)"
    case 'zunkooffline': return "東北ずん子(♀)"

    // Voiceroid
    case 'yukari': return "結月ゆかり(♀)"
    case 'maki':   return "民安ともえ(♀)"
    case 'zunko':  return "東北ずん子(♀)"
    case 'aoi':    return "琴葉 葵(♀)"
    case 'akane':  return "琴葉 茜(♀)"
    case 'ai':     return "月読アイ(♀)"
    case 'shota':  return "月読ショタ(♂)"
    case 'taka':   return "鷹の爪 吉田くん(♂)"

    // VoiceText

    case 'hikari': return "ヒカリ(ja,♀)"
    case 'sayaka': return "サヤカ(ja,♀)"
    case 'haruka': return "ハルカ(ja,♀)"
    case 'misaki': return "ミサカ(ja,♀)"
    case 'takeru': return "タケル(ja,♂)"
    case 'ryo':    return "リョウ(ja,♂)"
    case 'show':   return "ショウ(ja,♂)"

    case 'hong':   return "小紅(zh,♀)"
    case 'qiang':  return "小强(zh,♂)"

    case 'hyeryun':return "혜련(ko,♀)"
    case 'jihun':  return "지훈(ko,♂)"

    case 'julie':  return "Julie(en-US,♀)"
    case 'kate':   return "Kate(en-US,♀)"
    case 'james':  return "James(en-US,♂)"
    case 'paul':   return "Paul(en-US,♂)"

    case 'bridget': return "Bridget(en-GB,♀)"
    case 'hugh':    return "Hugh(en-GB,♂)"


    case 'violeta':   return "Violeta(es,♀)"
    case 'francisco': return "Francisco(es,♂)"

    case 'chloe':     return "Chloé(fr-CA,♀)"

    default: return key
    }
  }

  //property int _MIN_TEXT_LENGTH: 1
  //property int _MAX_TEXT_LENGTH: 255

  Desktop.TableView { id: table_
    anchors.fill: parent

    sortIndicatorVisible: true
    sortIndicatorDirection: 'up' // 'down' by default

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
          //enabled: canImprove(itemValue)
          checked: itemValue.ttsEnabled
          onCheckedChanged:
            if (checked !== itemValue.ttsEnabled) {
              itemValue.ttsEnabled = checked
              //itemValue.timestamp = Util.currentUnixTime()
            }
        }
      }
    }

    // Column: TTS Engine
    Desktop.TableColumn {
      role: 'object'; title: "TTS"
      width: 85
      delegate: Item {
        height: table_.cellHeight
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          text: root_.ttsEngineName(itemValue.ttsEngine)
          visible: !itemSelected
          color: itemSelected ? 'white' : entryColor(itemValue)
          //font.strikeout: !itemValue.ttsEnabled
          font.bold: itemValue.ttsEnabled
        }
        Desktop.ComboBox {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          model: ListModel { //id: genderModel_
            Component.onCompleted: {
              for (var i in root_.ttsEngines) {
                var it = root_.ttsEngines[i]
                append({value:it, text:root_.ttsEngineName(it)})
              }
            }
          }

          tooltip: Sk.tr("Type")
          visible: itemSelected

          onSelectedIndexChanged: {
            var t = model.get(selectedIndex).value
            if (t !== itemValue.ttsEngine) {
              itemValue.ttsEngine = t
              //itemValue.timestamp = Util.currentUnixTime()
            }
          }

          selectedText:  model.get(selectedIndex).text
          Component.onCompleted: {
            var i =  root_.ttsEngines.indexOf(itemValue.ttsEngine)
            if (i < 0)
              i = 0
            if (selectedIndex !== i)
              selectedIndex = i
          }
        }
      }
    }


    // Column: Gender
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Gender")
      width: 65
      delegate: Item {
        height: table_.cellHeight
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          text: {
            switch (itemValue.gender) {
            case 'f': return Sk.tr("Female")
            case 'm': return Sk.tr("Male")
            default: return Sk.tr("Not specified")
            }
          }
          visible: !itemSelected
          color: itemSelected ? 'white' : entryColor(itemValue)
          //font.strikeout: !itemValue.ttsEnabled
          font.bold: itemValue.ttsEnabled
        }
        Desktop.ComboBox {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          model: ListModel { //id: genderModel_
            Component.onCompleted: {
              append({value:'m', text:Sk.tr("Male")})
              append({value:'f', text:Sk.tr("Female")})
              append({value:'', text:Sk.tr("Not specified")})
            }
          }

          tooltip: Sk.tr("Type")
          visible: itemSelected

          onSelectedIndexChanged: {
            var t = model.get(selectedIndex).value
            if (t !== itemValue.gender) {
              itemValue.gender = t
              //itemValue.timestamp = Util.currentUnixTime()
            }
          }

          selectedText:  model.get(selectedIndex).text
          Component.onCompleted: {
            switch (itemValue.gender) { // Must be consistent with the model
            case 'm': selectedIndex = 0; break
            case 'f': selectedIndex = 1; break
            default: selectedIndex = 2
            }
          }
        }
      }
    }

    // Column: Text
    Desktop.TableColumn {
      role: 'object'; title: My.tr("Character name")
      width: 110
      delegate: Item {
        height: table_.cellHeight
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          text: root_.characterName(itemValue.name)
          color: itemSelected ? 'white' : entryColor(itemValue)
          //font.strikeout: !itemSelected && !itemValue.ttsEnabled
          font.bold: itemValue.ttsEnabled
        }
      }
    }

    // Column: Timestamp
    Desktop.TableColumn {
      role: 'object'; title: Sk.tr("Creation time")
      width: 150
      delegate: Item {
        height: table_.cellHeight
        Text {
          anchors { fill: parent; leftMargin: table_.cellSpacing }
          textFormat: Text.PlainText
          clip: true
          verticalAlignment: Text.AlignVCenter
          text: Util.timestampToString(itemValue.timestamp)
          color: itemSelected ? 'white' : entryColor(itemValue)
          font.bold: itemValue.ttsEnabled
        }
      }
    }

    // New Column
  }
}

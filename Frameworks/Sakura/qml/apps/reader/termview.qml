/** termview.qml
 *  2/20/2013 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../js/sakurakit.min.js' as Sk
import '../../js/reader.min.js' as My
import '../../js/util.min.js' as Util
import 'share' as Share
import 'termview' as TermView

//Share.View { id: root_
Item { id: root_
  //implicitWidth: 480; implicitHeight: 360
  width: 1080; height: 500

  // Window properties
  property string windowTitle: title() ///< window title
  function title() {
    var ret = My.tr("Shared Dictionary")
    if (table_.count > 0)
      ret += " (" + table_.count + ")"
    else
      ret += " (" + Sk.tr("Empty") + ")"
    return ret
  }

  // - Private -

  clip: true

  Component.onCompleted: {
    var lang = bean_.getSearchLanguage()
    var col = bean_.getSearchCol()
    var text = bean_.getSearchText()
    search(text, col, lang)
    console.log("termview.qml: pass")
  }

  Component.onDestruction: console.log("termview.qml:destroy: pass")

  //Plugin.DataManagerProxy { id: datamanPlugin_ }
  //Plugin.MainObjectProxy { id: mainPlugin_ }
  //Plugin.CometManagerProxy { id: cometPlugin_ }

  Plugin.Settings { id: settings_
    //onHentaiChanged: if (option_.hentaiEnabled != hentai) option_.hentaiEnabled = hentai
    //onTermMarkedChanged: if (option_.markEnabled != termMarked) option_.markEnabled = termMarked
  }

  Plugin.SystemStatus { id: statusPlugin_ } // FIXME: why this is indispensible
  property int userId: statusPlugin_.online ? statusPlugin_.userId : 0
  property alias userLevel: statusPlugin_.userTermLevel

  Plugin.TermViewBean { id: bean_
    Component.onCompleted:
      searchRequested.connect(root_.search)
  }

  Plugin.Tts { id: ttsPlugin_ }

  function search(text, col, lang) {
    searchToolBar_.clear()
    //console.log("termview.qml:search: col =", col)
    var changed = false
    changed = searchLang_.setValue(lang) || changed
    changed = searchCol_.setValue(col) || changed
    //changed = searchHost_.setValue(host) || changed
    if (searchBox_.text != text) {
      searchBox_.text = text
      changed = true
    }
    if (changed)
      searchBox_.accepted()
  }

  //function loadSettings() {
  //  mainToolBar_.enabled = settings_.termEnabled
  //}
  //function saveSettings() {
  //  settings_.termEnabled = mainToolBar_.enabled
  //}

  // ToolBar at the top

  TermView.MainToolBar { id: mainToolBar_
    anchors {
      left: parent.left; right: parent.right; top: parent.top
      topMargin: -1
    }

    currentItem: table_.currentItem
    userId: root_.userId
    userLevel: root_.userLevel

    Component.onCompleted: enabled = settings_.termEnabled
    onEnabledChanged:
      if (enabled !== settings_.termEnabled)
        settings_.termEnabled = enabled
  }

  // Table
  TermView.Table { id: table_
    anchors {
      left: parent.left; right: parent.right
      top: mainToolBar_.bottom
      bottom: selectToolBar_.visible ? selectToolBar_.top : searchBox_.top
    }
    userId: root_.userId
    userLevel: root_.userLevel

    displaysDuplicateRows: searchToolBar_.displaysDuplicateRows

    filterColumn: searchCol_.value
    filterLanguage: searchLang_.value
    filterSourceLanguage: searchSourceLang_.value
    filterHost: searchHost_.value
    filterTypes: filterToolBar_.values

    Share.Blocker {
      anchors.fill: parent
      visible: table_.currentCount <= 0 || !mainToolBar_.enabled
      text: (mainToolBar_.enabled ? Sk.tr("Empty") : Sk.tr("Disabled")) + "! ><"
    }

    Share.Navigator { //id: navToolBar_ // scroll buttons
      anchors {
        bottom: parent.bottom; right: parent.right
        margins: 25
      }

      onScrollTop: table_.positionViewAtBeginning()
      onScrollBottom: table_.positionViewAtEnd()
    }

    onPageNumberChanged:
      if (paginator_.value != pageNumber)
        paginator_.value = pageNumber
  }

  TermView.SelectToolBar { id: selectToolBar_
    anchors {
      left: parent.left; right: parent.right
      bottom: searchBox_.top
    }

    selectionCount: table_.selectionCount

    visible: selectionCount > 0 && settings_.termEnabled && !!root_.userId

    model: table_.model
  }

  // Middle row

  Share.Paginator { id: paginator_
    anchors {
      left: parent.left
      verticalCenter: searchBox_.verticalCenter
      leftMargin: 2
    }
    maximumValue: table_.maximumPageNumber
    onValueChanged:
      if (value != table_.pageNumber)
        table_.pageNumber = value
  }

  Desktop.ComboBox { id: searchHost_
    anchors {
      verticalCenter: searchBox_.verticalCenter
      left: paginator_.right
      leftMargin: 2
    }
    width: 65

    tooltip: My.tr("Translator")

    model: ListModel {
      Component.onCompleted: {
        append({value:'', text:My.tr("Translator")})
        for (var i in Util.TRANSLATOR_HOST_KEYS) {
          var key = Util.TRANSLATOR_HOST_KEYS[i]
          append({value:key, text:Util.translatorName(key)})
        }
      }
    }

    property string value
    onSelectedIndexChanged: value = model.get(selectedIndex).value

    // This function is not used
    //function setValue(v) { // string -> bool  whether changed
    //  if (!v)
    //    v = '' // for null
    //  for (var i = 0; i < model.count; ++i)
    //    if (model.get(i).value == v) {
    //      selectedIndex = i
    //      return true
    //    }
    //  return false
    //}
  }


  Desktop.ComboBox { id: searchSourceLang_
    anchors {
      verticalCenter: searchBox_.verticalCenter
      left: searchHost_.right
      leftMargin: 2
    }
    width: 60

    tooltip: Sk.tr("Language")

    model: ListModel {
      Component.onCompleted: {
        append({value:'', text:"From"})
        for (var i in Util.LANGUAGES) {
          var lang = Util.LANGUAGES[i]
          append({value:lang, text:Sk.tr(Util.languageShortName(lang))})
        }
      }
    }

    property string value
    onSelectedIndexChanged: value = model.get(selectedIndex).value

    // Not used
    //function setValue(v) { // string -> bool  whether changed
    //  if (!v)
    //    v = '' // for null
    //  if (v == value)
    //    return false
    //  var i = Util.LANGUAGES.indexOf(v)
    //  if (i !== -1) {
    //    selectedIndex = i
    //    return true
    //  }
    //  return false
    //}
  }

  Desktop.ComboBox { id: searchLang_
    anchors {
      verticalCenter: searchBox_.verticalCenter
      left: searchSourceLang_.right
      leftMargin: 2
    }
    width: 60

    tooltip: Sk.tr("Language")

    model: ListModel {
      Component.onCompleted: {
        append({value:'', text:"To"})
        for (var i in Util.LANGUAGES) {
          var lang = Util.LANGUAGES[i]
          append({value:lang, text:Sk.tr(Util.languageShortName(lang))})
        }
      }
    }

    property string value
    onSelectedIndexChanged: value = model.get(selectedIndex).value

    function setValue(v) { // string -> bool  whether changed
      if (!v)
        v = '' // for null
      if (v == value)
        return false
      var i = Util.LANGUAGES.indexOf(v)
      if (i !== -1) {
        selectedIndex = i
        return true
      }
      //for (var i = 0; i < model.count; ++i)
      //  if (model.get(i).value == v) {
      //    selectedIndex = i
      //    return true
      //  }
      return false
    }
  }

  Desktop.ComboBox { id: searchCol_
    anchors {
      verticalCenter: searchBox_.verticalCenter
      left: searchLang_.right
      leftMargin: 5
    }
    width: 60

    tooltip: Sk.tr("Column")

    model: ListModel {
      Component.onCompleted: {
        append({value:'', text:"*"})
        append({value:'id', text:"ID"})
        append({value:'user', text:Sk.tr("User")})
        append({value:'game', text:Sk.tr("Game")})
        append({value:'pattern', text:Sk.tr("Pattern")})
        append({value:'text', text:Sk.tr("Translation")})
        append({value:'ruby', text:My.tr("Ruby")})
        append({value:'role', text:Sk.tr("Role")})
        append({value:'comment', text:Sk.tr("Comment")})
      }
    }

    property string value
    onSelectedIndexChanged: value = model.get(selectedIndex).value

    function setValue(v) { // string -> bool  whether changed
      if (!v)
        v = '' // for null
      if (v == value)
        return false
      for (var i = 0; i < model.count; ++i)
        if (model.get(i).value == v) {
          selectedIndex = i
          return true
        }
      return false
    }
  }

  Share.SearchBox { id: searchBox_
    anchors {
      left: searchCol_.right
      //left: parent.left
      right: searchToolBar_.left
      bottom: inspector_.top
      leftMargin: 2
      rightMargin: 2
      bottomMargin: 5
    }
    totalCount: table_.count
    currentCount: table_.currentCount
    toolTip: qsTr("Type part of the pattern, text, user, language, etc, and press Enter to search")
           + " (" + Sk.tr("regular expression") + ", " + Sk.tr("case-insensitive") + ")"

    onAccepted: {
      table_.filterText = Util.trim(text)
      table_.refresh()
    }

    placeholderText: Sk.tr("Search") + " ... (" + holder() + ")"
    function holder() {
      return '@' + Sk.tr('user') + ", " + '#' + Sk.tr("game") //+ '#' + Sk.tr("game") + "ID, "
    }
  }

  TermView.SearchToolBar { id: searchToolBar_ // search buttons
    anchors {
      verticalCenter: searchBox_.verticalCenter
      right: parent.right
      rightMargin: 2
    }

    onTriggered: {
      searchBox_.text = text
      searchBox_.accepted()
    }
  }

  TermView.FilterToolBar { id: filterToolBar_
    anchors {
      top: searchToolBar_.bottom
      right: parent.right
      topMargin: 5
      rightMargin: 2
    }
  }

  TermView.Counter { id: counter_
    anchors {
      bottom: parent.bottom
      right: parent.right
      rightMargin: 5
      bottomMargin: 5
    }
  }

  // Bottom row

  // Inspector at the bottom
  TermView.Inspector { id: inspector_
    anchors {
      bottom: parent.bottom
      left: parent.left
      right: filterToolBar_.left
      rightMargin: 5
    }
    currentItem: table_.currentItem
    blockedLanguages: settings_.blockedLanguages
  }
}

// EOF

  //TermView.OptionPanel { id: option_
  //  anchors {
  //    right: parent.right
  //    bottom: parent.bottom
  //  }
  //  height: inspector_.height
  //
  //  Component.onCompleted: {
  //    hentaiEnabled = settings_.hentai
  //    markEnabled = settings_.termMarked
  //  }
  //  onHentaiEnabledChanged: if (settings_.hentai != hentaiEnabled) settings_.hentai = hentaiEnabled
  //  onMarkEnabledChanged: if (settings_.termMarked != markEnabled) settings_.termMarked = markEnabled
  //}

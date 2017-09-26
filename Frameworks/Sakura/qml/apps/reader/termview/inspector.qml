/** inspector.qml
 *  2/21/2013 jichi
 */
import QtQuick 1.1
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/eval.min.js' as Eval
import '../../../js/linkify.min.js' as Linkify
import '../../../js/underscore.min.js' as Underscore
import '../../../js/util.min.js' as Util
import '../share' as Share
import '.' as TermView

Item { id: root_

  property QtObject currentItem // dataman.Term
  property string blockedLanguages // string

  // - Private -

  height: Math.max(120, text_.height + 7)
  //color: '#ced0d6'

  function isLanguageBlocked(lang) { return blockedLanguages.indexOf(lang) !== -1 } // string -> bool

  Share.CachedAvatarImage { id: avatar_
    anchors {
      left: parent.left
      top: parent.top
      //verticalCenter: parent.verticalCenter
      topMargin: 3
      leftMargin: 9
    }
    width: 75
    //height: 75
    userId: currentItem ? currentItem.userId : 0
    userHash: currentItem ? currentItem.userHash : 0
  }

  TextEdit { id: text_
    anchors {
      top: parent.top //; bottom: parent.bottom
      right: cover_.visible ? cover_.left : parent.right
      left: avatar_.visible ? avatar_.right : parent.left
      leftMargin: 9; rightMargin: 9
      //topMargin: 0
    }
    textFormat: TextEdit.RichText
    font.pixelSize: 12

    wrapMode: TextEdit.WordWrap
    selectByMouse: true
    onLinkActivated: Eval.evalLink(link)

    text: summary()
  }

  Share.GameCoverImage { id: cover_
    anchors {
      right: parent.right
      top: parent.top; bottom: parent.bottom
      bottomMargin: 5
    }
    fileId: currentItem ? currentItem.gameId : 0
  }

  Plugin.JlpUtil { id: jlp_ }

  property variant _TYPE_NAMES: {
    trans: Sk.tr("Translation")
    , input: My.tr("Input")
    , output: My.tr("Output")
    , name: My.tr("Name")
    , yomi: My.tr("Yomi")
    , suffix: My.tr("Suffix")
    , prefix: My.tr("Prefix")
    , game: Sk.tr("Game")
    , tts: My.tr("TTS")
    , ocr: My.tr("OCR")
    , macro: Sk.tr("Macro")
    , proxy: Sk.tr("Proxy")
  }
  function typeName(type) {
    return _TYPE_NAMES[type] // string -> string
  }

  property variant _CONTEXT_NAMES: {
    scene: My.tr("Dialog")
    , name: My.tr("Name")
    , window: Sk.tr("Window")
    , other: Sk.tr("Other")
  }
  function contextName(ctx) {
    return _CONTEXT_NAMES[ctx] // string -> string
  }

  function hostName(host) { // string -> string
    if (~host.indexOf(',')) {
      var names = []
      var hosts = host.split(',')
      for (var i in hosts)
        names.push(Util.translatorName(hosts[i]) || '(' + hosts[i] + ')')
      return '+ ' + names.join(' + ')
    } else
      return '+ ' + Util.translatorName(host)
  }

  function typeDefaultRole(type) { // string -> string, the same as table.qml
    switch (type) {
    case 'trans':
      return 'x'
    case 'name': case 'yomi': case 'prefix': case 'suffix':
      return 'm'
    //case 'proxy': return 'x'
    }
  }
  function roleName(role) { // string -> string
    switch (role) {
    case 'm': return Sk.tr("Name")
    case 'x': return Sk.tr("Phrase")
    default: return My.tr("User-defined")
    }
  }

  function summary() {
    if (!currentItem)
      return ""

    var pattern = Underscore.escape(currentItem.pattern)
    var text = Underscore.escape(currentItem.text)
    var ruby = Underscore.escape(currentItem.ruby)
    var type = currentItem.type
    var lang = currentItem.language

    var ret = ""
    if (currentItem.errorType != 0)
      ret = Sk.tr("Check") + ": " + errorMessage(currentItem.errorType)

    if (ret)
      ret += "<br/>"
    ret += Sk.tr("Pattern") + ": " + pattern

    ret += "<br/>" + Sk.tr("Priority") + ": "
    if (currentItem.priority) {
      if (currentItem.priority > 0)
        ret += "+"
      ret += currentItem.priority
      var sign = currentItem.priority > pattern.length ? "&gt;" : currentItem.priority < pattern.length ? "&lt;" : "="
      ret += " (" + sign + pattern.length + ")"
    } else
      ret += pattern.length

    ret += "<br/>" + Sk.tr("Translation") + ": "
    if (!text)
      ret += "(" + Sk.tr("Delete") + ")"
    else if (text == pattern)
      ret += "(" + Sk.tr("Not changed") + ")"
    else
      ret += text

    if (ruby)
      ret += "<br/>" + My.tr("Ruby") + ": " + ruby

    if (text) {
      if (type == 'yomi')
        ret += "<br/>" + My.tr("Yomi") + ": " + renderYomiName(pattern, text)
      else if (type == 'name') {
        if (lang == 'en') {
          var t = renderLatinName(text)
          if (t)
            ret += "<br/>" + Sk.tr("Alphabet") + ": " + t
        } else if (lang == 'ru') { // || lang == 'uk') {
          var t = renderCyrillicName(text)
          if (t)
            ret += "<br/>" + Sk.tr("Alphabet") + ": " + t
        }
      }
    }

    if (text && (type == 'trans' || type == 'output' || type == 'name' || type == 'suffix' || type == 'prefix') && lang != 'en' && lang != 'ja')
      ret += "<br/>" + Sk.tr("Romaji") + ": " + jlp_.toroman(text, lang)

    ret += "<br/>" + Sk.tr("Type") + ": " + typeName(currentItem.type)
        + " (" + (Sk.tr(Util.languageName(currentItem.sourceLanguage)) || currentItem.sourceLanguage)
        + " &rArr; " + (Sk.tr(currentItem.language == 'ja' ? "All" : Util.languageName(currentItem.language)) || currentItem.Language)
        + ")"
    if (currentItem.context)
      ret += " #" + contextName(currentItem.context)
    if (currentItem.host)
      ret += " " + hostName(currentItem.host)
    var role = currentItem.role || typeDefaultRole(currentItem.type)
    if (role) {
      ret += " [[" + role + "]]"
      var t = roleName(role)
      if (t)
        ret += "(" + t + ")"
    }

    if (currentItem.gameId > 0)
      ret += "<br/>" + Sk.tr("Game") + ": " + gameSummary(currentItem.gameId)

    var ts = Util.timestampToString(currentItem.timestamp)
    ret += "<br/>" + Sk.tr("Creation") + ": " + renderUser(currentItem.userName) + " (" + ts + ")"
    if (currentItem.comment)
      ret += ": " + renderComment(currentItem.comment)

    if (currentItem.updateUserId) {
      ret += "<br/>"
      ts = Util.timestampToString(currentItem.updateTimestamp)
      ret += Sk.tr("Update") + ": " + renderUser(currentItem.updateUserName) + " (" + ts + ")"
      if (currentItem.updateComment)
        ret += ": " + renderComment(currentItem.updateComment)
    }

    if (pattern && pattern.length < 10) { // && (fr === 'ja' || fr === 'zhs' || fr === 'zht')) {
      var t = jlp_.render_hanzi(pattern)
      if (t)
        ret += '<br/>KanjiDic:<span style="font-family:Tahoma,HanaMinA,HanaMinB">' + t.replace(/\n/g, ', ') + '</span>'
    }

    return ret
  }

  function renderYomiName(pattern, text) { // string, string -> string
    var ret = ''
    for (var i in Util.YOMI_LANGUAGES) {
      var lang = Util.YOMI_LANGUAGES[i]
      if (!isLanguageBlocked(lang)) {
        if (ret)
          ret += ', '
        ret += jlp_.kana2name(text, lang) + ' (' + Sk.tr(lang) +  ')'
      }
    }

    if (!isLanguageBlocked('zh')) {
      if (ret)
        ret += ', '

      if (pattern && jlp_.ja2zh_name_test(pattern)) {
        var s = jlp_.ja2zhs_name(pattern) || Sk.tr("none")
        var t = jlp_.ja2zht_name(pattern) || Sk.tr("none")
        ret += t + ' (' + Sk.tr('zh') +  ')'
        if (s != t)
          ret += ', ' + s + ' (' + Sk.tr('zhs') +  ')'
      } else
        ret += Sk.tr("none") + ' (' + Sk.tr('zh') +  ')'
    }
    return ret
  }

  function renderCyrillicName(text) { // string, string -> string
    var ret = ''
    var fr = 'ru'
    var to = 'uk'
    if (!isLanguageBlocked(to)) {
      var t = jlp_.toalphabet(text, to, fr)
      if (t == text)
        t = '='
      ret += ', ' + t + ' (' + Sk.tr(to) +  ')'
    }
    if (ret)
      ret = text + ' (' + Sk.tr(fr) +  ')' + ret
    return ret
  }

  function renderLatinName(text) { // string -> string
    var ret = ''
    var fr = 'en'
    for (var i in Util.ALPHABET_LANGUAGES) {
      var lang = Util.ALPHABET_LANGUAGES[i]
      if (!isLanguageBlocked(lang))
        ret += ', ' + jlp_.toalphabet(text, lang, fr) + ' (' + Sk.tr(lang) +  ')'
    }
    if (ret)
      ret = text + ' (' + Sk.tr(fr) +  ')' + ret
    return ret
  }

  function gameSummary(id) {
    if (id <= 0)
      return ""
    var itemId = datamanPlugin_.queryGameItemId(id)

    var ret = Sk.tr("File") + "ID: "
            + "<a href=\"javascript://main.searchDictionary(" + id + ",'game')\">" + id + "</a>"
    if (itemId > 0)
      ret = Sk.tr("Game") + "ID: "
          + "<a href=\"javascript://main.searchDictionary(" + itemId + ",'game')\">" + itemId + "</a>"
          + ", " + ret
    ret = "(" + ret + ")"

    var n = datamanPlugin_.queryGameName(id)
    if (!n)
      return ret
    var t = removeRegex(n)
    t = Underscore.escape(t)
    n = Underscore.escape(n)
    n = "<a href=\"javascript://main.searchDictionary('" + t + "','game')\">" + n + "</a>"
    //n = "<a href=\"javascript://main.showGameView(" + id + ")\">" + n + "</a>"
    ret = n + " " + ret

    //if (itemId) // slow to compute
    //  ret += ' <a href="javascript://main.showGameNames(' + itemId + ')">+' + My.tr("Names") + '</a>'

    var s = datamanPlugin_.queryGameSeries(id)
    if (!s)
      return ret
    s = Underscore.escape(s)
    ret = "[<a href=\"javascript://main.searchDictionary('" + s + "','game')\">" + s + "</a>] "
        + ret
    return ret
  }

  function renderUser(name) { // string -> string
    name = Underscore.escape(name)
    return "<a href=\"javascript://main.showUser('" + name + "')\">@" + name + "</a>"
  }

  function renderComment(text) { // string -> string
    text = Underscore.escape(text, '/') // do not escape '/'
    if (~text.indexOf('//')) {
      text = text.replace(/([^:\/])\/\/([^\/])/g, '$1<br/>//$2') // replace // with <br/>//
      text = Linkify.parse(text)
    }
    if (~text.indexOf('@'))
      text = text.replace(/@(\w+)/g,
        "<a href=\"javascript://main.showUser('$1')\">@$1</a>"
      )
    return text
  }

  function removeRegex(t) { // string -> string
    return t.replace(/["'^$,.?+*\[\]\(\){}]/g, ' ')
  }

  function errorMessage(v) { // int -> string
    // Must be consistent with Term error type in dataman.py
    switch (v) {
    case 0:   return "OK"
    case 5:   return qsTr("Language should be Simplified Chinese not Chinese") // W_CHINESE_TRADITIONAL
    case 6:   return qsTr("Language should be Chinese not Simplified Chinese") // W_CHINESE_SIMPLIFIED
    //case 7:   return qsTr("Having Japanese kanji in Chinese translation") // W_CHINESE_KANJI
    case 11:  return qsTr("Pattern or translation is very long") // W_LONG
    case 12:  return qsTr("Pattern is too short") // W_SHORT
    case 20:  return qsTr("Translation is empty") // W_MISSING_TEXT
    case 25:  return qsTr("Translation should not contain Japanese") // W_KANA_TEXT
    case 30:  return qsTr("Game type should not be used for translation") // W_NOT_GAME
    case 31:  return qsTr("Type should not translation instead of input") // W_NOT_INPUT
    case 100: return qsTr("Parentheses or bracks mismatch in regular expression") // W_BAD_REGEX
    case -100: return qsTr("This rule is useless that has no effect") // E_USELESS
    case -101: return qsTr("Pattern does not need enabling regex") // E_USELESS_REGEX
    case -800: return qsTr("Entry type does not allow being translator-specific") // E_BAD_HOST
    case -801: return qsTr("Please use only ASCII characters for translation role") // E_BAD_ROLE
    case -802: return qsTr("Rule type does not support ruby") // E_BAD_RUBY
    case -803: return qsTr("Rule type does not support context") // E_BAD_CONTEXT
    case -900: return qsTr("New line characters are not allowed in text") // E_NEWLINE
    case -901: return qsTr("Tab characters are not allowed in text") // E_TAB
    case -999: return qsTr("Missing translation") // E_EMPTY_TEXT
    case -1000: return qsTr("Missing pattern") // E_EMPTY_PATTERN
    default: return v > 0 ? Sk.tr("Unknown warning") : Sk.tr("Unknown error")
    }
  }
}

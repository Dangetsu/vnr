/** appmodel.qml
 *  9/30/2012 jichi
 *  Model for applets
 *
 *  It should contain either "show" or "run" method.
 */
import QtQuick 1.1
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My

// Translation on property text is not allowed
ListModel {

  // - Private -

//  function qmlrun(fun) {
//    return "\
//import org.sakuradite.reader 1.0 as Plugin; \
//Plugin.MainObjectProxy { \
//  function run() { ${fun}() } \
//} \
//".replace('${fun}', fun)
//  }

  function createLink(fun) { // string ->
    return "javascript://main." + fun + '()'
  }

  /**
   *  Applet properties:
   *  - name: name of the applet
   *  - icon: image of the applet
   *  - toolTip: popup tool tip
   *  - searchText: string used for searching
   *  - link: String to evaluate
   *  - qml: String that could be executed by Qt.createQmlObject
   *  It should contain either "show" or "run" method.
   */


  Component.onCompleted: {

    append({ name: Sk.tr("Software Update")
      , searchText: "Software Update" + "\n" + Sk.tr("Software Update")
      , icon: 'image://rc/app-update'
      , toolTip: My.tr("Check for updates")
      , link: createLink('update')
    })

    //append({ name: Sk.tr("Preferences")
    //  , searchText: "Preferences" + "\n" + Sk.tr("Preferences")
    //  , icon: 'image://rc/dock-prefs'
    //  , toolTip: qsTr("Settings of language, translation, UI, etc")
    //  , link: createLink('showPreferences')
    //})

    //append({ name: My.tr("Game Wizard")
    //  , searchText: "Game Wizard" + "\n" + My.tr("Game Wizard")
    //  , icon: 'image://rc/dock-gamewiz'
    //  , toolTip: qsTr("Add new game step by step")
    //  , link: createLink('showGameWizard')
    //})

    append({ name: My.tr("Shared Dictionary")
      , searchText: "Shared Dictionary" + "\n" + My.tr("Shared Dictionary")
      , icon: 'image://rc/dock-dict'
      , toolTip: qsTr("Shared dictionary for machine translation")
      , link: createLink('showDictionary')
    })

    append({ name: Sk.tr("Machine Translation")
      , searchText: "Machine Translation" + "\n" + Sk.tr("Machine Translation")
      , icon: 'image://rc/dock-mttest'
      , toolTip: My.tr("Test machine translation")
      , link: createLink('showMachineTranslationTester')
    })

    append({ name: My.tr("Japanese Dictionary")
      , searchText: "Japanese Dictionary" + "\n" + Sk.tr("Japanese Dictionary")
      , icon: 'image://rc/dock-jdict'
      , toolTip: qsTr("Japanese word dictionary")
      , link: createLink('showDictionaryTester')
    })

    //append({ name: My.tr("Japanese Syntax Tree")
    //  , searchText: "Japanese Syntax Tree" + "\n" + My.tr("Japanese Syntax Tree")
    //  , icon: 'image://rc/dock-syntax'
    //  , toolTip: My.tr("Test Japanese syntax tree")
    //  , link: createLink('showJapaneseSyntaxTester')
    //})

    //append({ name: My.tr("Speech Recognition")
    //  , searchText: "Speech Recognition" + "\n" + My.tr("Speech Recognition")
    //  , icon: 'image://rc/dock-srtest'
    //  , toolTip: My.tr("Test speech recognition")
    //  , link: createLink('showSpeechRecognitionTester')
    //})

    if (!statusPlugin_.wine)
      append({ name: My.tr("Text Reader") + " (α)" // あるふぁ
      , searchText: "Text Reader" + "\n" + My.tr("Text Reader")
      , icon: 'image://rc/dock-textreader'
      , toolTip: qsTr("Window text translator")
      , link: createLink('showTextReader')
    })

    //append({ name: My.tr("Game Finder") + " (α)" // あるふぁ
    //  , searchText: "Game Finder" + "\n" + My.tr("Game Finder")
    //  , icon: 'image://rc/dock-gamefinder'
    //  , toolTip: qsTr("Searching game information online")
    //  , link: createLink('showGameFinder')
    //})

    //append({ name: My.tr("Game Board")
    //  , searchText: "Game Board" + "\n" + My.tr("Game Board")
    //  , icon: 'image://rc/dock-gameboard'
    //  , toolTip: qsTr("Information of online games")
    //  , link: createLink('showGameBoard')
    //})

    //append({ name: Sk.tr("Regular Expression")
    //  , searchText: "Regular Expression" + "\n" + Sk.tr("Regular Expression")
    //  , icon: 'image://rc/dock-regexp'
    //  , toolTip: My.tr("Test regular expression")
    //  , link: createLink('showRegExpTester')
    //})

    //append({ name: "BBCode"
    //  , searchText: "BBCode"
    //  , icon: 'image://rc/dock-bbcode'
    //  , toolTip: My.tr("Test BBCode")
    //  , link: createLink('showBBCodeTester')
    //})

    //if (!statusPlugin_.wine)
    //  append({ name: My.tr("YouTube Downloader")
    //  , searchText: "YouTube Downloader" + "\n" + My.tr("Download YouTube videos")
    //  , icon: 'image://rc/dock-youtube'
    //  , toolTip: My.tr("Download YouTube videos")
    //  , link: createLink('showYouTubeInput')
    //})

    //append({ name: My.tr("Messages")
    //  , searchText: "Messages" + "\n" + My.tr("Messages")
    //  , icon: 'image://rc/dock-chat'
    //  , toolTip: qsTr("Real-time messages from other users")
    //  , link: createLink('showGlobalChatView')
    //})
  }
}

// EOF

//    append({ name: My.tr("Web Browser") + " (α)" // あるふぁ
//      , searchText: "Web Browser" + "\n" + My.tr("Web Browser")
//      , icon: 'image://rc/dock-browser'
//      , toolTip: qsTr("VNR's built-in web browser")
//      , qml: "\
//import org.sakuradite.reader 1.0 as Plugin; \
//Plugin.MainObjectProxy { \
//  function run() { showWebBrowser() } \
//} \
//"
//    })

/** dock.qml
 *  9/30/2012 jichi
 *  Preferences panel
 *
 *  For unicode characters see:
 *  http://ja.wikipedia.org/wiki/JIS_X_0213非漢字一覧
 *  http://wiki.livedoor.jp/qvarie/d/%A5%E6%A5%CB%A5%B3%A1%BC%A5%C96.0%B0%CA%B9%DF%A4%C7%BB%C8%CD%D1%A4%C7%A4%AD%A4%EB%B3%A8%CA%B8%BB%FA%28%B4%EF%CA%AA%CA%D42%29
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
//import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My

Item {

  property alias growlChecked: growlAct_.checked
  property alias autoHideChecked: autoHideAct_.checked

  function showPopup(x, y) {
    updateSubtitleAct_.enabled = updateCommentAct_.enabled = statusPlugin_.online
    visible = true
    menu_.showPopup(x, y)
    visible = false
  }

  // - Private -

  width: 0; height: 0
  z: -1
  visible: false

  //Plugin.Growl { id: growl_ }
  //Plugin.MainObjectProxy { id: mainPlugin_ }
  //Plugin.SystemStatus { id: statusPlugin_ }
  //Plugin.TextManagerProxy { id: textmanPlugin_ }
  //Plugin.DataManagerProxy { id: datamanPlugin_ }

  Desktop.Menu { id: menu_

    Desktop.MenuItem {
      text: My.tr("Text Settings")
      onTriggered: mainPlugin_.showTextSettings()
    }

    Desktop.MenuItem {
      text: My.tr("Voice Settings")
      onTriggered: mainPlugin_.showVoiceSettings()
    }

    Desktop.MenuItem {
      text: Sk.tr("Preferences")
      onTriggered: mainPlugin_.showPreferences()
    }

    Desktop.Separator {}

    Desktop.MenuItem {
      text: My.tr("Shared Dictionary")
      onTriggered: mainPlugin_.showDictionary()
    }

    Desktop.MenuItem {
      text: My.tr("Japanese Dictionary")
      onTriggered: mainPlugin_.showDictionaryTester()
    }

    Desktop.MenuItem {
      text: My.tr("Test Machine Translation")
      onTriggered: mainPlugin_.showMachineTranslationTester()
    }

    // Temporarily disabled
    //Desktop.MenuItem {
    //  text: My.tr("Test Japanese Syntax")
    //  onTriggered: mainPlugin_.showJapaneseSyntaxTester()
    //}

    //Desktop.MenuItem {
    //  text: My.tr("Speech Recognition")
    //  onTriggered: mainPlugin_.showSpeechRecognitionTester()
    //}

    Desktop.Separator {}

    Desktop.MenuItem {
      text: My.tr("Subtitle Editor")
      onTriggered: mainPlugin_.showSubtitleView()
    }

    Desktop.MenuItem {
      text: My.tr("Subtitle Maker")
      onTriggered: mainPlugin_.showSubtitleMaker()
    }

    Desktop.Separator {}

    Desktop.MenuItem {
      text: Sk.tr("Game Information")
      onTriggered: mainPlugin_.showCurrentGameView()
    }

    //Desktop.MenuItem {
    //  text: My.tr("Game Discussion")
    //  onTriggered: mainPlugin_.showGameDiscussion()
    //}

    Desktop.MenuItem {
      text: My.tr("Spring Board")
      onTriggered: mainPlugin_.showSpringBoard()
    }

    Desktop.MenuItem {
      text: My.tr("Game Board")
      onTriggered: mainPlugin_.showGameBoard()
    }

    Desktop.Separator {}

    //Desktop.MenuItem {
    //  text: qsTr("Edit Subtitles Online")
    //  enabled: statusPlugin_.online
    //  onTriggered: mainPlugin_.liveEdit()
    //}

    //Desktop.MenuItem { id: updateDictionaryAct_
    //  text: My.tr("Update Shared Dictionary")
    //  onTriggered: datamanPlugin_.updateTerms()
    //}

    Desktop.MenuItem { id: updateCommentAct_
      text: My.tr("Update Danmaku")
      onTriggered: textmanPlugin_.reload()
    }

    Desktop.MenuItem { id: updateSubtitleAct_
      text: My.tr("Update Subtitles")
      onTriggered: datamanPlugin_.updateSubtitles()
    }

    //Desktop.MenuItem { id: updateDatabaseAct_
    //  text: My.tr("Update Game Database")
    //  onTriggered: datamanPlugin_.updateGameDatabase()
    //}

    //Desktop.MenuItem {
    //  text: Sk.tr("Statistics")
    //  onTriggered: mainPlugin_.showCommentAnalytics()
    //}

    Desktop.Separator {}

    Desktop.MenuItem { id: growlAct_
      text: Sk.tr("Notification")
      checkable: true
      checked: true
      onTriggered:
        if (checked)
          growl_.show()
    }

    Desktop.MenuItem { id: autoHideAct_
      text: My.tr("Auto Hide")
      checkable: true
      checked: true
    }

    //Desktop.MenuItem {
    //  text: Sk.tr("Help")
    //  onTriggered: mainPlugin_.help()
    //}

    Desktop.MenuItem {
      text: Sk.tr("Restart")
      onTriggered: mainPlugin_.confirmRestart()
    }

    Desktop.MenuItem {
      text: Sk.tr("Quit")
      onTriggered: mainPlugin_.confirmQuit()
    }
  }
}

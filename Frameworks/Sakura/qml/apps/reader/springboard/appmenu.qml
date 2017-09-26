/** springboard.qml
 *  9/29/2012 jichi
 *  SpringBoard root_ element. Rendered within a window.
 *
 *  Hierarchy:
 *  - SpringBoard: root_ rectangle
 *    - Drawer: curtain container
 *      - Curtain: contain panel
 *    - Desktop: dashboard manager
 *      - Dock
 *      - Dashboard: app manager
 *        - Games: galgame
 *        - Applets: utilities
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
//import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My

Item {
  function showPopup(x, y) { menu_.showPopup(x, y) }

  // - Private -

  width: 0; height: 0
  visible: false
  z: -1

  //Plugin.MainObjectProxy { id: mainPlugin_ }
  //Plugin.SystemStatus { id: statusPlugin_ }

  Desktop.Menu { id: menu_

    Desktop.MenuItem {
      text: My.tr("Sync with Running Game")
      //enabled: !statusPlugin_.gameAttached
      onTriggered: mainPlugin_.openRunningGame()
      shortcut: 'Alt+S'
    }
    Desktop.Separator {}
    Desktop.MenuItem {
      text: My.tr("Update Game Database")
      shortcut: 'Alt+U'
      enabled: statusPlugin_.online
      onTriggered: mainPlugin_.confirmUpdateGameDatabase()
    }
    Desktop.MenuItem {
      text: My.tr("Update Shared Dictionary")
      enabled: statusPlugin_.online
      onTriggered: datamanPlugin_.updateTerms()
    }
    //Desktop.MenuItem {
    //  text: My.tr("Update Translation Scripts")
    //  enabled: statusPlugin_.online
    //  onTriggered: datamanPlugin_.updateTranslationScripts()
    //}
    //Desktop.Separator {}
    //Desktop.MenuItem {
    //  text: My.tr("Reload Translation Scripts")
    //  enabled: statusPlugin_.online
    //  onTriggered: datamanPlugin_.reloadTranslationScripts()
    //}
    Desktop.Separator {}
    Desktop.MenuItem {
      text: My.tr("Game Board")
      onTriggered: mainPlugin_.showGameBoard()
      shortcut: 'Alt+F'
    }
    Desktop.MenuItem {
      text: My.tr("Game Wizard")
      onTriggered: mainPlugin_.showGameWizard()
      shortcut: 'Alt+N'
    }
    Desktop.MenuItem {
      text: Sk.tr("Preferences")
      onTriggered: mainPlugin_.showPreferences()
      shortcut: 'Alt+O'
    }
    //Desktop.Separator {}
    //Desktop.MenuItem {
    //  text: My.tr("Test Machine Translation")
    //  onTriggered: mainPlugin_.showMachineTranslationTester()
    //}
    Desktop.Separator {}
    Desktop.MenuItem {
      text: Sk.tr("Check for updates")
      enabled: statusPlugin_.online
      onTriggered: mainPlugin_.checkUpdate()
    }
    //Desktop.MenuItem {
    //  text: Sk.tr("About")
    //  onTriggered: mainPlugin_.about()
    //}
    Desktop.MenuItem {
      text: Sk.tr("About")
      onTriggered: mainPlugin_.about()
    }
    //Desktop.MenuItem {
    //  text: Sk.tr("Credits")
    //  onTriggered: mainPlugin_.showCredits()
    //}
    //Desktop.MenuItem {
    //  text: Sk.tr("Wiki")
    //  onTriggered: mainPlugin_.openWiki('VNR')
    //}
    Desktop.Separator {}
    Desktop.MenuItem {
      text: Sk.tr("Restart")
      onTriggered: mainPlugin_.confirmRestart()
      shortcut: 'Alt+R'
    }
    Desktop.MenuItem {
      text: Sk.tr("Quit")
      onTriggered: mainPlugin_.confirmQuit()
      shortcut: 'Alt+Q'
    }
  }
}

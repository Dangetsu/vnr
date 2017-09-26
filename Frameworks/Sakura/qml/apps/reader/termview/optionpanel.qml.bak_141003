/** optionpanel.qml
 *  9/14/2013 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop

Column { id: root_
  property alias markEnabled: markButton_.checked
  property alias hentaiEnabled: hentaiButton_.checked

  // - Private -

  Desktop.CheckBox { id: markButton_
    text: qsTr("Underline the modified text if possible")
  }

  Desktop.CheckBox { id: hentaiButton_
    text: qsTr("Enable hentai rules for H-scene")
  }
}

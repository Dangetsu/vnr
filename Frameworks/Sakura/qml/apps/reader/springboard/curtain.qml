/** curtain.qml
 *  9/30/2012 jichi
 *  Control panel in the drawer menu.
 */
import QtQuick 1.1
import '.' as SpringBoard // for PrefsPane

Rectangle { id: root_
  color: 'transparent'

  // - Private -

  MouseArea { anchors.fill: parent; hoverEnabled: true } // swallow mouse event

  //Component.onCompleted: console.log("springboard:curtain.qml: pass")

  clip: true // otherwise the curtain will fall out of springboard

  ///  Return the property height of the menubar on the top
  function menuBarHeight() { return Math.min(40, height) }

  Column { id: layout_
    anchors.fill: parent
    z: 1

    // Container for the menubar
    Rectangle{ id: menuBar_
      height: menuBarHeight()
      width: root_.width
      color: 'beige'
      gradient: Gradient {
        GradientStop { position: 0.0;  color: '#8c8f8c' }
        GradientStop { position: 0.17; color: '#6a6d6a' }
        GradientStop { position: 0.77; color: '#3f3f3f' }
        GradientStop { position: 1.0;  color: '#0e1b20' }
      }

      // Menubar title
      Text {
        height: parent.height
        //anchors { right: menuBarContent.left ; verticalCenter: parent.bottom }
        anchors {
          left: parent.left; top: parent.top
          margins: 20
        }
        text: qsTr("Game Launch Settings")
        color: 'snow'
        //font {weight: Font.Light; italic: true}
        //smooth: true
      }

      /*
      Row { id: menuBarContent

        // Menubar buttons -- left for future usage
        anchors.centerIn: parent
        spacing:40

        Ui.TextButton { id: homeButton
          text: qsTr("Home")
          //height: 20; width: 50
          //color : menuListView.currentIndex === 0? buttonColor : Qt.darker(buttonColor, 1.5)
          // on a button click, change the list's currently selected item to FileMenu
          onClicked: menuListView.currentIndex = 0
        }
        Ui.TextButton { id: advanceButton
          text: qsTr("Advance")
          height: 20; width: 50
          //color : menuListView.currentIndex === 1?  Qt.darker(buttonColor, 1.5) : Qt.darker(buttonColor, 1.9)
          // on a button click, change the list's currently selected item to EditMenu
          onClicked: menuListView.currentIndex = 1
        }
      }
      */
    }

    // List view will display a model according to a delegate
    ListView { id: menuListView
      width: root_.width
      contentWidth: width
      height: Math.max(0, root_.height - menuBarHeight())

      //the model contains the data
      model: menuListModel_

      //control the movement of the menu switching
      snapMode: ListView.SnapOneItem
      orientation: ListView.Horizontal
      boundsBehavior: Flickable.StopAtBounds
      flickDeceleration: 5000
      highlightFollowsCurrentItem: true
      highlightMoveDuration:240
      highlightRangeMode: ListView.StrictlyEnforceRange
    }
  }

  // A list of visual items already have delegates handling their display
  VisualItemModel { id: menuListModel_
    // Advanced, as a place holder for future usage
    SpringBoard.PrefsPane { anchors.fill: parent }
  }
}

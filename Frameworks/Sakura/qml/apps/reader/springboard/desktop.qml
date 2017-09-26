/** desktop.qml
 *  9/29/2012 jichi
 *  Dashboard manager
 */
import QtQuick 1.1
import '../../../components' as Components // for ScrollBar
import '../share' as Share

Item { id: root_

  property alias backgroundSource: background_.source   ///< dashboard background
  property alias backgroundSize: background_.sourceSize

  property alias foregroundSource: foreground_.source   ///< dashboard foreground
  property alias foregroundSize: foreground_.sourceSize

  //property alias cornerSource: corner_.source   ///< dashboard corner
  //property alias cornerSize: corner_.sourceSize

  property int topMargin: 0      ///< background margin
  property alias currentIndex: dashboard_.currentIndex  ///< desktop index

  /**
   *  @brief  By default, self.children will become dashboard items.
   *
   *  Child should be descendant of Item, and has icon property
   */
  property alias model: dashboard_.model

  // - Private -

  //Component.onCompleted: console.log("springboard:desktop.qml: pass")

  // Background image
  Image { id: background_
    //fillMode: Image.PreserveAspectCrop
    //fillMode: Image.PreserveAspectFit
    //fillMode: Image.Stretch
    anchors.fill: parent
    anchors.leftMargin: - root_.topMargin - dashboard_.contentX / 4 // div to make it moving slower, -100: margin
    fillMode: Image.Tile
    width: Math.max(dashboard_.contentWidth, root_.width)

    visible: !!source
    z: -10

    //asynchronous: Util.startsWith(source, 'http')
    asynchronous: false  // async iff source is the Internet
  }

  // Background image
  //Image { id: foreground_
  //  anchors.fill: parent
  //  fillMode: Image.Tile
  //  visible: !!source
  //  z: -1
  //  asynchronous: false  // only load local source file, or it might cause loop binding issue
  //}
  Share.FadingImage { id: foreground_
    anchors.fill: parent
    //anchors.leftMargin: -dashboard_.contentX/2 // div to make it moving slower, -100: margin
    anchors.leftMargin: -dashboard_.contentX // div to make it moving slower, -100: margin
    fillMode: Image.Tile
    z: -1
    asynchronous: false  // only load local source file, or it might cause loop binding issue
    visible: settingsPlugin_.springBoardSlidesEnabled
  }

  // Dashboard view
  ListView { id: dashboard_
    anchors.fill: parent

    //currentIndex: 0
    //onCurrentIndexChanged: root_.currentIndex = currentIndex

    orientation: Qt.Horizontal
    boundsBehavior: Flickable.DragOverBounds

    highlightRangeMode: ListView.StrictlyEnforceRange
    snapMode: ListView.SnapOneItem

    // Only show the scrollbars when the view is moving.
    states: State {
      when: dashboard_.movingHorizontally //|| dashboard_.movingVertically
      PropertyChanges { target: horizontalScrollBar_; opacity: 1 }
      //PropertyChanges { target: verticalScrollBar_; opacity: 1 }
    }

    transitions: Transition {
      NumberAnimation { property: 'opacity'; duration: 400 }
    }
  }

  Components.ScrollBar { id: horizontalScrollBar_
    width: Math.max(0, dashboard_.width - 12)
    height: 12
    anchors.top: dashboard_.top
    anchors.horizontalCenter: dashboard_.horizontalCenter
    opacity: 0
    orientation: Qt.Horizontal
    position: dashboard_.visibleArea.xPosition
    pageSize: dashboard_.visibleArea.widthRatio
  }

  //Components.ScrollBar { id: verticalScrollBar_
  //  width: 12
  //  height: Math.max(0, dashboard_.height - 12)
  //  anchors.right: dashboard_.right
  //  anchors.verticalCenter: dashboard_.verticalCenter
  //  opacity: 0
  //  orientation: Qt.Vertical
  //  position: dashboard_.visibleArea.yPosition
  //  pageSize: dashboard_.visibleArea.heightRatio
  //}
}

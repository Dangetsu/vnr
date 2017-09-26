/** floatingrectangle.qml
 *  12/13/2013 jichi
 *  Draggable and closable container
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import '.' as Share

Rectangle { id: root_

  property alias toolTip: tip_.text
  property alias hover: tip_.containsMouse
  property alias drag: mouse_.drag

  // - Private -

  MouseArea { id: mouse_
    anchors.fill: parent
    acceptedButtons: Qt.LeftButton
    drag.target: root_; drag.axis: Drag.XandYAxis
  }

  Desktop.TooltipArea { id: tip_
    anchors.fill: parent
  }

  Share.CloseButton { id: closeButton_
    anchors { left: parent.left; top: parent.top; margins: -9 }
    onClicked: parent.visible = false
    //visible: hover || tip_.containsMouse // this will make it difficult to close
  }
}

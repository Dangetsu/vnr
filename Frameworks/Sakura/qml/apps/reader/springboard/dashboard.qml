/** dashboard.qml
 *  9/29/2012 jichi
 *  App manager
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import '../../../js/eval.min.js' as Eval
import '../../../components' as Components
import '../share' as Share

Item { id: root_
  property alias model: grid_.model   ///< dashboard model
  property alias currentIndex: grid_.currentIndex

  //property string searchText: ""
  //property variant searchRe: new RegExp(searchText, 'i')
  property bool highlight: false

  //signal contextMenuAt(int x, int y)

  // - Private -
  //Component.onCompleted: console.log("springboard:dashboard.qml: pass")

  //function evalQml(qml, owner) { // string, item ->
  //  if (qml) {
  //    var q = Qt.createQmlObject(qml, owner ? owner : root_, 'runDashboardApp')
  //    if (q !== null) { // && 'run' in q) {
  //      console.log('dashboard.qml:evalQml: running')
  //      q.run()
  //      console.log('dashboard.qml:evalQml: destroying')
  //      q.destroy()
  //      console.log('dashboard.qml:evalQml: pass')
  //    }
  //  }
  //}

  //function evalModel(model) { // dict ->
  //  var qml = model.qml
  //  if (qml) {
  //    evalQml(qml, owner)
  //    return
  //  }
  //  var link = model.link
  //  if (link)
  //    Eval.evalLink(link)
  //}

  GridView { id: grid_
    anchors.fill: parent
    cellWidth: 100; cellHeight: 100
    focus: true
    //model: 12 // 12 items, just as a place holder

    //KeyNavigation.down: listMenu
    //KeyNavigation.left: contextMenu

    //onCountChanged:
    //  if (currentIndex >= count)
    //    currentIndex = count ? 1 : 0

    Keys.onPressed: {
      // ENTER
      if ((event.key === Qt.Key_Return || event.key === Qt.Key_Enter) &&
          !event.modifiers) {
        event.accepted = true
        var modelData = grid_.model.get(grid_.currentIndex)
        if (modelData)
          Eval.evalLink(modelData.link)
      }
    }

    footer: Item { width: 1; height: 150 } // vertical place holder

    delegate: Item { id: delegateItem_
      width: GridView.view.cellWidth
      height: GridView.view.cellHeight

      // No effect
      // Behavior on x { SmoothedAnimation { velocity: 640 } }
      // Behavior on y { SmoothedAnimation { velocity: 480 } }

      //property bool matched: !!root_.searchText && searchRe.test(model.searchText)

      //opacity: (!root_.searchText || matched) ? 1.0 : 0.2
      //visible: !root_.searchText || matched

      //property bool selected: GridView.view.currentIndex === index

      function focusMe() {
        GridView.view.currentIndex = index
        forceActiveFocus()
      }

      Rectangle { id: content_
        color: 'transparent'
        smooth: true
        anchors.fill: parent; anchors.margins: 20
        //radius: 10 // change to flat style

        // Outline
        Rectangle {
          anchors { fill: parent; margins: 1 }
          opacity: 0.4
          smooth: true
          //radius: 8 // change to flat style

          color: {
            // http://www.tayloredmktg.com/rgb/
            switch (model.styleHint) {
            case 'junai': return '#3073b6'  // blue
            case 'nuki': return '#9370db'   // median purple
            case 'otome': return '#98fb98'  // pale green
            default: return '#91aa9d'       // white
            }
          }
        }
        Image {
          anchors.centerIn: parent
          smooth: true
          sourceSize.width: 48; sourceSize.height: 48
          source: model.icon ? model.icon : '' //'image://rc/game'
        }
      }

      Text { id: label
        anchors {
          bottom: parent.bottom
          left: parent.left; right: parent.right
          //margins: 2
        }
        horizontalAlignment: Text.AlignHCenter
        text: model.name // model property
        color: 'snow'
        //style: Text.Raised; styleColor: 'lightblue'
        wrapMode: Text.Wrap
        //font.pixelSize: 18; font.bold: true
        font.bold: true

        effect: Share.TextEffect {
          highlight: delegateItem_.activeFocus //|| delegateItem_.matched
        }
      }

      property bool active: delegateItem_.activeFocus || root_.highlight
      states: [
        State { when: !active
          PropertyChanges { target: content_; scale: 1.0; color: 'transparent' }
        }
        , State { when: active
          PropertyChanges { target: content_; scale: 1.1; color: '#fcfff5' }
        }
      ]

      transitions: Transition {
        ParallelAnimation {
          ColorAnimation {}
          //NumberAnimation { property: 'scale'; duration: 100 }
          SpringAnimation {
            property: 'scale'; duration: 100
            spring: 5.0; damping: 0.05 // spring: strength; damping: speed
          }
        }
      }

      MouseArea {
        anchors.fill: parent
        acceptedButtons: Qt.LeftButton //|Qt.MiddleButton|Qt.RightButton

        onClicked:
          delegateItem_.focusMe()
          //if (mouse.button === Qt.RightButton) {
          //  var gp = mapToItem(null, x + mouse.x, y + mouse.y)
          //  root_.contextMenuAt(gp.x, gp.y)
          //}

        onDoubleClicked: {
          delegateItem_.focusMe() // ensure focus for double click
          if (mouse.button === Qt.LeftButton)
            Eval.evalLink(model.link)
            //evalModel(model, delegateItem_)
        }
      }

      Desktop.TooltipArea {
        // Note this will eat hover events
        anchors.fill: parent
        text: model.toolTip
      }
    }

    // Only show the scrollbars when the view is moving.
    states: State {
      when: grid_.movingVertically //|| grid_.movingHorizontally
      PropertyChanges { target: verticalScrollBar_; opacity: 1 }
      //PropertyChanges { target: horizontalScrollBar_; opacity: 1 }
    }

    transitions: Transition {
      NumberAnimation { property: 'opacity'; duration: 400 }
    }
  }

  Components.ScrollBar { id: verticalScrollBar_
    width: 12
    height: Math.max(0, grid_.height - 12)
    anchors.right: grid_.right
    anchors.verticalCenter: grid_.verticalCenter
    opacity: 0
    orientation: Qt.Vertical
    position: grid_.visibleArea.yPosition
    pageSize: grid_.visibleArea.heightRatio
  }

  //Components.ScrollBar { id: horizontalScrollBar_
  //  width: Math.max(0, grid_.width - 12)
  //  height: 12
  //  anchors.bottom: grid_.bottom
  //  anchors.horizontalCenter: grid_.horizontalCenter
  //  opacity: 0
  //  orientation: Qt.Horizontal
  //  position: grid_.visibleArea.xPosition
  //  pageSize: grid_.visibleArea.widthRatio
  //}
}

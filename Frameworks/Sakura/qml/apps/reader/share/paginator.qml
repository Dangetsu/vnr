/** paginator.qml
 *  5/25/2014 jichi
 */
import QtQuick 1.1
//import QtDesktop 0.1 as Desktop
import '../../../js/sakurakit.min.js' as Sk
import '../../../components/bootstrap3' as Bootstrap
import '.' as Share

Item { id: root_

  property alias value: spin_.intValue
  property alias maximumValue: spin_.maximumValue

  //property string buttonStyle: 'btn btn-default'
  property string buttonStyleClass: 'btn btn-inverse'
  //property string buttonStyleClass: 'btn btn-success'

  // - Private -

  implicitWidth: 150
  implicitHeight: spin_.height

  //property int cellWidth: 20
  //property int cellHeight: 18
  //property int pixelSize: 10

  Bootstrap.Button { id: firstPageButton_
    anchors {
      verticalCenter: parent.verticalCenter
      left: parent.left
    }
    //width: parent.cellWidth
    //font.pixelSize: parent.pixelSize
    styleClass: root_.buttonStyleClass
    text: "|<"
    //toolTip: Sk.tr("Previous")
    //font.bold: true
    //font.family: 'YouYuan'
    scale: 0.8
    width: height

    onClicked: spin_.intValue = spin_.minimumValue
  }

  Bootstrap.Button { id: previousPageButton_
    anchors {
      verticalCenter: parent.verticalCenter
      left: firstPageButton_.right
    }
    //width: parent.cellWidth
    //font.pixelSize: parent.pixelSize
    styleClass: root_.buttonStyleClass
    text: "<"
    toolTip: Sk.tr("Previous")
    //font.bold: true
    //font.family: 'YouYuan'
    scale: 0.8
    width: height

    onClicked:
      if (spin_.intValue > spin_.minimumValue)
        --spin_.intValue
  }

  Share.IntSpinBox { id: spin_
    anchors {
      verticalCenter: parent.verticalCenter
      left: previousPageButton_.right
      right: nextPageButton_.left
      leftMargin: 2
    }

    height: 20
    minimumValue: maximumValue > 0 ? 1 : 0

    postfix: '/' + maximumValue
    topMargin: 4 // input is too high
  }

  Bootstrap.Button { id: nextPageButton_
    anchors {
      verticalCenter: parent.verticalCenter
      right: lastPageButton_.left
    }
    //width: parent.cellWidth
    //font.pixelSize: parent.pixelSize
    styleClass: root_.buttonStyleClass
    text: ">"
    toolTip: Sk.tr("Next")
    //font.bold: true
    //font.family: 'YouYuan'
    scale: 0.8
    width: height

    onClicked:
      if (spin_.intValue < spin_.maximumValue)
        ++spin_.intValue
  }

  Bootstrap.Button { id: lastPageButton_
    anchors {
      verticalCenter: parent.verticalCenter
      right: parent.right
    }
    //width: parent.cellWidth
    //font.pixelSize: parent.pixelSize
    styleClass: root_.buttonStyleClass
    text: ">|"
    //toolTip: Sk.tr("Previous")
    //font.bold: true
    //font.family: 'YouYuan'
    scale: 0.8
    width: height

    onClicked: spin_.intValue = spin_.maximumValue
  }
}

// EOF

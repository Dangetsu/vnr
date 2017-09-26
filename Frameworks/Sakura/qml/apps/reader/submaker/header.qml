/** header.qml
 *  6/6/2013 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../js/util.min.js' as Util
import '../../../components/bootstrap3' as Bootstrap

Item { id: root_

  property alias spellChecked: spellButton_.checked
  property alias highlightChecked: highlightButton_.checked
  property alias copyChecked: copyButton_.checked

  // - Private -

  height: 40

  //gradient: Gradient {
  //  //GradientStop { position: 0.0;  color: '#8c8f8c' }
  //  //GradientStop { position: 0.17; color: '#6a6d6a' }
  //  //GradientStop { position: 0.77; color: '#3f3f3f' }
  //  //GradientStop { position: 1.0;  color: '#6a6d6a' }
  //  GradientStop { position: 0.17; color: '#dfdfe3' }
  //  GradientStop { position: 0.77; color: '#f1f1f3' }
  //  GradientStop { position: 1.0;  color: '#f0f0f3' }
  //}
  //color: '#ced0d6'

  //Image {
  //  anchors.fill: parent
  //  fillMode: Image.Tile
  //  source: 'image://rc/texture-black'
  //  //z: -1
  //}

  Plugin.MainObjectProxy { id: main_ }

  // - Left -

  //Desktop.CheckBox { id: spellButton_
  //  anchors {
  //    verticalCenter: parent.verticalCenter
  //    left: parent.left
  //    leftMargin: 9
  //  }
  //  text: ' ' + Sk.tr("Spell check")
  //  width: 85
  //  //tooltip: qsTr("Mark mistyped words")  // tooltip does not exist for Desktop.ComboBox
  //}

  property int _MARGIN: 10
  property int _BUTTON_WIDTH: 60

  // - Left -

  Desktop.CheckBox { id: spellButton_
    anchors {
      verticalCenter: parent.verticalCenter
      left: parent.left
      leftMargin: _MARGIN
    }
    text: ' ' + Sk.tr("Spell check")
    width: 90
    //tooltip: tooltip does not exist for Desktop.ComboBox
  }

  Desktop.CheckBox { id: highlightButton_
    anchors {
      verticalCenter: parent.verticalCenter
      left: spellButton_.right
      leftMargin: _MARGIN
    }
    text: ' ' + qsTr("Highlight headers")
    width: 125
    //tooltip: tooltip does not exist for Desktop.ComboBox
  }

  Desktop.CheckBox { id: copyButton_
    anchors {
      verticalCenter: parent.verticalCenter
      left: highlightButton_.right
      leftMargin: _MARGIN
    }
    text: ' ' + qsTr("Copy selected text")
    width: 130
    //tooltip: tooltip does not exist for Desktop.ComboBox
  }

  // - Right -

  Bootstrap.Button { id: testButton_
    anchors {
      verticalCenter: parent.verticalCenter
      right: editButton_.left
      rightMargin: _MARGIN
    }
    width: _BUTTON_WIDTH
    styleClass: 'btn btn-default'
    text: Sk.tr("Test")
    toolTip: My.tr("Test BBCode")
    onClicked: main_.showBBCodeTester()
  }

  Bootstrap.Button { id: editButton_
    anchors {
      verticalCenter: parent.verticalCenter
      right: helpButton_.left
      rightMargin: _MARGIN
    }
    width: _BUTTON_WIDTH
    styleClass: 'btn btn-default'
    text: Sk.tr("Search")
    toolTip: My.tr("Subtitle editor")
    onClicked: main_.showSubtitleView()
  }

  Bootstrap.Button { id: helpButton_
    anchors {
      verticalCenter: parent.verticalCenter
      right: parent.right
      rightMargin: _MARGIN
    }
    width: _BUTTON_WIDTH
    styleClass: 'btn btn-success'
    text: Sk.tr("Help")
    toolTip: Sk.tr("Help")
    onClicked: main_.showCommentHelp()
  }
}

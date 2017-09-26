/** submaker.qml
 *  12/3/2012 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import org.sakuradite.reader 1.0 as Plugin
import '../../imports/qmlhelper' as Helper
import '../../js/reader.min.js' as My
import '../../js/util.min.js' as Util
import 'share' as Share
import 'submaker' as SubMaker

Share.View { id: root_
  //implicitWidth: 480; implicitHeight: 360
  width: 720; height: 560

  // Window properties
  property string windowTitle: My.tr("Subtitle Maker") ///< window title
  //property string windowIconSource: 'window-submaker'
  property bool windowVisible: false ///< if the container window is visible

  // - Private -

  //gradient: Gradient {
  //  GradientStop { position: 0.0;  color: '#8c8f8c' }
  //  GradientStop { position: 0.17; color: '#6a6d6a' }
  //  GradientStop { position: 0.77; color: '#3f3f3f' }
  //  GradientStop { position: 1.0;  color: '#6a6d6a' }
  //}

  Component.onCompleted: {
    loadSettings()
    qApp.aboutToQuit.connect(saveSettings)
    console.log("submaker.qml: pass")
  }

  Component.onDestruction: console.log("submaker.qml:destroy: pass")

  function loadSettings() {
    //dock_.textChecked = settings_.graffitiTextVisible
    //dock_.translationChecked = settings_.graffitiTranslationVisible
    //dock_.subtitleChecked = settings_.graffitiSubtitleVisible
    //dock_.commentChecked = settings_.graffitiCommentVisible
    ////dock_.spellChecked = settings_.graffitiSpellCheck
    ////dock_.groupChecked = settings_.graffitiGroupEnabled

    header_.copyChecked = settings_.graffitiCopyEnabled
    header_.highlightChecked = settings_.graffitiHeaderVisible
    header_.spellChecked = settings_.inputSpellCheck

    footer_.lockChecked = settings_.inputLocked
    footer_.returnChecked = settings_.inputAcceptsReturn
    footer_.shiftReturnChecked = settings_.inputAcceptsShiftReturn
    //console.log("submaker.qml:loadSettings: pass")
  }

  function saveSettings() {
    //settings_.graffitiTextVisible = dock_.textChecked
    //settings_.graffitiTranslationVisible = dock_.translationChecked
    //settings_.graffitiSubtitleVisible = dock_.subtitleChecked
    //settings_.graffitiCommentVisible = dock_.commentChecked
    ////settings_.graffitiSpellCheck = dock_.spellChecked
    ////settings_.graffitiGroupEnabled = dock_.groupChecked

    settings_.graffitiCopyEnabled = header_.copyChecked
    settings_.graffitiHeaderVisible = header_.highlightChecked
    settings_.inputSpellCheck = header_.spellChecked

    settings_.inputLocked = footer_.lockChecked
    settings_.inputAcceptsReturn = footer_.returnChecked
    settings_.inputAcceptsShiftReturn = footer_.shiftReturnChecked
    //console.log("submaker.qml:saveSettings: pass")
  }

  Helper.QmlHelper { id: qmlhelper_ }

  Plugin.Settings { id: settings_ }

  Plugin.MainObjectProxy { id: mainPlugin_ }

  Plugin.SystemStatus { id: status_ }
  property bool canLock: status_.online && !!status_.userId && status_.userId !== 4

  Desktop.SplitterColumn {
    anchors.fill: parent

    Item { // top area
      anchors {
        left: parent.left; right: parent.right
        top: parent.top
      }

      //height: Math.max(300, graffiti_.height + searchBox_.height)
      //height: 300
      Desktop.Splitter.expanding: true

      SubMaker.Header { id: header_
        anchors {
          left: parent.left; right: parent.right
          top: parent.top
        }
      }

      SubMaker.Graffiti { id: graffiti_
        anchors {
          left: parent.left; right: parent.right
          top: header_.bottom
          bottom: searchBox_.top
        }

        enabled: root_.windowVisible

        textVisible: true //dock_.textChecked
        translationVisible: true //dock_.translationChecked
        subtitleVisible: true //dock_.subtitleChecked
        commentVisible: true //dock_.commentChecked
        copyEnabled: header_.copyChecked
        spellCheckEnabled: header_.spellChecked
        //groupEnabled: true //dock_.groupChecked
        headerVisible: header_.highlightChecked

        //function setSearchText(t) {
        //  if (!isModelConnected())
        //    searchText = t
        //  else {
        //    disconnectModel()
        //    searchText = t
        //    connectModel()
        //  }
        //}

        //searchText: Util.trim(searchBox_.text)

        //SubMaker.Dock { id: dock_
        //  anchors {
        //    verticalCenter: parent.verticalCenter
        //    left: parent.left
        //  }
        //  z: 9999 // make sure always on top

        //  //allButtonEnabled: !graffiti_.allCommentsVisible

        //  //onClearButtonClicked: graffiti_.clear()
        //  //onAllButtonClicked: graffiti_.showAllComments()
        //  //onAnalyticsButtonClicked: main_.showCommentAnalytics()
        //  //onCreditsButtonClicked: main_.showCommentCredits()

        //  onUpButtonClicked: graffiti_.scrollBeginning()
        //  onDownButtonClicked: graffiti_.scrollEnd()
        //}
      }

      Share.SearchBox { id: searchBox_
        anchors {
          left: parent.left; right: parent.right
          bottom: parent.bottom
          bottomMargin: -2
        }
        totalCount: graffiti_.count
        currentCount: graffiti_.searchText ? graffiti_.visibleCount() : totalCount
        toolTip: qsTr("Type part of text, user, language, date, etc.")

        onTextChanged: graffiti_.searchText = Util.trim(text)
        //onAccepted: graffiti_.searchText = Util.trim(text)
      }
    }

    Item { // middle area
      anchors {
        left: parent.left; right: parent.right
        bottom: bottomItem_.top
      }

      //height: subEdit_.height + footer_.height
      height: 120
      Desktop.Splitter.expanding: false

      visible: status_.online && status_.login

      SubMaker.SubEdit { id: subEdit_
        anchors {
          left: parent.left; right: parent.right
          top: parent.top
          bottom: footer_.top
        }
        height: 100

        acceptsReturn: footer_.returnChecked
        acceptsShiftReturn: footer_.shiftReturnChecked
        submitType: footer_.selectedType
        spellCheckEnabled: header_.spellChecked
        lockComments: footer_.lockChecked && root_.canLock
        //popupEnabled: footer_.popupChecked

        // FIXME: mysterious binding loop warning
        //Component.onCompleted:
        //console.log("kagami.qml:CommentBar: binding loop warning ignored")
      }

      SubMaker.Footer { id: footer_
        anchors {
          left: parent.left; right: parent.right
          bottom: parent.bottom
        }
        onSubmitClicked: subEdit_.submit()

        //Component.onCompleted:
        //  tagTriggered.connect(subEdit_.addTag)
      }
    }

    Item { id: bottomItem_
      anchors {
        left: parent.left; right: parent.right
        bottom: parent.bottom
      }

      height: 120
      Desktop.Splitter.expanding: false

      SubMaker.ContextEdit { id: contextEdit_
        anchors.fill: parent
      }
    }
  }
}

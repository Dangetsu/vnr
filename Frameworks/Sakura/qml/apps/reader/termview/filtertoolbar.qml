/** filtertoolbar.qml
 *  2/20/2013 jichi
 */
import QtQuick 1.1
//import QtDesktop 0.1 as Desktop
import '../../../js/sakurakit.min.js' as Sk
import '../../../js/reader.min.js' as My
import '../../../components/bootstrap3' as Bootstrap

Grid { id: root_ // Theme refers to Bootstrap.label

  property string values // types split by ','

  // - Private -
  rows: 4 // 4 * 4
  spacing: 2

  onValuesChanged: console.log("filtertoolbar.qml: values =", values)

  Component.onCompleted: {
    var l = [
        {value:'trans', text:qsTr("Trans"),     toolTip:qsTr("Replace text matching pattern with translation")}
      , {value:'output', text:My.tr("Output"),  toolTip:qsTr("Fix output text after translation")}
      , {value:'input', text:My.tr("Input"),    toolTip:qsTr("Fix input text before translation")}
      , {width:1, height:1} // empty item

      , {value:'name',   text:My.tr("Name"),    toolTip:qsTr("A Japanese first or last name")}
      , {value:'yomi',   text:My.tr("Yomi"),    toolTip:qsTr("Yomigana of a Japanese name")}
      , {value:'suffix', text:My.tr("Suffix"),  toolTip:qsTr("Title after a Japanese name")}
      , {value:'prefix', text:My.tr("Prefix"),  toolTip:qsTr("Title before a Japanese name")}

      , {value:'macro',  text:Sk.tr("Macro"),   toolTip:qsTr("Reusable regular expression")}
      , {value:'proxy',  text:Sk.tr("Proxy"),   toolTip:qsTr("Delegate translation roles")}
      , {width:1, height:1} // empty item
      , {width:1, height:1} // empty item

      , {value:'game', text:Sk.tr("Game"),      toolTip:qsTr("Fix game text")}
      , {width:1, height:1} // empty item
      , {value:'tts', text:"TTS",               toolTip:qsTr("Fix text to send to TTS")}
      , {value:'ocr',    text:"OCR",            toolTip:qsTr("Fix text received from OCR")}
    ]
    for (var i in l)
      buttonComp_.createObject(root_, l[i])
  }

  function toggleValue(value, checked) { // string, bool
    var s = root_.values
    if (checked) {
      if (s)
        s += ','
      s += value
    } else
      s = s.replace(value, '') // assume types are not included by others
           .replace(',,', ',')
           .replace(/^,/, '')
           .replace(/,$/, '')
    root_.values = s
  }

  Component { id: buttonComp_
    Bootstrap.Button {
      width: 45; height: 18
      styleClass: checked ? 'btn btn-success' : 'btn btn-default'
      checkable: true
      property string value
      onClicked: root_.toggleValue(value, checked)
    }
  }
}

// EOF

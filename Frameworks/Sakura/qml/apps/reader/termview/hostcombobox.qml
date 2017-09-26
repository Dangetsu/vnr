/** hostcombobox.qml
 *  2/7/2015 jichi
 */
import QtQuick 1.1
import '../../../components/desktopex' as DesktopEx
import '../../../js/reader.min.js' as My
import '.' as TermView

DesktopEx.MultiComboBox { id: root_

  property string selectedValue

  // - Private -
  TermView.HostMenuItem { id: i1; value: 'bing' }
  TermView.HostMenuItem { id: i2; value: 'google' }
  TermView.HostMenuItem { id: i3; value: 'babylon' }
  TermView.HostMenuItem { id: i4; value: 'lecol' }
  TermView.HostMenuItem { id: i5; value: 'infoseek' }
  TermView.HostMenuItem { id: i6; value: 'excite' }
  TermView.HostMenuItem { id: i7; value: 'nifty' }
  TermView.HostMenuItem { id: i8; value: 'systran' }
  TermView.HostMenuItem { id: i9; value: 'transru' }
  TermView.HostMenuItem { id: i10; value: 'naver' }
  TermView.HostMenuItem { id: i11; value: 'baidu' }
  TermView.HostMenuItem { id: i12; value: 'youdao' }
  TermView.HostMenuItem { id: i13; value: 'jbeijing' }
  TermView.HostMenuItem { id: i14; value: 'fastait' }
  TermView.HostMenuItem { id: i15; value: 'dreye' }
  TermView.HostMenuItem { id: i16; value: 'eztrans' }
  TermView.HostMenuItem { id: i17; value: 'transcat' }
  TermView.HostMenuItem { id: i18; value: 'atlas' }
  TermView.HostMenuItem { id: i19; value: 'lec' }
  TermView.HostMenuItem { id: i20; value: 'hanviet' }
  TermView.HostMenuItem { id: i21; value: 'vtrans' }

  menuItems: [i1, i2, i3, i4, i5, i6, i7, i8, i9, i10, i11, i12, i13, i14, i15, i16, i17, i18, i19, i20, i21]

  property string valueSep: ','

  placeholderText: "*"
  separator: "+"

  tooltip: My.tr("Translator")

  prefix: ~selectedValue.indexOf(valueSep) ? "+" : ""

  Component.onCompleted: if (selectedValue) {
    if (~selectedValue.indexOf(',')) {
      var l = selectedValue.split(valueSep)
      for (var i in menuItems) {
        var item = menuItems[i]
        if (~l.indexOf(item.value))
          item.checked = true
      }
    } else
      for (var i in menuItems) {
        var item = menuItems[i]
        if (item.value == selectedValue)
          item.checked = true
      }
  }

  //onSelectedValueChanged: // not implemented as not needed

  onSelectionChanged: updateSelectedValue()

  function updateSelectedValue() {
    var l = []
    for (var i in menuItems) {
      var item = menuItems[i]
      if (item.checked)
        l.push(item.value)
    }
    selectedValue = l.join(valueSep)
  }
}

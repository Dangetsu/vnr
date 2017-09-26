// multicombobox.qml
// 2/7/2015 jichi
// Modified from QtDesktop.ComboBox to support multiple selection.
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import '../../../../Qt/imports/QtDesktop/custom' as DesktopCustom
import '.' as DesktopEx

DesktopCustom.BasicButton { id: root_
  property alias menuItems: popup_.items

  property alias selectedText: popup_.selectedText
  property alias separator: popup_.separator

  property string placeholderText: "-"
  property string prefix
  property string suffix

  signal selectionChanged

  //property alias selectedItems: popup_.selectedItems // not used

  property alias popupOpen: popup_.visible

  // - Private -

  default property alias defaultMenuItems_: popup_.menuItems

  background: Desktop.StyleItem {
    anchors.fill: parent
    elementType: "combobox"
    sunken: root_.pressed
    raised: !sunken
    hover: root_.containsMouse
    enabled: root_.enabled
    text: root_.selectedText ? root_.prefix + root_.selectedText + root_.suffix : root_.placeholderText
    hasFocus: root_.focus
    contentHeight: 18
  }

  width: implicitWidth
  height: implicitHeight

  implicitWidth: Math.max(80, backgroundItem.implicitWidth)
  implicitHeight: backgroundItem.implicitHeight

  onWidthChanged: popup_.setMinimumWidth(width)
  checkable: false

  onPressedChanged: if (pressed) popup_.visible = true

  DesktopEx.MultiContextMenu { id: popup_
    property bool center: backgroundItem.styleHint("comboboxpopup")
    centerSelectedText: center
    y: center ? 0 : root_.height

    onSelectionChanged: root_.selectionChanged()
  }

  // The key bindings below will only be in use when popup is
  // not visible. Otherwise, native popup key handling will take place:
  //Keys.onUpPressed: { if (selectedIndex < model.count - 1) selectedIndex++ }
  //Keys.onDownPressed: { if (selectedIndex > 0) selectedIndex-- }

  Keys.onSpacePressed: { root_.popupOpen = !root_.popupOpen }
}

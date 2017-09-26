/** prefspane.qml
 *  11/19/2012 jichi
 */
import QtQuick 1.1
//import org.sakuradite.reader 1.0 as Plugin
import '.' as SpringBoard

Rectangle {
  color: '#343434'
  Image { source: 'image://rc/stripes'; fillMode: Image.Tile; anchors.fill: parent; opacity: 0.3 }

  //Plugin.Settings { id: settings_ }

  Column { id: layout_
    anchors.fill: parent
    property int cellHeight: 70
    property int fontSize: 20 // pixelSize

    //SpringBoard.SwitchButton { // App locale
    //  checked: settings_.applocEnabled
    //  onCheckedChanged:
    //    if (settings_.applocEnabled !== checked)
    //      settings_.applocEnabled = checked

    //  text: qsTr("Launch games in Japanese locale (0x0411) using AppLocale")

    //  height: layout_.cellHeight; width: parent.width
    //  font.pixelSize: layout_.fontSize
    //}

    //SpringBoard.SwitchButton { // Time zone
    //  checked: settings_.timeZoneEnabled
    //  onCheckedChanged:
    //    if (settings_.timeZoneEnabled !== checked)
    //      settings_.timeZoneEnabled = checked

    //  text: qsTr("Launch games in Japanese Time Zone (+9 Asia/Tokyo)")

    //  height: layout_.cellHeight; width: parent.width
    //  font.pixelSize: layout_.fontSize
    //}

    //SpringBoard.SwitchButton { // Game detection
    //  checked: settings_.gameDetectionEnabled
    //  onCheckedChanged:
    //    if (settings_.gameDetectionEnabled !== checked)
    //      settings_.gameDetectionEnabled = checked

    //  text: qsTr("Detect and sync with running game")

    //  height: layout_.cellHeight; width: parent.width
    //  font.pixelSize: layout_.fontSize
    //}

    //SpringBoard.SwitchButton { // User-defined hook code
    //  checked: settings_.hookCodeEnabled
    //  onCheckedChanged:
    //    if (settings_.hookCodeEnabled !== checked)
    //      settings_.hookCodeEnabled = checked

    //  text: qsTr("Apply /h-code after game starts")
    //      + " (" + qsTr("Disable me if user-defined hcode is incorrect") + ")"

    //  height: layout_.cellHeight; width: parent.width
    //  font.pixelSize: layout_.fontSize
    //}
  }
}

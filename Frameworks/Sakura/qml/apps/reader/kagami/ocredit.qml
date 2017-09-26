/** ocredit.qml
 *  9/7/2014 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop
import '../../../js/sakurakit.min.js' as Sk
import '../share' as Share

Rectangle { id: root_

  property real zoomFactor: 1.0
  property bool ignoresFocus: false

  property string text: textArea_.textEdit.text
  //property bool autoReleaseImage: false

  property bool busy: false // whether is ocring

  function show(image, text) { // OcrImageObject
    imageObject = image
    loadImageProperties()
    textArea_.textEdit.text = text || ('(' + Sk.tr("empty") + ')')
    textArea_.textEdit.font.pixelSize = zoomFactor * 12
    visible = true
  }

  function hide() {
    visible = false
    saveImageProperties()
    imageObject = null
  }

  // - Private -

  //function releaseImageObject() {
  //  if (autoReleaseImage && imageObject)
  //    imageObject.release()
  //  imageObject = null
  //}

  property QtObject imageObject // OcrImageObject  ocr controller

  property bool savedEnabled

  property bool savedScaleEnabled
  property real savedScaleFactor

  property bool savedColorIntensityEnabled
  property real savedMinimumColorIntensity
  property real savedMaximumColorIntensity

  property bool savedHueEnabled
  property real savedMinimumHue
  property real savedMaximumHue

  property bool savedSaturationEnabled
  property real savedMinimumSaturation
  property real savedMaximumSaturation

  function loadImageProperties() {
    if (imageObject) {
      enableButton_.checked = savedEnabled = imageObject.editable

      scaleEnableButton_.checked = savedScaleEnabled = imageObject.scaleEnabled
      scaleSlider_.value = savedScaleFactor = imageObject.scaleFactor

      intensityEnableButton_.checked = savedColorIntensityEnabled = imageObject.colorIntensityEnabled
      intensitySlider_.startValue = savedMinimumColorIntensity = imageObject.minimumColorIntensity
      intensitySlider_.stopValue = savedMaximumColorIntensity = imageObject.maximumColorIntensity

      hueEnableButton_.checked = savedHueEnabled = imageObject.hueEnabled
      hueSlider_.startValue = savedMinimumHue = imageObject.minimumHue
      hueSlider_.stopValue = savedMaximumHue = imageObject.maximumHue

      saturationEnableButton_.checked = savedSaturationEnabled = imageObject.saturationEnabled
      saturationSlider_.startValue = savedMinimumSaturation = imageObject.minimumSaturation
      saturationSlider_.stopValue = savedMaximumSaturation = imageObject.maximumSaturation
    }
  }

  function saveImageProperties() {
    if (imageObject) {
      imageObject.editable = enableButton_.checked

      imageObject.scaleEnabled = scaleEnableButton_.checked
      imageObject.scaleFactor = scaleSlider_.value

      imageObject.colorIntensityEnabled = intensityEnableButton_.checked
      imageObject.minimumColorIntensity = intensitySlider_.startValue
      imageObject.maximumColorIntensity = intensitySlider_.stopValue

      imageObject.hueEnabled = hueEnableButton_.checked
      imageObject.minimumHue = hueSlider_.startValue
      imageObject.maximumHue = hueSlider_.stopValue

      imageObject.saturationEnabled = saturationEnableButton_.checked
      imageObject.minimumSaturation = saturationSlider_.startValue
      imageObject.maximumSaturation = saturationSlider_.stopValue
    }
  }

  function reset() {
    if (imageObject) {
      enableButton_.checked = savedEnabled

      scaleEnableButton_.checked = savedScaleEnabled
      scaleSlider_.value = savedScaleFactor

      intensityEnableButton_.checked = savedColorIntensityEnabled
      intensitySlider_.startValue = savedMinimumColorIntensity
      intensitySlider_.stopValue = savedMaximumColorIntensity

      hueEnableButton_.checked = savedHueEnabled
      hueSlider_.startValue = savedMinimumHue
      hueSlider_.stopValue = savedMaximumHue

      saturationEnableButton_.checked = savedSaturationEnabled
      saturationSlider_.startValue = savedMinimumSaturation
      saturationSlider_.stopValue = savedMaximumSaturation

      ocr()
    }
  }

  property int _ROOT_MARGIN: 9
  //property int spacing: _ROOT_MARGIN

  width: Math.max(300, image_.width + _ROOT_MARGIN * 2)

  height: _ROOT_MARGIN
        + image_.height
        + _ROOT_MARGIN
        + textRect_.height
        + _ROOT_MARGIN
        + intensitySlider_.height
        + _ROOT_MARGIN
        + hueSlider_.height
        + _ROOT_MARGIN
        + saturationSlider_.height
        + _ROOT_MARGIN
        + scaleSlider_.height
        + _ROOT_MARGIN
        + rightButtonRow_.height
        + _ROOT_MARGIN

  //radius: 9 // the same as ocrpopup
  radius: 0 // flat

  color: '#99000000' // black
  //color: hover ? '#99000000' : '#55000000' // black

  //property bool hover: tip_.containsMouse || closeButton_.hover

  function ocr() {
    if (!imageObject)
      return

    imageObject.minimumColorIntensity = intensitySlider_.startValue
    imageObject.maximumColorIntensity = intensitySlider_.stopValue
    imageObject.colorIntensityEnabled = intensityEnableButton_.checked

    imageObject.minimumHue = hueSlider_.startValue
    imageObject.maximumHue = hueSlider_.stopValue
    imageObject.hueEnabled = hueEnableButton_.checked

    imageObject.minimumSaturation = saturationSlider_.startValue
    imageObject.maximumSaturation = saturationSlider_.stopValue
    imageObject.saturationEnabled = saturationEnableButton_.checked

    imageObject.scaleFactor = scaleSlider_.value
    imageObject.scaleEnabled = scaleEnableButton_.checked

    imageObject.editable = enableButton_.checked

    busy = true
    textArea_.textEdit.text = imageObject.ocr() || ('(' + Sk.tr("empty") + ')')
    busy = false
  }

  MouseArea { id: mouse_
    anchors.fill: parent
    acceptedButtons: Qt.LeftButton
    drag.target: root_; drag.axis: Drag.XandYAxis
  }

  Image { id: image_
    anchors {
      //left: parent.left; right: parent.right
      horizontalCenter: parent.horizontalCenter
      bottom: textRect_.top
      margins: _ROOT_MARGIN
    }
    source: imageObject ? imageObject.imageUrl : ''
    smooth: true
    fillMode: Image.PreserveAspectFit
  }

  //Desktop.TooltipArea { id: tip_
  //  anchors.fill: parent
  //  text: Sk.tr("Edit")
  //}

  // Text edit

  Rectangle { id: textRect_ // background color
    anchors {
      left: parent.left; right: parent.right
      bottom: intensitySlider_.top
      margins: _ROOT_MARGIN
    }
    color: '#aaffffff' // white
    //radius: 4
    radius: 0 // flat
    //height: 100
    //height: 60
    height: root_.width ? Math.max(70, 30000/root_.width) : 100 // 70 ~ 100

    Share.TextArea { id: textArea_
      anchors.fill: parent
      //anchors.margins: _ROOT_MARGIN
      anchors.margins: 4

      menuEnabled: !root_.ignoresFocus

      textEdit { // id: textEdit_  -- such syntax is not allowed
        textFormat: TextEdit.PlainText
        //wrapMode: TextEdit.WordWrap
        wrapMode: TextEdit.Wrap
        //color: 'snow'
        color: 'black'
        //font.pixelSize: Math.12 * root_._zoomFactor // FIXME: Do not work
      }

      onCopyTriggered: {
        var t = textEdit.text
        if (t)
          clipboardPlugin_.text = t
      }
    }
  }

  // Color intensity

  property int _SLIDER_LABEL_WIDTH: 30

  function formatIntensity(value) { // real -> string
    return Math.round(value * 255)
  }

  Share.CheckBox { id: intensityEnableButton_
    anchors {
      left: parent.left
      verticalCenter: intensitySlider_.verticalCenter
      margins: _ROOT_MARGIN
    }
    enabled: enableButton_.checked
    text: qsTr("I")
    toolTip: qsTr("Color intensity in HSI model") + " [0,255]"
  }

  Share.LabeledGrayRangeSlider { id: intensitySlider_
    anchors {
      left: intensityEnableButton_.right
      right: parent.right
      bottom: hueSlider_.top
      //margins: _ROOT_MARGIN // remove left margin
      rightMargin: _ROOT_MARGIN
      bottomMargin: _ROOT_MARGIN
    }
    enabled: enableButton_.checked && intensityEnableButton_.checked
    spacing: _ROOT_MARGIN
    labelWidth: _SLIDER_LABEL_WIDTH

    minimumValue: 0.0
    maximumValue: 1.0

    //startValue: 0.3
    //stopValue: 0.7

    startLabelText: formatIntensity(enabled ? startValue : minimumValue)
    stopLabelText: formatIntensity(enabled ? stopValue : maximumValue)

    startLabelToolTip: qsTr("Minimum text color intensity")
    stopLabelToolTip: qsTr("Maximum text color intensity")

    startHandleToolTip: startLabelToolTip
    stopHandleToolTip: stopLabelToolTip

    sliderToolTip: qsTr("Range of the text color intensity") + " [0,255]"

    //onStartValueChanged: root_.refresh()
    //onStopValueChanged: root_.refresh()
  }

  // Color hue

  function formatHue(value) { // real -> string
    return Math.round(360 * value) + "°"
  }

  Share.CheckBox { id: hueEnableButton_
    anchors {
      left: parent.left
      verticalCenter: hueSlider_.verticalCenter
      margins: _ROOT_MARGIN
    }
    enabled: enableButton_.checked
    text: qsTr("H")
    toolTip: qsTr("Hue in HSI model") + " [0°,360°]"
  }

  Share.LabeledHueRangeSlider { id: hueSlider_
    anchors {
      left: hueEnableButton_.right
      right: parent.right
      bottom: saturationSlider_.top
      //margins: _ROOT_MARGIN // remove left margin
      rightMargin: _ROOT_MARGIN
      bottomMargin: _ROOT_MARGIN
    }
    enabled: enableButton_.checked && hueEnableButton_.checked
    spacing: _ROOT_MARGIN
    labelWidth: _SLIDER_LABEL_WIDTH

    minimumValue: 0.0
    maximumValue: 1.0

    //startValue: 0.3
    //stopValue: 0.7

    startLabelText: formatHue(enabled ? startValue : minimumValue)
    stopLabelText: formatHue(enabled ? stopValue : maximumValue)

    startLabelToolTip: qsTr("Minimum hue of the text color")
    stopLabelToolTip: qsTr("Maximum hue of the text color")

    startHandleToolTip: startLabelToolTip
    stopHandleToolTip: stopLabelToolTip

    sliderToolTip: qsTr("Range of the text color's hue") + " [0°,360°]"

    //onStartValueChanged: root_.refresh()
    //onStopValueChanged: root_.refresh()
  }

  // Color saturation

  function formatSaturation(value) { // real -> string
    return value.toFixed(2)
  }

  Share.CheckBox { id: saturationEnableButton_
    anchors {
      left: parent.left
      verticalCenter: saturationSlider_.verticalCenter
      margins: _ROOT_MARGIN
    }
    enabled: enableButton_.checked
    text: qsTr("S")
    toolTip: qsTr("Saturation in HSI model") + " [0,1]"
  }

  Share.LabeledGrayRangeSlider { id: saturationSlider_
    anchors {
      left: saturationEnableButton_.right
      right: parent.right
      bottom: scaleSlider_.top
      //margins: _ROOT_MARGIN // remove left margin
      rightMargin: _ROOT_MARGIN
      bottomMargin: _ROOT_MARGIN
    }
    enabled: enableButton_.checked && saturationEnableButton_.checked
    spacing: _ROOT_MARGIN
    labelWidth: _SLIDER_LABEL_WIDTH

    minimumValue: 0.0
    maximumValue: 1.0

    //startValue: 0.3
    //stopValue: 0.7

    startLabelText: formatSaturation(enabled ? startValue : minimumValue)
    stopLabelText: formatSaturation(enabled ? stopValue : maximumValue)

    startColor: 'black'
    stopColor: 'red'

    startLabelToolTip: qsTr("Minimum saturation of the text color")
    stopLabelToolTip: qsTr("Maximum saturation of the text color")

    startHandleToolTip: startLabelToolTip
    stopHandleToolTip: stopLabelToolTip

    sliderToolTip: qsTr("Range of the text color's saturation") + " [0,1]"

    //onStartValueChanged: root_.refresh()
    //onStopValueChanged: root_.refresh()
  }
  // Scale

  function formatScale(value) { // real -> string
    return value.toFixed(2)
    //return 'x' + value.toFixed(2)
  }

  Share.CheckBox { id: scaleEnableButton_
    anchors {
      left: parent.left
      verticalCenter: scaleSlider_.verticalCenter
      margins: _ROOT_MARGIN
    }
    enabled: enableButton_.checked
    text: qsTr("Z")
    toolTip: qsTr("Zoom image text that is too large or too small")
  }

  Share.LabeledSlider { id: scaleSlider_
    anchors {
      left: scaleEnableButton_.right
      right: parent.right
      bottom: rightButtonRow_.top
      //margins: _ROOT_MARGIN // remove left margin
      bottomMargin: _ROOT_MARGIN
      rightMargin: _SLIDER_LABEL_WIDTH + _ROOT_MARGIN * 2
    }
    enabled: enableButton_.checked && scaleEnableButton_.checked
    spacing: _ROOT_MARGIN
    labelWidth: _SLIDER_LABEL_WIDTH

    minimumValue: 0.2
    maximumValue: 2.0

    handleWidth: intensitySlider_.handleWidth

    text: formatScale(enabled ? value : 1.0)
    sliderToolTip: qsTr("Scale ratio") + " [0.2,2.0]"
  }

  // Footer

  property int buttonWidth: 50

  Share.CheckButton { id: enableButton_
    anchors {
      left: parent.left
      bottom: parent.bottom
      margins: _ROOT_MARGIN
    }
    width: root_.buttonWidth
    //text: checked ? Sk.tr("Enable") : Sk.tr('Disable')
    text: Sk.tr("Enable")
    toolTip: qsTr("Enable image processing for OCR")

    //onCheckedChanged: root_.refresh()
  }

  Row { id: rightButtonRow_
    anchors {
      right: parent.right
      bottom: parent.bottom
      margins: _ROOT_MARGIN
    }

    spacing: _ROOT_MARGIN

    Share.PushButton { //id: refreshButton_
      width: root_.buttonWidth
      text: "OCR"
      toolTip: qsTr("Apply OCR to the current image")
      onClicked: root_.ocr()
      enabled: !root_.busy
      styleHint: 'primary'
      backgroundColor: style.activeColor // do not change color
    }

    Share.PushButton { id: resetButton_
      width: root_.buttonWidth
      text: Sk.tr("Reset")
      toolTip: qsTr("Reset to the last OCR settings")
      onClicked: root_.reset()
      enabled: !root_.busy
      styleHint: 'danger'
      backgroundColor: style.activeColor // do not change color
    }
  }

  Share.CloseButton { id: closeButton_
    anchors { left: parent.left; top: parent.top; margins: -4 }
    onClicked: root_.hide()
    //visible: hover || tip_.containsMouse // this will make it difficult to close
  }
}

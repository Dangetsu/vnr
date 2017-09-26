/** intspinbox.qml
 *  5/25/2014 jichi
 */
import QtQuick 1.1
import QtDesktop 0.1 as Desktop

Desktop.SpinBox {
  property int intValue

  // - Private -

  onIntValueChanged: value = intValue
  onMinimumValueChanged: if (intValue < minimumValue) intValue = minimumValue
  onMaximumValueChanged: if (intValue > maximumValue) intValue = maximumValue

  onValueChanged:
    if (parseInt(value) !== intValue) {
      if (isNaN(value))
        intValue = value = minimumValue
      else
        intValue = value
    }
}

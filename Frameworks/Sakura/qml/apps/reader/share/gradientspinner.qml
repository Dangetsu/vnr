/** gradientspinner.qml
 *  2/10/2013 jichi
 *
 *  See: http://qt-project.org/wiki/Busy-Indicator-for-QML
 */
import QtQuick 1.1
import org.sakuradite.reader 1.0 as Plugin

Plugin.GradientSpinner { id: root_
  property alias running: ani_.running
  property alias duration: ani_.duration
  property alias direction: ani_.direction

  // - Private -

  //backgroundColor: '#46b1d28f'
  //foregroundColor: '#ff77b753'

  focus: false

  RotationAnimation { id: ani_ // Make the ring do something interesting
    target: root_
    property: 'rotation' // Suppress a warning
    from: 0; to: 360
    direction: RotationAnimation.Clockwise
    duration: 1000
    loops: Animation.Infinite
    //running: indicator_.visible
    running: root_.visible
  }
}

/** rating.qml
 *  6/24/2014 jichi
 */
import QtQuick 1.1
import '../components/rating' as Rating

Item {
  implicitWidth: 400; implicitHeight: 250

  // - Private -

  Rating.RatingIndicator { id: root_
    anchors.centerIn: parent
    scale: 0.5
  }
}

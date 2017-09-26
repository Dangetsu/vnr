/** text5.qmt
 *  1/7/2015 jichi
 *  Parameters:
 *  - class: Text
 *  Require: qmlhelper_
 */
import QtQuick 1.1
//import "../../imports/qmlhelper"

Text { id: root_

  /**
   *  Property is not used to save memory
   *  @return  QTextDocument
   */
  function getTextDocument() {
    return qmlhelper_.textEdit_document(root_)
  }

  /**
   *  May need mapToItem(root_, x + mouse.x, y + mouse.y)
   *
   *  @param  x  real  relative position
   *  @param  y  real  relative position
   *  @return  string
   */
  function linkAt(x, y) {
    return qmlhelper_.textEdit_linkAt(root_, x, y)
  }

  /**
   *  Property is not used to save memory
   *  This property (selectedText) is not part of Qt5.
   *
   *  @param  x  real  relative position
   *  @param  y  real  relative position
   *  @return  string
   */
  function getSelectedLink() {
    return qmlhelper_.textEdit_linkAtCursor(root_)
  }
}

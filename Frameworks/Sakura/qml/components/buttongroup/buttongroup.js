// buttongroup.js
// 6/20/2014 jichi
// See: QtDesktop/ButtonGroup.js
// self is renamed to root otherwise it would conflict window.self while
// using Googel Closure compiler.

var root;
var checkHandlers = [];
var visibleButtons = [];
var nonVisibleButtons = [];
var direction;

function create(that, options) {
  root = that;
  direction = options.direction || Qt.Horizontal;
  root.childrenChanged.connect(rebuild);
//  root.widthChanged.connect(resizeChildren);
  build();
}

//function isButton(item) {
//  if (item && item.hasOwnProperty("__position"))
//    return true;
//  return false;
//}

function hasChecked(item) {
  return (item && item.hasOwnProperty("checked"));
}

function destroy() {
  root.childrenChanged.disconnect(rebuild);
//  root.widthChanged.disconnect(resizeChildren);
  cleanup();
}

function build() {
  visibleButtons = [];
  nonVisibleButtons = [];

  for (var i = 0, item; (item = root.children[i]); ++i) {

    //if (item.hasOwnProperty("styleHint"))
    //  item.styleHint = styleHint;

    if (!hasChecked(item))
      continue;

    item.visibleChanged.connect(rebuild); // Not optimal, but hardly a bottleneck in your app
    if (!item.visible) {
      nonVisibleButtons.push(item);
      continue;
    }
    visibleButtons.push(item);

    if (root.exclusive && item.hasOwnProperty("checkable"))
      item.checkable = true;

    if (root.exclusive) {
      item.checked = false;
      checkHandlers.push(checkExclusive(item));
      item.checkedChanged.connect(checkHandlers[checkHandlers.length - 1]);
    }
  }

  if (visibleButtons.length == 0)
    return;
  //var nrButtons = visibleButtons.length;
  //if (nrButtons == 0)
  //  return;

  if (root.checkedButton)
    root.checkedButton.checked = true;
  else if (root.exclusive) {
    root.checkedButton = visibleButtons[0];
    root.checkedButton.checked = true;
  }

  //if (nrButtons == 1) {
  //  finishButton(visibleButtons[0], "only");
  //} else {
  //  finishButton(visibleButtons[0], direction == Qt.Horizontal ? "leftmost" : "top");
  //  for (var i = 1; i < nrButtons - 1; ++i)
  //    finishButton(visibleButtons[i], direction == Qt.Horizontal ? "h_middle": "v_middle");
  //  finishButton(visibleButtons[nrButtons - 1], direction == Qt.Horizontal ? "rightmost" : "bottom");
  //}
}

//function finishButton(button, position) {
//  if (isButton(button)) {
//    button.__position = position;
//    if (direction == Qt.Vertical) {
//      button.anchors.left = root.left   //mm How to make this not cause binding loops? see QTBUG-17162
//      kutton.anchors.right = root.right
//    }
//  }
//}

function cleanup() {
  visibleButtons.forEach(function(item, i) {
    if (checkHandlers[i])
      item.checkedChanged.disconnect(checkHandlers[i]);
    item.visibleChanged.disconnect(rebuild);
  });
  checkHandlers = [];

  nonVisibleButtons.forEach(function(item, i) {
    item.visibleChanged.disconnect(rebuild);
  });
}

function rebuild() {
  if (root == undefined)
    return;

  cleanup();
  build();
}

function resizeChildren() {
  if (direction != Qt.Horizontal)
    return;

  var extraPixels = root.width % visibleButtons;
  var buttonSize = (root.width - extraPixels) / visibleButtons;
  visibleButtons.forEach(function(item, i) {
    if (!item || !item.visible)
      return;
    item.width = buttonSize + (extraPixels > 0 ? 1 : 0);
    if (extraPixels > 0)
      extraPixels--;
  });
}

function checkExclusive(item) {
  var button = item;
  return function() {
    for (var i = 0, ref; (ref = visibleButtons[i]); ++i) {
      if (ref.checked == (button === ref))
        continue;

      // Disconnect the signal to avoid recursive calls
      ref.checkedChanged.disconnect(checkHandlers[i]);
      ref.checked = !ref.checked;
      ref.checkedChanged.connect(checkHandlers[i]);
    }
    root.checkedButton = button;
  }
}

// EOF

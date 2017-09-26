// eval.js
// 1/10/2014 jichi

.pragma library // stateless

//function scriptContext() {}
var scriptContext = {} // dict

function evalLink(link) { // string ->
  if (!link)
    return
  if (link.indexOf('javascript://') === 0)
    evalJavascriptLink(link);
  else
    openExternalUrl(link);
}

function openExternalUrl(link) { // string ->
  //scriptContext.growl.msg(My.tr("Open in external browser")); // My is not defined
  Qt.openUrlExternally(link);
}

function evalJavascriptLink(link) { // string, object ->
  link = link.replace('javascript://', '');
  //console.log("eval.js:evalJavascriptLink: script =", link)
  // QML does not allow use global associate array for eval
  // See: https://bugreports.qt.io/browse/QTBUG-10492
  // See: http://stackoverflow.com/questions/543533/restricting-eval-to-a-narrow-scope
  //link = "with(this){" + link + "}";
  link = "with(this){" + link + ";null};null"; // append ';null' to prevent from returning value
  try {
    //eval.call(scriptContext, link); // not work
    (new Function(link)).call(scriptContext);
  } catch (e) {
    console.log("eval.js:evalJavascriptLink: exception =", e);
  }
}

// EOF

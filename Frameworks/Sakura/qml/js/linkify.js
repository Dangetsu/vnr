// linkify.js
// 5/27/2014 jichi

.pragma library // stateless

var RE_LINK = /(^|[^=\]])(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;

function parse(str) { // string -> string
  return str.indexOf('://') === -1 ? str : str.replace(RE_LINK, function (all, prefix, url) {
    return prefix + '<a target="_blank" href="' + url + '">' + url + '</a>';
  });
}

// EOF

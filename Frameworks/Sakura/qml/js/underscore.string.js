// underscore.string.js
// 2/21/2014 jichi

//.pragma library // stateless

var defaultToWhiteSpace = function(characters) {
  if (characters == null)
    return '\\s';
  else if (characters.source)
    return characters.source;
  else
    return '[' + _s.escapeRegExp(characters) + ']';
};

function ltrim(str, characters){
  if (str == null) return '';
  //if (!characters && nativeTrimLeft) return nativeTrimLeft.call(str);
  characters = defaultToWhiteSpace(characters);
  return String(str).replace(new RegExp('^' + characters + '+'), '');
}

var escapeChars = {
  lt: '<',
  gt: '>',
  quot: '"',
  amp: '&',
  apos: "'"
};

var reversedEscapeChars = {};
for(var key in escapeChars) reversedEscapeChars[escapeChars[key]] = key;
reversedEscapeChars["'"] = '#39';

function escapeHTML(str) {
  if (str == null) return '';
  return String(str).replace(/[&<>"']/g, function(m){ return '&' + reversedEscapeChars[m] + ';'; });
}

function unescapeHTML(str) {
  if (str == null) return '';
  return String(str).replace(/\&([^;]+);/g, function(entity, entityCode){
    var match;

    if (entityCode in escapeChars) {
      return escapeChars[entityCode];
    } else if (match = entityCode.match(/^#x([\da-fA-F]+)$/)) {
      return String.fromCharCode(parseInt(match[1], 16));
    } else if (match = entityCode.match(/^#(\d+)$/)) {
      return String.fromCharCode(~~match[1]);
    } else {
      return entity;
    }
  });
}

function escapeRegExp(str){
  if (str == null) return '';
  return String(str).replace(/([.*+?^=!:${}()|[\]\/\\])/g, '\\$1');
}

// EOF

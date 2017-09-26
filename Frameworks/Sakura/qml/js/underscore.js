// underscore.js
// 2/21/2014 jichi

.pragma library // stateless

var ArrayProto = Array.prototype, ObjProto = Object.prototype, FuncProto = Function.prototype;
var push             = ArrayProto.push,
    slice            = ArrayProto.slice,
    concat           = ArrayProto.concat,
    unshift          = ArrayProto.unshift,
    toString         = ObjProto.toString,
    hasOwnProperty   = ObjProto.hasOwnProperty;

// All **ECMAScript 5** native function implementations that we hope to use
// are declared here.
var
  nativeForEach      = ArrayProto.forEach,
  nativeMap          = ArrayProto.map,
  nativeReduce       = ArrayProto.reduce,
  nativeReduceRight  = ArrayProto.reduceRight,
  nativeFilter       = ArrayProto.filter,
  nativeEvery        = ArrayProto.every,
  nativeSome         = ArrayProto.some,
  nativeIndexOf      = ArrayProto.indexOf,
  nativeLastIndexOf  = ArrayProto.lastIndexOf,
  nativeIsArray      = Array.isArray,
  nativeKeys         = Object.keys,
  nativeBind         = FuncProto.bind;

// Copied from coffeescript instead of underscore.js
function bind(fn, me){
  return function() {
    return fn.apply(me, arguments);
  };
}

// Slight different from underscore.js
// It can only take one parameter
function extend(obj, source) {
  if (source)
    for (var prop in source)
      obj[prop] = source[prop];
  return obj;
};


function has(obj, key) {
  return hasOwnProperty.call(obj, key);
};

function invert(obj) {
  var result = {};
  for (var key in obj) if (has(obj, key)) result[obj[key]] = key;
  return result;
};

var keys = nativeKeys || function(obj) {
  if (obj !== Object(obj)) throw new TypeError('Invalid object');
  var keys = [];
  for (var key in obj) if (has(obj, key)) keys[keys.length] = key;
  return keys;
};

function values(obj) {
  var values = [];
  for (var key in obj) if (has(obj, key)) values.push(obj[key]);
  return values;
};

var entityMap = {
  escape: {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2f;'
  }
};
entityMap.unescape = invert(entityMap.escape);

var entityRegexes = {
  escape:   new RegExp('[' + keys(entityMap.escape).join('') + ']', 'g'),
  unescape: new RegExp('(' + keys(entityMap.unescape).join('|') + ')', 'g')
};

function escape(string, safe) {
  //if (string == null) return '';
  //return ('' + string)
  return string.replace(entityRegexes.escape, function(match) {
    //return entityMap.escape[match];
    return safe && (safe.length === 1 && match === safe || match.indexOf(safe) !== -1) ? match : entityMap.escape[match];
  });
}

function unescape(string, safe) {
  //if (string == null) return '';
  //return ('' + string)
  return string.replace(entityRegexes.unescape, function(match) {
    //return entityMap.unescape[match];
    return safe && (safe.length === 1 && match === safe || match.indexOf(safe) !== -1) ? match : entityMap.unescape[match];
  });
}

// EOF

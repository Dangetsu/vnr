// util.js
// 10/20/2012 jichi

.pragma library // stateless

// - Qt -

// http://stackoverflow.com/questions/13923794/how-to-do-a-is-a-typeof-or-instanceof-in-qml/28384228#28384228
function qmltypeof(obj, className) { // QtObject, string -> bool
  // className plus "(" is the class instance without modification
  // className plus "_QML" is the class instance with user-defined properties
  var str = obj.toString();
  return str.indexOf(className + "(") == 0 || str.indexOf(className + "_QML") == 0;
}

// - i18n -

var LANGUAGES = [
  'ja'
  , 'en'
  , 'zht', 'zhs'
  , 'ko'
  , 'vi', 'tl', 'th', 'id', 'ms', 'he', 'ar'
  , 'cs', 'da', 'de', 'el', 'es', 'et', 'fr', 'hu', 'it', 'lt', 'lv', 'nl', 'no', 'pl', 'pt', 'ro', 'sl', 'sk', 'sv', 'tr'
  , 'be', 'bg', 'ru', 'uk'
];

/**
 *  @param  lang  string
 *  @return  bool
 **/
function isKnownLanguage(lang) { return -1 !== LANGUAGES.indexOf(lang); }

/**
 *  @param  lang  string
 *  @return  string
 **/
function languageShortName(lang) { return lang === 'no' ? 'nb' : lang || '' }

/**
 *  @param  lang  string
 *  @return  string
 **/

var LANGUAGE_NAME = {
 ja: "Japanese"
 , en: "English"
 , zh: "Chinese", zht: "Chinese", zhs: "Simplified Chinese"
 , ko: "Korean"
 , vi: "Vietnamese"
 //, tl: "Filipino"
 , tl: "Tagalog"
 , th: "Thai"
 , id: "Indonesian"
 , ms: "Melayu"
 , he: "Hebrew"
 , ar: "Arabic"
 , be: "Belarusian"
 , bg: "Bulgarian"
 , cs: "Czech"
 , da: "Danish"
 , de: "German"
 , el: "Greek"
 , es: "Spanish"
 , et: "Estonian"
 , fi: "Finnish"
 , fr: "French"
 , hu: "Hungarian"
 , it: "Italian"
 , lt: "Lithuanian"
 , lv: "Latvian"
 , nl: "Dutch"
 , nb: "Norwegian", no: "Norwegian"
 , pl: "Polish"
 , pt: "Portuguese"
 , ro: "Romanian"
 , ru: "Russian"
 , sk: "Slovak"
 , sl: "Slovenian"
 , sv: "Swedish"
 , tr: "Turkish"
 , uk: "Ukrainian"
};
function languageName(lang) { return LANGUAGE_NAME[lang]; }

var LATIN_LANGUAGES = [
  'en'
  , 'el'
  , 'ru', 'bg', 'uk',
  , 'cs', 'da', 'de', 'es', 'et', 'fi', 'fr', 'hu', 'it', 'lt', 'lv', 'no', 'nl', 'pl', 'pt', 'ro','sk', 'sl', 'sv', 'tr'
  , 'vi', 'tl', 'th', 'ms', 'id', 'he', 'ar'
];

/**
 *  @param  lang  string
 *  @return  bool  whether the language is based on latin characters
 */
function isLatinLanguage(lang) { return -1 !== LATIN_LANGUAGES.indexOf(lang); }

/**
 *  @param  lang  string
 *  @return  bool  whether the language is based on cyrillic characters
 */
var CYRILLIC_LANGUAGES = ['ru', 'be', 'bg', 'uk']
function isCyrillic(lang) { return -1 !== CYRILLIC_LANGUAGES.indexOf(lang); }

var CJK_LANGUAGES = [
  'ja'
  , 'zht', 'zhs', 'zh'
  , 'ko'
];
/**
 *  @param  lang  string
 *  @return  bool  whether it is eastern asian language
 */
function isCJKLanguage(lang) {
  switch (lang) {
    case 'zht': case 'zhs': case 'zh':
    case 'ko': case 'ja':
      return true;
    default: return false;
  }
}

/** Japanese/Chinese but Korean.
 *  The definition of this function is different from Python.
 *  @param  lang  string
 *  @return  bool  whether it is based on kanji characters
 */
function isKanjiLanguage(lang) {
  switch (lang) {
    case 'zht': case 'zhs': case 'zh':
    case 'ja':
      return true;
    default: return false;
  }
}

/**
 *  @param  lang  string
 *  @return  bool
 */
function isChineseLanguage(lang) {
  switch (lang) {
    case 'zht': case 'zhs': return true;
    default: return false;
  }
}

/**
 *  @param  lang  string
 *  @return  bool
 */
function spellSupportsLanguage(lang) {
  switch (lang) {
    case 'en': case 'de': case 'fr': return true;
    default: return false;
  }
}

var YOMI_LANGUAGES = [
  'en'
  , 'ru'
  //, 'be'
  //, 'bg'
  , 'uk'
  , 'el'
  //, 'he'
  , 'ar'
  , 'th'
  , 'ko'
  //, 'zh'
]

var ALPHABET_LANGUAGES = [
  //'en'
  'ru'
  //, 'bg'
  , 'uk'
  //, 'he'
  //, 'el'
]

/**
 *  @param  text  string
 *  @return  bool
 */
function containsLatin(text) {
  return text && text.match(/[a-zA-Z]/);
}

var LANGUAGE_FONT = {
  //ja: "MS Mincho"
  ja: "MS Gothic"
  , en: "Helvetica"
  , zh: "YouYuan"
  , zhs: "YouYuan"
  , zht: "YouYuan"
  , ko: "Batang"
  //, vi: "Tahoma"
  //, th: "Tahoma"
  //, ar: "Tahoma" //"Aria"
};
/**
 *  @param  lang  string
 *  @return  string
 *
 *  http://en.wikipedia.org/wiki/List_of_CJK_fonts
 */
function fontFamilyForLanguage(lang) { return LANGUAGE_FONT[lang] || "Tahoma"; } // "Helvetica" not available on Windows

var TRANSLATOR_HOST_KEYS = [
  'bing'
  , 'google'
  , 'babylon'
  , 'lecol'
  , 'infoseek'
  , 'excite'
  , 'nifty'
  , 'systran'
  , 'transru'
  , 'naver'
  , 'baidu'
  , 'youdao'
  , 'jbeijing'
  , 'fastait'
  , 'dreye'
  , 'eztrans'
  , 'transcat'
  , 'lec'
  , 'atlas'
  , 'hanviet'
  , 'vtrans'
];

var TRANSLATOR_NAME = {
  infoseek: "Infoseek.co.jp"
  , excite: "Excite.co.jp"
  , systran: "SYSTRANet.com"
  , babylon: "Babylon.com"
  , bing: "Bing.com"
  , google: "Google.com"
  , naver: "Naver.com"
  , nifty: "@nifty.com"
  , baidu: "百度.com"
  , youdao: "有道.com"
  , jbeijing: "J北京"
  , fastait: "金山快譯"
  , dreye: "Dr.eye"
  , eztrans: "ezTrans XP"
  , transcat: "TransCAT"
  , atlas: "ATLAS"
  , lec: "LEC"
  , lecol: "LEC Online"
  , transru: "Translate.Ru"
  //, lou: "ルー語"
  , hanviet: "Hán Việt"
  , vtrans: "vTrans"
  , romaji: "読み方"
};
function translatorName(tr) {
  var ret = TRANSLATOR_NAME[tr];
  if (!ret && ~tr.indexOf(',')) {
    var s = tr.split(','),
        t = [];
    for (var i in s)
      t.push(TRANSLATOR_NAME[s[i]]);
    ret = t.join(',');
  }
  return ret || '';
}

// - Type constants -

var TERM_TYPES = [
  'trans'
  , 'input'
  , 'output'
  , 'name'
  , 'yomi'
  , 'suffix'
  , 'prefix'
  , 'game'
  , 'tts'
  , 'ocr'
  , 'macro'
  , 'proxy'
];

var TERM_CONTEXTS = [
  'scene'
  , 'name'
  , 'window'
  , 'other'
];

// - Cast -

/**
 *  @param  val  var
 *  @return  bool
 */
function toBool(val) {
  //return !!val
  return val ? true : false;
}

// - String -

// See: http://blog.enjoitech.jp/article/180
// See: http://stackoverflow.com/questions/2429146/javascript-regular-expression-single-space-character
// \s: [\t\n\v\f\r \u00a0\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a\u200b\u2028\u2029\u3000]
/**
 *  @param  str  string
 *  @return  string
 */
function utrim(str) { // unicode trim
  return str ? str.replace(/^\s+|\s+$/g, "") : "";
}

/**
 *  @param  str  string
 *  @return  string
 */
function ultrim(str) {
  return str ? str.replace(/^\s+/, "") : "";
}

/**
 *  @param  str  string
 *  @return  string
 */
function urtrim(str) {
  return str ? str.replace(/\s+$/, "") : "";
}

/**
 *  @param  str  string
 *  @return  string
 */
function trim(str) { // unicode trim
  return str ? str.replace(/^[\t\n\v\f\r ]+|[\t\n\v\f\r ]+$/g, "") : "";
}

/**
 *  @param  str  string
 *  @return  string
 */
function ltrim(str) {
  return str ? str.replace(/^[\t\n\v\f\r ]+/, "") : "";
}

/**
 *  @param  str  string
 *  @return  string
 */
function rtrim(str) {
  return str ? str.replace(/[\t\n\v\f\r ]+$/, "") : "";
}


// See: http://www.openjs.com/scripts/strings/setcharat_function.php
/**
 *  @param  str  string
 *  @param  index  int
 *  @param  ch  string[1]
 *  @return  string
 */
function setCharAt(str, index, ch) {
  return index < 0 || !str || index >= str.length ? str :
         str.substr(0, index) + ch + str.substr(index + 1);
}

// See: http://dev.ariel-networks.com/Members/uchida/javascript7684startswith/
/**
 *  @param  str  string
 *  @param  prefix  string
 *  @return  bool
 */
function startsWith(str, prefix) {
  return !!str && !str.indexOf(prefix); //=== 0
}

// See: http://stackoverflow.com/questions/280634/endswith-in-javascript
/**
 *  @param  str  string
 *  @param  suffix  string
 *  @return  bool
 */
function endsWith(str, suffix) {
  return !!(str && suffix && ~str.indexOf(suffix, str.length - suffix.length)); // !== -1
}

// See: http://www.electrictoolbox.com/pad-number-zeroes-javascript/
/**
 *  @param  d  Date
 *  @return  int
 */
function padZero(number, length) {
  var ret = '' + number;
  while (ret.length < length)
     ret = '0' + ret;
  return ret;
}

/**
 *  @param  str  string
 *  @return  string
 */
function removeHtmlTags(str) {
  return str.replace(/<[^>]*>/g, '');
}

/**
 *  @param  text  string
 *  @param* limit  max name length
 *  @return  string
 */
//var MAX_NAME_LENGTH = 16; // max name length not forced
function removeTextName(text, limit) {
  // http://stackoverflow.com/questions/1979884/how-to-use-javascript-regex-over-multiple-lines
  //return text.replace(/^[\s\S]+?「/, '「') // remove text before 「
  //           .replace(/^【[^】]*】/, '')  // remove text in 【】
  // Do not use regex for better performance
  if (!text)
    return text;
  var i = text.indexOf('「');
  if (i > 0 && (!limit || i < limit))
    return text.substr(i);
  if (text[0] == '【') {
    i = text.indexOf('】');
    if (i > 0 && (!limit || i < limit))
      return text.substr(i+1);
  }
  return text;
}

/**
 *  @param  text  string
 *  @return  string
 */
function removeBBCode(text) { // string ->  string  remove HTML tags
  if (!~text.indexOf('['))
    return text
  return text.replace(/\[[^\]]+\]/g, '') // remove all bbcode tags between []
}

// - Datetime -

// See: http://www.electrictoolbox.com/unix-timestamp-javascript/
/**
 *  @param  d  Date
 *  @return  int
 */
function currentUnixTime() {
  return Math.floor(new Date().getTime() / 1000);
}

/**
 *  @param  d  Date
 *  @return  string
 */

var WEEK_NAME = [
  "日"
  , "月"
  , "火"
  , "水"
  , "木"
  , "金"
  , "土"
];

function dateTimeToString(d) {
  return (d.getMonth()+1) + "/" + d.getDate() + "/" + d.getFullYear() + " " + WEEK_NAME[d.getDay()] + " " +
         d.getHours() + ":" + padZero(d.getMinutes(), 2) + ":" + padZero(d.getSeconds(), 2);
}

function dateToString(d) {
  return (d.getMonth()+1) + "/" + d.getDate() + "/" + d.getFullYear() + " " + WEEK_NAME[d.getDay()];
}

function timeToString(d) {
  return d.getHours() + ":" + padZero(d.getMinutes(), 2) + ":" + padZero(d.getSeconds(), 2);
}

/**
 *  @param  seconds  int
 *  @return  string
 */
function datestampToString(seconds) {
  return dateToString(new Date(seconds * 1000));
}

function timestampToString(seconds) {
  return dateTimeToString(new Date(seconds * 1000));
}

/**
 *  @param  h  int
 *  @param  m  int
 *  @param* s  int or undefined
 *  @return  string
 */
function formatTime(h, m, s) {
  var r = h + ":" + padZero(m, 2);
  if (s !== undefined)
    r += ":" + padZero(s, 2);
  return r;
}

/**
 *  @param  m  int  month
 *  @param  d  int  day
 *  @param* y  int  year
 *  @param* w  int  week
 *  @return  string
 */
function formatDate(m, d, y, w) {
  var r = m + "/" + d;
  if (y !== undefined)
    r += "/" + y;
  if (w !== undefined)
    r += " " + WEEK_NAME[w];
  return r;
}

/**
 *  @param w  int  week
 *  @return  string
 */
function formatWeek(w) { return WEEK_NAME[w]; }

// - QML -

/**
 *  @param  item  QtQuick.Item
 *  @return  Qt.point
 */
function itemGlobalPos(item) {
  var x = 0;
  var y = 0;
  while (item) {
    if (item.x) // test first as most x,y are zeros
      x += item.x;
    if (item.y)
      y += item.y;
    item = item.parent;
  }
  return Qt.point(x, y);
}

// EOF

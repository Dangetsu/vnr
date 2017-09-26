// ajax.js
// 2/20/2014 jichi

.pragma library // stateless

//var DEBUG = true;
var DEBUG = false;

var MIMETYPE_JSON = 'application/json;charset=utf-8',
    MIMETYPE_URL = 'application/x-www-form-urlencoded',
    MIMETYPE_XML = 'application/xml;charset=utf-8';

// JSON List model
// http://qt-project.org/wiki/JSONListModel

// XMLHttpRequest:
// http://qt-project.org/forums/viewthread/2057
// http://stackoverflow.com/questions/6461958/parameter-true-in-xmlhttprequest-open-method

/**
 *  options  object
 *    url  string
 *    *data  string
 *    *contentType  string
 *    *headers  {string k:string v}
 *    *success  string data ->
 *    *error  xhr ->
 *  -> xhr
 *
 *  See:
 *  https://api.jquery.com/jQuery.ajax/
 *  http://qt-project.org/doc/qt-4.8/declarative-xml-xmlhttprequest-xmlhttprequest-example-qml.html
 */
function ajax(options) {
  var url = options.url,
      type = options.type || 'GET',
      data = options.data,
      contentType = options.contentType,
      headers = options.headers,
      success = options.success,
      error = options.error;

  var xhr = new XMLHttpRequest();

  xhr.open(type, url, true);

  // timeout is not implemented in QML? https://qt-project.org/forums/viewthread/18666
  //xhr.timeout
  //xhr.ontimeout

  if (contentType)
    xhr.setRequestHeader('Content-Type', contentType);

  if (data)
    xhr.setRequestHeader('Content-Length', data.length);
  //xhr.setRequestHeader('Connection', 'close');

  if (headers)
    for (var k in headers)
      xhr.setRequestHeader(k, headers[k]);

  xhr.onreadystatechange = function() {
    switch (xhr.readyState) {
      case XMLHttpRequest.DONE:
        switch (xhr.status) {
          case 200:
            if (success)
              success(xhr.responseText, xhr);
            break;
          default:
            if (DEBUG)
              console.log("ajax.js: error status =", xhr.status)
            if (error)
              error(xhr);
        }
        break;
      //case xhr.readyState == XMLHttpRequest.HEADERS_RECEIVED:
    }
  }
  if (DEBUG)
    console.log("ajax.js: send url =", url)
  if (data)
    xhr.send(data);
  else
    xhr.send();
  return xhr;
}

/**
 *  -  url: string
 *  -* success  string data ->
 *  -* error  xhr ->
 *  -> xhr
 *
 *  See:
 *  https://api.jquery.com/jQuery.get/
 */
function get(url, success, error) {
  return ajax({
    url: url
    , type: 'GET'
    , success: success
    , error: error
  });
}

function getJSON(url, success, error) {
  return ajax({
    url: url
    , type: 'GET'
    , contentType: MIMETYPE_JSON
    , error: error
    , success: function(data, xhr) {
      if (success)
        success(data ? JSON.parse(data) : null, xhr);
    }
  });
}

/**
 *  -  url  string
 *  -  data  string
 *  -* success  string data ->
 *  -* error  xhr ->
 *  -> xhr
 *
 *  See:
 *  https://api.jquery.com/jQuery.post/
 */
function post(url, data, success, error) {
  return ajax({
    url: url
    , type: 'POST'
    , data: data
    , success: success
    , error: error
  });
}

/**
 *  -  url  string
 *  -  obj  object
 *  -* success  string data ->
 *  -* error  xhr ->
 *  -> xhr
 *
 *  See:
 *  https://api.jquery.com/jQuery.post/
 */
function postJSON(url, obj, success, error) {
  return ajax({
    url: url
    , type: 'POST'
    , data: JSON.stringify(obj)
    , contentType: MIMETYPE_JSON
    , error: error
    , success: function(data, xhr) {
      if (success)
        success(data ? JSON.parse(data) : null, xhr);
    }
  });
}

// EOF

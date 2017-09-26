// atmosphere.js
// 2/20/2014 jichi

.pragma library // stateless

//var DEBUG = true;
var DEBUG = false;

// - AJAX -

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
              console.log("ajax.js: error status =", xhr.status);
            if (error)
              error(xhr);
        }
        break;
      //case xhr.readyState == XMLHttpRequest.HEADERS_RECEIVED:
    }
  }
  if (DEBUG)
    console.log("ajax.js: send url =", url);
  if (data)
    xhr.send(data);
  else
    xhr.send();
  return xhr;
}

//function get(url, success, error) {
//  return ajax({
//    url: url
//    , type: 'GET'
//    , success: success
//    , error: error
//  });
//}
//
//function post(url, data, success, error) {
//  return ajax({
//    url: url
//    , type: 'POST'
//    , data: data
//    , success: success
//    , error: error
//  });
//}

// - Underscore -

function bind(fn, me){
  return function() {
    return fn.apply(me, arguments);
  };
}

function extend(obj, source) {
  if (source)
    for (var prop in source)
      obj[prop] = source[prop];
  return obj;
};

// - Underscore.string -

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

// - jQuery -

// Simplified
function param(obj) {
  var ret = ''
  for (var k in obj) {
    if (ret)
      ret += '&';
    // encodeURIComponent is not used, which is not needed for atmosphere parameters
    ret += k + '=' + obj[k];
  }
  return ret;
}

// - Atmosphere -

// class Comet in coffeescript
var Comet = (function() {

  // Constants

  var TRANSPORT_WEBSOCKETS = 'websockets',
      TRANSPORT_LONGPOLLING = 'long-polling',
      TRANSPORT_CLOSE = 'close';

  var REQ_KEY_ID = 'X-Atmosphere-tracking-id', // string, such as 0 or 8d09cbf7-e229-4747-a584-a0a43c372cff
      REQ_KEY_TRANSPORT = 'X-Atmosphere-Transport', // string, such as long-polling and close
      REQ_KEY_TIMESTAMP = '_'; // long in msecs, such as 1392746413354

  // Connect: http://localhost:8080/push/topic?X-Atmosphere-tracking-id=0&X-Atmosphere-Framework=2.1.2-jquery&X-Atmosphere-Transport=long-polling&X-Cache-Date=0&Content-Type=application%2Fjson&X-atmo-protocol=true&_=1392746413354
  // Respond body: a7141a65-54b5-4cce-9d13-79d2e0d436ff|1392746413433
  var REQ_PARAMS_CONNECT = {
    'X-atmo-protocol': 'true'
    , 'X-Cache-Date': '0'
    , 'X-Atmosphere-Framework': '2.1.2-jquery'
    , 'Content-Type': 'application/json'
  };
  REQ_PARAMS_CONNECT[REQ_KEY_TRANSPORT] = TRANSPORT_LONGPOLLING;

  var REQ_PARAMS_POP = REQ_PARAMS_CONNECT;
  var REQ_PARAMS_PUSH = REQ_PARAMS_CONNECT;

  // Close: http://localhost:8080/push/topic?X-Atmosphere-Transport=close&X-Atmosphere-tracking-id=6e9c61ee-0610-4d8a-8114-fec108362c72&_=1392746369695
  // Respond header: X-Atmosphere-tracking-id:  8d09cbf7-e229-4747-a584-a0a43c372cff
  var REQ_PARAMS_DISCONNECT = {};
  REQ_PARAMS_DISCONNECT[REQ_KEY_TRANSPORT] = TRANSPORT_CLOSE;

  var REQ_HEADERS_CONNECT = {
    Connection: 'keep-alive'
    , 'Content-Type': 'application/json'
    //User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:27.0) Gecko/20100101 Firefox/27.0
    //Referer: http://localhost:8080/topic
    //Host: localhost:8080
    //Accept-Language: en-US,en;q=0.5
    //Accept-Encoding: gzip, deflate
    //Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
  };

  var REQ_HEADERS_POP = REQ_HEADERS_CONNECT;

  var REQ_HEADERS_PUSH = {
    'X-Requested-With': 'XMLHttpRequest'
    , Connection: 'keep-alive'
    , Pragma: 'no-cache'
    , 'Cache-Control': 'no-cache'
    //User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:27.0) Gecko/20100101 Firefox/27.0
    //Referer: http://localhost:8080/topic/139
    //Host: localhost:8080
    //Content-Type: application/json;charset=utf-8
    //Content-Length: 108
    //Accept-Language: en-US,en;q=0.5
    //Accept-Encoding: gzip, deflate
    //Accept: application/json, text/javascript, */*; q=0.01
  };

  var REQ_HEADERS_DISCONNECT = {
    'X-Requested-With': 'XMLHttpRequest'
    , Connection: 'keep-alive'
    //User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:27.0) Gecko/20100101 Firefox/27.0
    //Referer: http://localhost:8080/game
    //Host: localhost:8080
    //Accept-Language: en-US,en;q=0.5
    //Accept-Encoding: gzip, deflate
    //Accept: */*
  };

  // Static methods
  function currentTimeMillis() { return new Date().getTime(); }

  // Constructor
  var __methods = [] // [string}

  function Comet(url, reconnectTimerId) { // string, QML timer ID ->
    for (var k in __methods)
      this[k] = bind(this[k], this);

    this.url = url; // string
    this.trackingId = 0; // string or 0

    this.state = 'disconnected'; // {'connected', 'disconnected'}

    this.reconnectCount = 0; // int
    this.maxReconnectCount = 5; // int, 5 times
    //this.reconnectInterval = 5000; // int, 5 seconds // setTimeout is not supported by QML

    this.onMessage = function(xhr, data) {}; // onPop, naming is consistent with atmosphere
    this.onMessagePublished = function(xhr, data) {}; // onPush,naming is consistent with atmosphere
    this.onConnect = function(xhr) {};
    this.onDisconnect = function(xhr) {};
    this.onReconnect = function(xhr) {};
    this.onError = function(xhr, message) {};

    //if (reconnectTimerId)
    //  this.setReconnectTimer(reconnectTimerId);
    this.reconnectTimer = reconnectTimerId;
  }

  // Methods
  //__methods.push('setReconnectTimer');
  //Comet.prototype.setReconnectTimer = function(timerId) { // QML timer ID ->
  //  if (this.reconnectTimer !== timerId) {
  //    this.reconnectTimer = timerId;
  //    if (timerId) {
  //      timerId.interval = this.reconnectInterval;
  //      timerId.repeat = false;
  //      timerId.triggered.connect(this.pop); // This does not work since pop bound with this
  //      timerId.start();
  //    }
  //  }
  //}

  __methods.push('connect');
  Comet.prototype.connect = function() { // -> xhr
    if (this.state == 'connected')
      return;
    if (DEBUG)
      console.log("atmosphere: connect enter")
    var params = {};
    params[REQ_KEY_ID] = 0;
    params[REQ_KEY_TIMESTAMP] = currentTimeMillis();
    extend(params, REQ_PARAMS_CONNECT);
    var url = this.url + '?' + param(params);
    return ajax({
      url: url
      , headers: REQ_HEADERS_CONNECT
      , error: bind(function (xhr) {
        this.onError(xhr, "connect error");
      }, this)
      , success: bind(function (data, xhr) {
        if (data) {
          // The response body is patched with leading spaces
          data = ltrim(data);
          // Example: 551f1b35-8067-4b02-9c4e-e2588934de5a|1392761214993
          //trackingId, _, timestamp = data.partition('|');
          var trackingId = data.split('|')[0];
          if (trackingId) {
            this.trackingId = trackingId;
            if (DEBUG)
              console.log("atmosphere: connected");
            this.onConnect(xhr);
            this.state = 'connected';
            this.pop();
            return;
          }
        }
        this.onError(xhr, "connect error: invalid response data: " + data);
      }, this)
    });
  }

  __methods.push('disconnect');
  Comet.prototype.disconnect = function() { // -> xhr
    if (this.state == 'disconnected')
      return;
    this.state = 'disconnected';
    if (DEBUG)
      console.log("atmosphere: disconnect enter")
    var params = {};
    params[REQ_KEY_ID] = this.trackingId;
    params[REQ_KEY_TIMESTAMP] = currentTimeMillis();
    extend(params, REQ_PARAMS_DISCONNECT);
    var url = this.url + '?' + param(params);
    return ajax({
      url: url
      , headers: REQ_HEADERS_DISCONNECT
      , error: bind(function (xhr) {
        this.onError(xhr, "disconnect error");
        if (DEBUG)
          console.log("atmosphere: disconnected");
        this.onDisconnect(xhr);
      }, this)
      , success: bind(function (data, xhr) {
        var ok = xhr.getResponseHeader(REQ_KEY_ID) == this.trackingId;
        if (!ok)
          this.onError(xhr, "disconnect error: mismatched tracking ID");
        if (DEBUG)
          console.log("atmosphere: disconnected");
        this.onDisconnect(xhr);
      }, this)
    })
  }

  __methods.push('push');
  Comet.prototype.push = function (data) { // string -> xhr
    if (this.state != 'connected')
      return;
    if (DEBUG)
      console.log("atmosphere: push enter")
    var params = {};
    params[REQ_KEY_ID] = this.trackingId;
    params[REQ_KEY_TIMESTAMP] = currentTimeMillis();
    extend(params, REQ_PARAMS_PUSH);
    var url = this.url + '?' + param(params);
    return ajax({
      url: url
      , type: 'POST'
      , data: data
      , error: bind(function (xhr) {
        this.onError(xhr, "push error");
      }, this)
      , success: bind(function (data, xhr) {
        if (DEBUG)
          console.log("atmosphere: message published");
        this.onMessagePublished(xhr, data);
      }, this)
    });
  }

  __methods.push('pop');
  Comet.prototype.pop = function() { // -> xhr
    if (this.state != 'connected')
      return;
    if (DEBUG)
      console.log("atmosphere: pop enter")
    var params = {};
    params[REQ_KEY_ID] = this.trackingId;
    params[REQ_KEY_TIMESTAMP] = currentTimeMillis();
    extend(params, REQ_PARAMS_POP);
    var url = this.url + '?' + param(params);
    return ajax({
      url: url
      , headers:REQ_HEADERS_POP
      , error: bind(function (xhr) {
        this.onError(xhr, "pop error");

        if (this.state == 'connected' && this.reconnectCount < this.maxReconnectCount) {
          this.reconnectCount++;
          if (DEBUG)
            console.log("atmosphere: reconnect", this.reconnectCount, '/', this.maxReconnectCount);
          this.onReconnect(xhr);
          //setTimeout(this.pop, this.reconnectInterval); // FIXME: Not supported in QML
          //this.pop();
          if (this.reconnectTimer)
            this.reconnectTimer.start();
          else
            this.reconnect();
        } else
          this.disconnect();
      }, this)
      , success: bind(function (data, xhr) {
        if (this.state == 'connected') {
          data = ltrim(data);
          if (DEBUG)
            console.log("atmosphere: message: data =", data);
          this.onMessage(xhr, data);
          this.pop();
        }
      }, this)
    });
  }

  __methods.push('reconnect');
  Comet.prototype.reconnect = function() { // -> xhr
    //this.onReconnect(xhr);
    return this.pop();
  }

  return Comet;
})();

function subscribe(url) { return new Comet(url); }

// Debug
//var url = "http://sakuradite.com/push/vnr/topic/term";
//var conn = new Comet(url);
//conn.onError = function (xhr, msg) { console.log(msg); }
//conn.onMessage = function (xhr, data) { console.log(msg); }
//conn.connect()
//conn.push("revive")
//conn.pop()
//conn.disconnect()

// EOF

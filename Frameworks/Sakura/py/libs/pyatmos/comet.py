# coding: utf8
# comet.py
# jichi 2/17/2014
#
# See:
# atmosphere.js 2.1.2
# https://gist.github.com/aparrish/1672967

__all__ = 'CometConnection',

import requests, time

def EMPTY_FUNC(*args, **kwargs): pass

# Constants

TRANSPORT_WEBSOCKETS = 'websockets'
TRANSPORT_LONGPOLLING = 'long-polling'
TRANSPORT_CLOSE = 'close'

REQ_KEY_ID = 'X-Atmosphere-tracking-id' # string, such as 0 or 8d09cbf7-e229-4747-a584-a0a43c372cff
REQ_KEY_TRANSPORT = 'X-Atmosphere-Transport' # string, such as long-polling and close
REQ_KEY_TIMESTAMP = '_' # long in msecs, such as 1392746413354

# Connect: http://localhost:8080/push/topic?X-Atmosphere-tracking-id=0&X-Atmosphere-Framework=2.1.2-jquery&X-Atmosphere-Transport=long-polling&X-Cache-Date=0&Content-Type=application%2Fjson&X-atmo-protocol=true&_=1392746413354
# Respond body: a7141a65-54b5-4cce-9d13-79d2e0d436ff|1392746413433
REQ_PARAMS_CONNECT = {
  REQ_KEY_TRANSPORT: TRANSPORT_LONGPOLLING,
  'X-atmo-protocol': 'true',
  'X-Cache-Date': '0',
  'X-Atmosphere-Framework': '2.1.2-jquery',
  'Content-Type': 'application/json',
}

REQ_PARAMS_POP = REQ_PARAMS_CONNECT
REQ_PARAMS_PUSH = REQ_PARAMS_CONNECT

# Close: http://localhost:8080/push/topic?X-Atmosphere-Transport=close&X-Atmosphere-tracking-id=6e9c61ee-0610-4d8a-8114-fec108362c72&_=1392746369695
# Respond header: X-Atmosphere-tracking-id:  8d09cbf7-e229-4747-a584-a0a43c372cff
REQ_PARAMS_DISCONNECT = {
  REQ_KEY_TRANSPORT: TRANSPORT_CLOSE,
}

REQ_HEADERS_CONNECT = {
  'Connection': 'keep-alive',
  'Content-Type': 'application/json',
  #User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:27.0) Gecko/20100101 Firefox/27.0
  #Referer: http://localhost:8080/topic
  #Host: localhost:8080
  #Accept-Language: en-US,en;q=0.5
  #Accept-Encoding: gzip, deflate
  #Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
}

REQ_HEADERS_POP = REQ_HEADERS_CONNECT

REQ_HEADERS_PUSH = {
  'X-Requested-With': 'XMLHttpRequest',
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  #User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:27.0) Gecko/20100101 Firefox/27.0
  #Referer: http://localhost:8080/topic/139
  #Host: localhost:8080
  #Content-Type: application/json;charset=utf-8
  #Content-Length: 108
  #Accept-Language: en-US,en;q=0.5
  #Accept-Encoding: gzip, deflate
  #Accept: application/json, text/javascript, */*; q=0.01
}

REQ_HEADERS_DISCONNECT = {
  'X-Requested-With': 'XMLHttpRequest',
  'Connection': 'keep-alive',
  #User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:27.0) Gecko/20100101 Firefox/27.0
  #Referer: http://localhost:8080/game
  #Host: localhost:8080
  #Accept-Language: en-US,en;q=0.5
  #Accept-Encoding: gzip, deflate
  #Accept: */*
}

class CometConnection(object):

  @staticmethod
  def currentTimeMillis(): return int(time.time() * 1000)

  def get(self, *args, **kwargs): return self.session.get(*args, **kwargs)

  def post(self, *args, **kwargs): return self.session.post(*args, **kwargs)

  def __init__(self, url):
    self.session = requests.Session()

    self.url = url # str
    self.trackingId = 0 # string or 0

    # Callbacks
    self.onMessage = EMPTY_FUNC # onPop, naming is consistent with atmosphere
    self.onMessagePublished = EMPTY_FUNC # onPush,naming is consistent with atmosphere
    self.onConnect = EMPTY_FUNC
    self.onDisconnect = EMPTY_FUNC
    self.onReconnect = EMPTY_FUNC
    self.onError = EMPTY_FUNC

  def connect(self): # -> str trackingId or 0
    params = {REQ_KEY_ID:0, REQ_KEY_TIMESTAMP:self.currentTimeMillis()}
    params.update(REQ_PARAMS_CONNECT)
    r = None
    try:
      r = self.get(self.url, params=params, headers=REQ_HEADERS_CONNECT)
      ok = r.status_code == 200
      if ok:
        # The response body is patched with leading spaces
        data = r.content.lstrip()
        # Example: 551f1b35-8067-4b02-9c4e-e2588934de5a|1392761214993
        trackingId, _, timestamp = data.partition('|')
        if trackingId:
          self.trackingId = trackingId
          self.onConnect(r)
          return trackingId
      self.onError(r, "connect error")
    except Exception, e:
      self.onError(r, "connect error: %s" % e)
    return 0

  def disconnect(self): # -> bool
    params = {REQ_KEY_ID:self.trackingId, REQ_KEY_TIMESTAMP:self.currentTimeMillis()}
    params.update(REQ_PARAMS_DISCONNECT)
    ok = False
    r = None
    try:
      r = self.get(self.url, params=params, headers=REQ_HEADERS_DISCONNECT)
      r.content # flush request
      ok = r.status_code == 200 and r.headers[REQ_KEY_ID] == self.trackingId
      if not ok:
        self.onError(r, "disconnect error")
    except Exception, e:
      self.onError(r, "disconnect error: %s" % e)
    self.onDisconnect(r)
    return ok

  def pop(self): # -> bool
    params = {REQ_KEY_ID:self.trackingId, REQ_KEY_TIMESTAMP:self.currentTimeMillis()}
    params.update(REQ_PARAMS_POP)
    r = None
    try:
      r = self.get(self.url, params=params, headers=REQ_HEADERS_POP)
      ok = r.status_code == 200
      if ok:
        data = r.content.lstrip()
        self.onMessage(r, data)
        return True
      self.onError(r, "pop error")
    except Exception, e:
      self.onError(r, "pop error: %s" % e)
    return False

  def push(self, data):
    params = {REQ_KEY_ID:self.trackingId, REQ_KEY_TIMESTAMP:self.currentTimeMillis()}
    params.update(REQ_PARAMS_PUSH)
    r = None
    try:
      r = self.post(self.url, data=data, params=params, headers=REQ_HEADERS_PUSH)
      r.content # flush request
      ok = r.status_code == 200
      if ok:
        self.onMessagePublished(r, data)
        return True
      self.onError(r, "push error")
    except Exception, e:
      self.onError(r, "push error: %s" % e)
    return False

if __name__ == '__main__':

  def onMessage(res, msg):
    print "msg:", msg

  def onError(res, msg):
    print "error:", msg

  #from Queue import Queue
  #q = Queue()

  import sys
  url = sys.argv[-1]
  if not url or not url.startswith('http://'):
    #url = 'http://localhost:8080/meteor/topic'
    #url = 'http://localhost:8080/push/topic'
    #url = 'http://localhost:8080/push/vnr/topic/term'
    #url = 'http://sakuradite.com/push/vnr/topic/term'
    url = 'http://sakuradite.com/push/vnr/global'

  conn = CometConnection(url)
  conn.onError = onError
  conn.onMessage = onMessage

  print "url:", url
  ok = conn.connect()
  print "connect:", ok
  if ok:
    ok = conn.push("revive")
    print "push:", ok
    ok = conn.pop()
    print "pop:", ok
    #conn.trackingId = '0a92930c-9998-4859-8640-05fc5631b450'
    ok = conn.disconnect()
    print "disconnect:", ok

  #q.get()

# EOF

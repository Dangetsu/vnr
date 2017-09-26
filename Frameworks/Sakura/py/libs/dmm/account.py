# coding: utf8
# 10/23/2014 jichi
# See: https://github.com/solupro/kancolle/
#
# See: https://www.dmm.com/my/-/login/=/path=Sg__/
#   $.ajax({
#       url: 'https://www.dmm.com/my/-/login/ajax-get-token/',
#       beforeSend: function( xhr ) {
#           xhr.setRequestHeader("DMM_TOKEN", "cacf69c440a98ba37354f813b9cc07b2");
#       },
#       type: "POST",
#       async: false,
#       data: {
#           "token": "357fc1eb2807a60860092c93a3523958"
#       },
#       dataType: "json",
#       success: function (data) {
#           token = data.token;
#           idKey = data.login_id;
#           pwKey = data.password;
#       },
#       error: function(res) {
#           alert("通信エラーが発生しました");
#           return false;
#       }
#   });
if __name__ == '__main__':
  import sys
  sys.path.append('..')

import json, re
import requests
from sakurakit import sknetio
from sakurakit.skdebug import dwarn

class Config:
  def __init__(self):
    self.login_url = 'https://www.dmm.com/my/-/login/'
    self.token_url = 'https://www.dmm.com/my/-/login/ajax-get-token/'
    self.post_url = 'https://www.dmm.com/my/-/login/auth/'
    self.game_url = 'http://www.dmm.com/netgame/social/-/gadgets/=/app_id=854854/'
    #self.game_url = 'http://www.dmm.com/netgame/social/application/-/detail/=/app_id=854854/notification=on/myapp=on/act=install/'
    self.headers = {
      'User-Agent' : "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:26.0) Gecko/20100101 Firefox/26.0",
      #'Host' : "www.dmm.com", # not needed, though
      #'Referer': "https://www.dmm.com/my/-/login/", # not needed, though
      #'X-Forwarded-For': IPADDR,
    }

class Helper(object):
  def __init__(self, session=None, config=None):
    self.session = session or requests.Session()
    self.config = config or Config()

  def get_token(self):
    token = {}
    try:
      r = self.session.get(self.config.login_url, headers=self.config.headers)
      html = r.content
      if html:
        m = re.search('"DMM_TOKEN",\W+"([\d|\w]+)"', html)
        dmm_token = m.group(1)
        m = re.search('"token":\W+"([\d|\w]+)"', html)
        req_token = m.group(1)

        hs = dict(r.headers)
        hs['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
        hs['X-Requested-With'] = 'XMLHttpRequest'
        hs['DMM_TOKEN'] = dmm_token
        data = {
          'token' : req_token,
        }

        r = self.session.post(self.config.token_url, data=data, headers=hs)
        token = r.json()
    except Exception, e:
      dwarn(e)
    return token

  def login(self, account, password, token):
    """
    @param  account  str
    @param  password  str
    @param  token  dict
    @return bool
    """
    try:
      data = {
        token['login_id'] : account,
        token['password'] : password,
        'login_id' : account,
        'password' : password,
        'token' : token['token'],
        'path' : '', # Sg__
        'save_login_id': 1,
        'save_password': 1,
        'use_auto_login':	1,
      }
      r = self.session.post(self.config.post_url, data=data)
      #print r.text
      return True
    except Exception, e:
      dwarn(e)
      return False

  def get_play_url(self):
    play_url = ''
    try:
      r = self.session.get(self.config.game_url)
      html = r.content
      m = re.search('<img src="([^"]*)" width="1" height="1" />', html)
      if not m:
        dwarn("failed to login")
        return None
      if html:
        m = re.search('URL\W+:\W+"(.*)",', html)
        if m:
          play_url = m.group(1)
    except Exception, e:
      dwarn(e)
    return play_url

if __name__ == '__main__':
  print sys.argv
  name = sys.argv[1]
  passwd = sys.argv[2]
  print name, passwd

  h = Helper()

  token = h.get_token()
  print token
  print h.login(name, passwd, token)
  print h.get_play_url()

# EOF

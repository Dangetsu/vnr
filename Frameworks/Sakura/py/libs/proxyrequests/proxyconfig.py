# coding: utf8
# proxyconfig.py
# 1/2/2015 jichi
# See: http://www.pxaa.com
# See: https://twitter.com/bypassproxy

JPWEBPROXY_CONFIG = { # faster, but jittered
  'host': 'http://4freeproxy.com/includes/process.php?action=update',
  'referer': 'http://4freeproxy.com',
  'postkey': 'u',
  'region': 'ja',
}

USWEBPROXY_CONFIG = JPWEBPROXY_CONFIG;

#JPWEBPROXY_CONFIG = { # faster, but jittered
#  'host': 'http://netherlandsproxy.pw',
#  'referer': 'http://netherlandsproxy.pw',
#  'postkey': 'x',
#  'region': 'ja',
#}

#USWEBPROXY_CONFIG = { # faster, but jittered
#  'host': 'http://japanwebproxy.com', # cannot access erogamescape
#  'referer': 'http://japanwebproxy.com',
#  'postkey': 'x',
#  'region': 'ja',
#}

# Currently not supported yet
#USWEBPROXY_CONFIG = {
#  #'host': 'http://www.unblock-proxy.us',
#  #'referer': 'http://www.unblock-proxy.us',
#  'host': 'http://www.uswebproxy.com',
#  'referer': 'http://www.uswebproxy.com',
#  'postkey': 'x',
#  'region': 'en',
#}

# EOF
